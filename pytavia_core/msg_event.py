import os
import sys
import copy
import json
import base64
import copy

sys.path.append("pytavia_core"    )
sys.path.append("pytavia_modules" )
sys.path.append("pytavia_settings")
sys.path.append("pytavia_stdlib"  )
sys.path.append("pytavia_storage" )

from pytavia_stdlib import idgen

class msg_event:

    def __init__(self, rid, action, handler_name, collection, db, time_action, desc , data ):
        call_id       = idgen._get_api_call_id()
        self.response = {
            "id"             : call_id      ,
            "handler_name"   : handler_name ,
            "rid"            : rid          ,
            "collection"     : collection   ,
            "db"             : db           ,
            "time"           : time_action  ,
            "action"         : action       ,
            "desc"           : desc         ,
            "data"           : data         ,
        }
    # end def

    def put(self, key, value):
        if not (key in self.response):
            raise ValueError('SETTING_NON_EXISTING_FIELD', key, value)
        # end if
        self.response[key] = value
    #end def

    def get(self, key):
        if not (key in self.response):
            raise ValueError('SETTING_NON_EXISTING_FIELD', key, value)
        # end if
        return self.response[key]
    # end def

    def json(self):
        return self.response
    # end def

    def stringify(self):
        self.response["rid"] = str( self.response["rid"] )
        return json.dumps( self.response )
    # end def

# end class
