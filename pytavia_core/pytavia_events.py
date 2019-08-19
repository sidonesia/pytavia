import json
import time
import pymongo
import sys
import urllib.parse
import base64
import threading
import traceback

import database
import config
import msg_event

class event_proc(threading.Thread):

    mgdDB          = database.get_db_conn(config.mainDB)
    dispatchDB     = database.get_db_conn(config.pytavia_dispatchDB)

    g_collection   = None
    g_handler      = None
    g_handler_name = None
    g_query        = None
    g_event_loop   = True

    def __init__(self, handler_name, collection, handler, query):
        threading.Thread.__init__(self)

        self.g_handler_name = handler_name
        self.g_collection   = collection
        self.g_handler      = handler
        self.g_query        = query
    # end def

    def get_resume_token( self , params ):
        handler_name       = params["handler_name"   ]
        collection_name    = params["collection_name"]
        resume_history_rec = self.dispatchDB.db_sys_resume_history.find_one({
            "collection"   : collection_name,
            "handler_name" : handler_name
        })
        if resume_history_rec != None:
            resume_token = resume_history_rec["resume_token"]
            return resume_token
        # end if
        return None 
    # end def

    def save_resume_token( self, params ):
        event           = params["event"]
        handler_name    = params["handler_name"]

        resume_token    = event["_id"]        
        operation_type  = event["operationType"]        
        database_name   = event["ns"]["db"]        
        collection_name = event["ns"]["coll"]        
        document_key    = event["documentKey"]["_id"]        
        mgd_timestamp   = event["clusterTime"]        

        now_time        = int(time.time() * 1000)

        resume_history_rec = self.dispatchDB.db_sys_resume_history.find_one({
            "collection"   : collection_name,
            "handler_name" : handler_name
        })
        if resume_history_rec != None:
            self.dispatchDB.db_sys_resume_history.update(
                {"collection" : collection_name, "handler_name" : handler_name},
                {"$set"       : {
                    "resume_token"   : resume_token,
                    "operation_type" : operation_type,
                    "document_key"   : document_key,
                    "cluster_time"   : mgd_timestamp,
                    "rec_timestamp"  : now_time
                }}
            )
        else:
            sys_resume_history = database.new( self.dispatchDB , "db_sys_resume_history" )
            sys_resume_history.put( "resume_token"   , resume_token) 
            sys_resume_history.put( "operation_type" , operation_type) 
            sys_resume_history.put( "document_key"   , document_key) 
            sys_resume_history.put( "cluster_time"   , mgd_timestamp) 
            sys_resume_history.put( "handler_name"   , handler_name) 
            sys_resume_history.put( "collection"     , collection_name) 
            sys_resume_history.insert()
        # end if
    # end def

    def shutdown(self, params):
        self.g_event_loop = params["event_loop_status"]
    # end def

    def extract_event(self, event):
        operation_type = event["operationType"]
        if operation_type == "delete":
            clusterTime   = event["clusterTime"]
            collection    = event["ns"]["coll"]
            db            = event["ns"]["db"]
            object_id     = event["documentKey"]["_id"]
            handler_name  = event["handler_name"]
            m_event       = msg_event.msg_event(
                object_id,
                operation_type.upper(),
                handler_name,
                collection,
                db,
                clusterTime,
                operation_type.upper() + "_" + collection.upper(),
                {}
            )
            return m_event
        elif operation_type == "insert":
            clusterTime   = event["clusterTime"]
            collection    = event["ns"]["coll"]
            db            = event["ns"]["db"]
            object_id     = event["documentKey"]["_id"]
            handler_name  = event["handler_name"]
            event["fullDocument"]["_id"] = str( event["fullDocument"]["_id"] )
            full_document = event["fullDocument"]
            m_event       = msg_event.msg_event(
                object_id,
                operation_type.upper(),
                handler_name,
                collection,
                db,
                clusterTime,
                operation_type.upper() + "_" + collection.upper(),
                full_document
            )
            return m_event
        else :
            # this is for update
            clusterTime   = event["clusterTime"]
            collection    = event["ns"]["coll"]
            db            = event["ns"]["db"]
            object_id     = event["documentKey"]["_id"]
            handler_name  = event["handler_name"]
            changed_field = event["updateDescription"]
            m_event       = msg_event.msg_event(
                object_id,
                operation_type.upper(),
                handler_name,
                collection,
                db,
                clusterTime,
                operation_type.upper() + "_" + collection.upper(),
                changed_field
            )
            return m_event
        # end if
    # end if

    def run(self):
        try:
            print ("handler_listener - register() handler_name: " + str(self.g_handler_name))
            while self.g_event_loop:
                
                resume_token = self.get_resume_token({
                    "handler_name"    : self.g_handler_name,
                    "collection_name" : self.g_collection
                })
                msg_event = self.mgdDB[self.g_collection].watch(
                    resume_after = resume_token,
                    pipeline     = self.g_query
                )
                doc_event = next( msg_event )
                doc_event["handler_name"] = self.g_handler_name
                self.save_resume_token({
                    "event"        : doc_event,
                    "handler_name" : self.g_handler_name
                })
                event_msg = self.extract_event( doc_event )
                self.g_handler.event_switch( event_msg )
            # end while
        except:
            print ( traceback.format_exc() )
        # end try
    # end def 
# end class

class pytavia_events:

    running_handlers      = {}
    handler_register_list = {}
    event_loop            = True

    def __init__(self, params):
        pass
    # end def

    def shutdown(self, params):
        self.event_loop = params["event_loop_status"]
    # end def

    def register_handler(self, params):
        handler_name = params["handler_name"]
        collection   = params["collection"  ]
        handler      = params["handler"     ]
        query_filter = params["query_filter"]
        #
        # Add the registered handlers into the list
        #
        self.handler_register_list[handler_name] = {
            "handler_name" : handler_name,
            "collection"   : collection,
            "handler"      : handler,
            "query_filter" : query_filter
        }
    # end def

    def run_handler(self, params):
        handler_list = list(self.handler_register_list.values())
        for handler_check in handler_list:
            handler_name  = handler_check["handler_name"]
            collection    = handler_check["collection"]
            handler       = handler_check["handler"]
            query_filter  = handler_check["query_filter"]

            #
            # Ensure that we inhert from the event handler parent
            # and implements event_switch
            #
            event_switch        = getattr(handler, 'event_switch', None)
            event_handler_check = getattr(handler, 'event_handler_check', None)

            if not callable( event_switch ):
                return False
            # end if
            if not callable( event_handler_check ):
                return False
            # end if
        # end for
        for handler_action in handler_list:
            handler_name  = handler_action["handler_name"]
            collection    = handler_action["collection"]
            handler       = handler_action["handler"]
            query_filter  = handler_action["query_filter"]
            event_handler = event_proc( 
                handler_name, 
                collection,
                handler,
                query_filter
            )
            event_handler.start()
            self.running_handlers[handler_name] = event_handler
        # end for
        return True
    # end def

    def event_loop(self, params):
        event_loop_wait = params["event_loop_wait"]
        event_loop_exec = None
        if "event_loop_execute" in params:
            event_loop_exec = params["event_loop_execute"] 
        # end if
        print ( "-------------------------------------------" )
        print ( "STARTING PYTAVIA EVENT PROCESSOR ENGINE" )
        print ( "-------------------------------------------" )

        print ( "REGISTER HANDLER START ...")
        is_run_handler = self.run_handler( params )
        if not is_run_handler:
            print ( "[ERROR] - HANDLER MUST implement event_switch() & inherit from pytavia_event_handler ..." )
            print ( "[ERROR] - HANDLER pytavia_event_handler found in pytavia_core ( please implement )" )
            print ( "[ERROR] - exiting now ...")
            sys.exit( 1 ) 
        # end if

        print ( "START EVENT LOOP LISTENING FOR EVENTS STARTED ...")
        print ( "" )
        while self.event_loop:
            if event_loop_exec != None:
                event_loop_exec.execute( params )
            # end if
            time.sleep( event_loop_wait )
        # end while
    # end def
# end class
