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

from pytavia_core import helper
from pytavia_core import database
from pytavia_core import config

class dukcapil:

    def __init__(self):
        pass

    def process(self, params):
        response = helper.response_msg(
            "DUKCAPIL_GET_DATA_SUCCESS",
            "DUKCAPIL GET DATA SUCCESS",
            {}
        )
        try:
           pass 
        except:
            print( traceback.format_exc() )
        # end 
        return response
    # end def
# end class
