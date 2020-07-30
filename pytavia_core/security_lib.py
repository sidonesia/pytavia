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
from pytavia_core   import helper
from pytavia_core   import config


class security_lib:

    def __init__(self, app):
        self.webapp      = app
        self.ignore_flag = config.G_IGNORE_SECURITY
    # end def

    def sequance(self, params):
        sequance = ""
        for key, value in sorted(params.items()):
            if type( value ) == str:
                sequance = sequance + value
                self.webapp.logger.debug( key + " " + value )
            # end if
        # end for
        return sequance
    # end def

    def verify(self, params):
        response = helper.response_msg(
            "VERIFY_TOKEN_SUCCESS",
            "VERIFY TOKEN SUCCESS", {},
            "0000"
        )
        headers         = params["headers"]
        client_params   = params["params" ]
        #
        # This is where we ignore the test if we actually want to bypass
        # authentication
        #
        if self.ignore_flag:
            return response
        # end if
        #
        acc_label  = headers["Access-Label"]
        request_id = headers["Request-Id"  ]
        unique_id  = headers["Unique-Id"   ]
        mim_token  = headers["Mim-token"   ]
        try:
            access_key_rec = self.mgdDB.db_access_key.find_one({
                    "fk_unique_id" : unique_id
            }, { "_id" : 0, "key" : 1, "secret" : 1, "fk_unique_id" : 1, "label" : 1})
            #
            # Make sure that this account for api access exists
            #
            if access_key_rec == None:
                response.put( "status"      , "VERIFY_TOKEN_FAILED")
                response.put( "desc"        , "VERIFY TOKEN FAILED")
                response.put( "status_code" , "0001")
                response.put( "data"        , {})
                return response
            # end if
            key             = access_key_rec["key"       ]
            secret          = access_key_rec["secret"    ]
            gen_secret      = access_key_rec["gen_secret"]
            raw_gen_secret  = key + secret
            #
            # here we confirm that the unique id and the key are matched
            # and has been signed by the correct secret so this will match
            # the key with the unique_id that is sent
            #
            gen_secret  = hashlib.sha256(raw_gen_secret.encode('ascii')).hexdigest()
            if unique_id != gen_secret:
                response.put( "status"      , "VERIFY_TOKEN_FAILED")
                response.put( "desc"        , "VERIFY TOKEN FAILED")
                response.put( "status_code" , "0002")
                response.put( "data"        , {})
                return response
            # end if
            #
            # Start processing the token here
            #
            sequance    = self.sequance( client_params )
            temp_token  = acc_label  + "%|%" +\
                          request_id + "%|%" +\
                          key        + "%|%" +\
                          secret     + "%|%" +\
                          unique_id  + "%|%" + str(sequence)
            auth_token  = hashlib.sha256(temp_token.encode('ascii')).hexdigest()

            if mim_token != auth_token:
                response.put( "status"      , "VERIFY_TOKEN_FAILED")
                response.put( "desc"        , "VERIFY TOKEN FAILED")
                response.put( "status_code" , "0003")
                response.put( "data"        , {})
                return response
            # end if
            #
            response.put( "data" , {})
        except:
            self.webapp.logger.debug(traceback.format_exc())
            response.put( "status"      ,  "VERIFY_TOKEN_FAILED" )
            response.put( "desc"        ,  "GENERAL ERROR" )
            response.put( "status_code" ,  "9999" )
        # end try
        return response
    # end def

# end class
