import json
import time
import pymongo
import sys
import urllib.parse
import base64

sys.path.append("pytavia_core"    )
sys.path.append("pytavia_settings")
sys.path.append("pytavia_stdlib"  )
sys.path.append("pytavia_storage" )
sys.path.append("pytavia_modules" )
sys.path.append("pytavia_modules/event_loop_executor" )
sys.path.append("pytavia_modules/event_handler" )

from pytavia_stdlib      import utils
from pytavia_core        import database
from pytavia_core        import config
from pytavia_core        import pytavia_events
from pytavia_stdlib      import idgen

from event_handler       import customer_evt_handler
from event_loop_executor import event_loop_proc


class server_event_handler(pytavia_events.pytavia_events):

    def __init__(self, params):
        pytavia_events.pytavia_events.__init__( self, params )
        self.register_handlers(params)
   # end def

    def register_handlers(self, params):
        self.register_handler({
            "handler_name" : "INSERT_DB_QUEUE_WORKFLOW_PROCESS",
            "collection"   : "db_queue_workflow_process",
            "handler"      : customer_evt_handler.customer_evt_handler({}),
            "query_filter" : []
        })
    # end def

    def start(self, params):
        self.event_loop({
            "event_loop_wait"    : 60,
            "event_loop_execute" : event_loop_proc.event_loop_proc({})
        })
    # end 

# end class

seh = server_event_handler({})
seh.start({})


