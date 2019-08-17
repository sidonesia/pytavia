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

class event_loop_proc:

    def __init__(self):
        pass
    # end def

    def execute(self, params):
        print ( "event_loop_proc(): " )
        print ( params )
    # end def
# end class
