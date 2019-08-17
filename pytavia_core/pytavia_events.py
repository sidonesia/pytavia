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

class event_proc(threading.Thread):

    mgdDB          = database.get_db_conn(config.mainDB)
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

    def run(self):
        try:
            while self.g_event_loop:
                print ("event_loop - execute() handler: " + str(self.g_handler_name))
                msg_event = self.mgdDB[self.g_collection].watch(
                    pipeline=self.g_query
                )
                doc_event = next( msg_event )
                #
                # We should reformat the object here so it has a common format
                #
                print ( doc_event )
                self.g_handler.event_switch( doc_event )
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
    # end def

    def event_loop(self, params):
        event_loop_wait = params["event_loop_wait"]
        event_loop_exec = None
        if "event_loop_execute" in params:
            event_loop_exec = params["event_loop_execute"] 
        # end if
        self.run_handler( params )
        while self.event_loop:
            if event_loop_exec != None:
                event_loop_exec.execute( params )
            # end if
            time.sleep( event_loop_wait )
        # end while
    # end def
# end class
