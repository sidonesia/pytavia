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

    def process_customer_check(self, event):
        print ("do some action here")
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

