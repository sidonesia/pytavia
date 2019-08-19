import json
import time
import pymongo
import sys
import urllib.parse
import base64
import traceback

sys.path.append("pytavia_core"    )
sys.path.append("pytavia_settings")
sys.path.append("pytavia_stdlib"  )
sys.path.append("pytavia_storage" )
sys.path.append("pytavia_modules" )

from pytavia_core import pytavia_event_handler
from pytavia_core import database
from pytavia_core import config
from pytavia_core import bulk_db_multi

import dukcapil
import slik

class customer_evt_handler(pytavia_event_handler.pytavia_event_handler):

    mgdDB = database.get_db_conn( config.mainDB )

    def __init__(self, params):
        pytavia_event_handler.pytavia_event_handler.__init__(self,params)
    # end def

    def process_dukcapil(self, params):
        app_user_rec        = params["app_user_rec"]
        fk_workflow_item_id = params["fk_workflow_item_id"]

        nik_ktp_identity    = app_user_rec["nik"]
        dukcapil_resp       = dukcapil.dukcapil().process({
            "nik" : nik_ktp_identity
        })
        msg_status = dukcapil_resp.get("status")
        msg_desc   = dukcapil_resp.get("desc"  )
        if msg_status != "DUKCAPIL_GET_DATA_SUCCESS":
            print ("[process_dukcapil] - FAILED " + msg_desc) 
            return
        # end if
        now_time        = int(time.time() * 1000)
        fk_user_id      = app_user_rec["fk_user_id"]
        fk_app_id       = app_user_rec["fk_app_id"]
        fk_app_user_id  = app_user_rec["pkey"]
        
        mdl_app_sys_log = database.new( self.mgdDB , "db_application_sys_log" ) 
        mdl_app_sys_log.put( "fk_app_id"        , fk_app_id         )
        mdl_app_sys_log.put( "fk_user_id"       , fk_user_id        )
        mdl_app_sys_log.put( "fk_app_user_id"   , fk_app_user_id    )
        mdl_app_sys_log.put( "status_timestamp" , now_time          )
        mdl_app_sys_log.put( "status"           , "DUKCAPIL_SUCCESS")
        mdl_app_sys_log.put( "updated_by"       , "SLIK"            )

        db_handle  = database.get_database( config.mainDB )
        bulk_multi = bulk_db_multi.bulk_db_multi({
            "db_handle" : db_handle,
            "app"       : None
        })
        bulk_multi.add_action(
            bulk_db_multi.ACTION_UPDATE ,
            "db_queue_workflow_process_item",
            {   "pkey"  : fk_workflow_item_id },
            {   "$set"  : {
                "is_done"        : "TRUE",
                "completed_time" : now_time
            }}
        )
        bulk_multi.add_action(
            bulk_db_multi.ACTION_INSERT ,
            mdl_app_sys_log
        )
        bulk_multi.execute({})
    # end def

    def process_slik(self, params):
        print ("[process_slik] - ")
        print ( params )
    # end def

    def process_customer_check(self, event):

        print ( event.json() )

        record_id = event.get("rid")
        process_item_rec = self.mgdDB.db_queue_workflow_process.find_one({
            "_id"  : record_id
        })
        fk_process_workflow_id = process_item_rec["pkey"]
        fk_app_user_id         = process_item_rec["fk_app_user_id"]
        workflow_process_task_view = self.mgdDB.db_queue_workflow_process_item.find({
            "fk_process_workflow_id" : fk_process_workflow_id,
            "is_done"                : "FALSE"
        })
        for workflow_process_task_rec in workflow_process_task_view:
            fk_workflow_item_id = workflow_process_task_rec["pkey"]
            workflow_task_name  = workflow_process_task_rec["task_name"]
            app_user_rec        = self.mgdDB.db_application_user.find_one({
                "pkey" : fk_app_user_id
            })
            if workflow_task_name == "SLIK":
                self.process_slik({
                    "app_user_rec"         : app_user_rec,
                    "fk_workflow_item_id"  : fk_workflow_item_id
                }) 
            elif workflow_task_name == "DUKCAPIL":
                self.process_dukcapil({
                    "app_user_rec"         : app_user_rec,
                    "fk_workflow_item_id"  : fk_workflow_item_id
                }) 
            # end if
        # end for
        """
            Count the done workflow items vs the total number of workflow items.
                if the numbers match means all the tasks are completed and we can 
                update the workflow to be ready for scoring
        """
        completed_task_count = self.mgdDB.db_queue_workflow_process_item.find({
            "fk_process_workflow_id" : fk_process_workflow_id,
            "is_done"                : "TRUE"
        })
        all_task_count = self.mgdDB.db_queue_workflow_process_item.find({
            "fk_process_workflow_id" : fk_process_workflow_id,
        })
        if completed_task_count == all_task_count:
            self.mgdDB.db_queue_workflow_process.update(
                { "pkey" : fk_process_workflow_id },
                { "$set" : { "workflow_status" : "SCORING_READY"}}
            )
        # end if
    # end def

    def event_switch(self, event):
        pytavia_event_handler.pytavia_event_handler.event_switch( self, event)
        try:
            event_action = event.get("action")
            if event_action == "INSERT":
                self.process_customer_check( event )
                sys.stdout.flush()
            # end if     
        except:
            print( traceback.format_exc() )
        # end try
    # end def
# end class

