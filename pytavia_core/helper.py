import os
import sys
import copy
import json
import base64
import copy

from flask import make_response

sys.path.append("pytavia_core"    )
sys.path.append("pytavia_modules" )
sys.path.append("pytavia_settings")
sys.path.append("pytavia_stdlib"  )
sys.path.append("pytavia_storage" )

from pytavia_stdlib import idgen

class response_msg:

    mapping_data = {
        "status" : "message_action",
        "desc"   : "message_desc",
        "data"   : "message_data",
    }

    def __init__(self, status, desc, data):
        call_id       = idgen._get_api_call_id()
        self.response = {
            "id"             : call_id ,
            "status"         : status  ,
            "desc"           : desc    ,
            "data"           : data    ,
            "message_id"     : call_id ,
            "message_action" : status  ,
            "message_desc"   : desc    ,
            "message_data"   : data
        }
    # end def

    def put(self, key, value):
        if not (key in self.response):
            raise ValueError('SETTING_NON_EXISTING_FIELD', key, value)
        # end if
        self.response[key] = value
        self.response[self.mapping_data[key]] = value
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

    def json_v1(self):
        record_prev = copy.deepcopy( self.response )
        del record_prev["status"]
        del record_prev["id"]
        del record_prev["desc"]
        del record_prev["data"]
        return record_prev
    # end def

    def stringify(self, app=None):
        record_prev = copy.deepcopy( self.response )
        if app != None:
            app.logger.debug( record_prev["message_data"] )
        # end if
        del record_prev["message_action"]
        del record_prev["message_id"]
        del record_prev["message_desc"]
        del record_prev["message_data"]
        return json.dumps( record_prev )
    # end def

    def http_stringify(self, app=None):
        record_prev = self.stringify(app)
        response    = make_response(
            record_prev, 
            200
        )
        response.mimetype = "application/json"
        return response
    # end def

    def stringify_v1(self):
        record_prev = copy.deepcopy( self.response )
        del record_prev["status"]
        del record_prev["id"]
        del record_prev["desc"]
        del record_prev["data"]
        return json.dumps( record_prev )
    # end def

# end class
