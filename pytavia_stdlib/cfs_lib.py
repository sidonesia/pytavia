import datetime
import time
import random
import hashlib
import datetime
import os
import sys
import base64
import requests 
import json
import io


from pytavia_core import config
from pytavia_core import database
from flask import Flask
from flask import redirect
from flask import make_response

app            = Flask( __name__, config.G_STATIC_URL_PATH )
app.secret_key = config.G_FLASK_SECRET

wmsDB = database.get_db_conn( config.mainDB )

def store_file_to_cfs(params):
    response = {
        "message_id"     : "" ,
        "message_action" : "ADD_CSF_FILE_FAILED",
        "message_code"   : "0",
        "message_desc"   : "" ,
        "message_data"   : {} ,
    }
    bucket      = params["bucket"    ]
    label       = params["label"     ]
    file_data   = params["file_data" ]
    extension   = params["extension" ]
    allow_type  = params["allow_type"]
    file_name   = params["file_name" ]

    #app.logger.debug("-------------------file_data.read-------------------")
    #app.logger.debug( file_data.read() )
    #app.logger.debug("-------------------file_data.read-------------------")

    cfs_files   = dict(stream=file_data)

    app.logger.debug("-------------------cfs_files-------------------")
    app.logger.debug( cfs_files )
    app.logger.debug("-------------------cfs_files-------------------")

    cfs_headers = {
        "key"          : file_name     ,
        "bucket"       : bucket        ,
        "label"        : label         ,
        "extension"    : extension     ,
        "conType"      : allow_type[0] ,
    }
    response_put_file = requests.post(
        config.G_BASE_S3_LOCAL + "/v1/cfs/put",
        files   = cfs_files,
        headers = cfs_headers
    )        
    json_put_file = response_put_file.json()     
    app.logger.debug("--------------------------------------")
    app.logger.debug( json_put_file )
    app.logger.debug("--------------------------------------")
    if json_put_file["message_action"] != "ADD_CFS_FILE_SUCCES" :
        response = json_put_file
        response["message_desc"] = "Add file failed in send file to cfs process"
        return response
    response["message_data"   ] = json_put_file["message_data"   ]
    response["message_id"     ] = json_put_file["message_id"     ]
    response["message_action" ] = json_put_file["message_action" ]
    return response
# end def
