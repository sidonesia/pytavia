import json
import time
import pymongo
import sys
import urllib.parse
import base64

sys.path.append("pytavia_core"  )
sys.path.append("pytavia_stdlib")

# adding comments
from pytavia_stdlib  import utils
from pytavia_core    import database
from pytavia_core    import config
from pytavia_stdlib  import idgen

class module1:

    def __init__(self, app):
        self.webapp = app
    # end def

    def process(self, params):
        response = helper.response_msg(
            "PROCESS_SUCCESS", "PROCESS SUCCESS", {}
        )
        try:
            pass
        except:
            self.webapp.logger.debug( "exception occured ..." )
        # end try
        return response
    # end def
# end class
