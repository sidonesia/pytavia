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

from pytavia_core import pytavia_event_handler

class init_event_handler(pytavia_event_handler.pytavia_event_handler):

    def __init__(self, params):
        pytavia_event_handler.pytavia_event_handler.__init__(self,params)
    # end def

    """
        This is where we write the code to handle
            the event that comes in when the database is
            updated
    """
    def event_switch(self, event):
        pytavia_event_handler.pytavia_event_handler.event_switch( self, event)
    # end def

# end class
