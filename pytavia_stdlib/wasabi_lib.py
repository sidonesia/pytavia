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
import boto3

import urllib
sys.path.append("pytavia_modules/security" )

from pytavia_core import config
from pytavia_core import database
from flask import Flask
from flask import redirect
from flask import make_response

app            = Flask( __name__, config.G_STATIC_URL_PATH )
app.secret_key = config.G_FLASK_SECRET
wmsDB          = database.get_db_conn( config.mainDB )

def store_file(params):
    response = {
        "message_id"     : "" ,
        "message_action" : "ADD_WASABI_FILE_SUCCESS",
        "message_code"   : "1",
        "message_desc"   : "" ,
        "message_data"   : {} ,
    }

    bucket       = params["bucket"    ]
    file_data    = params["file_data" ]
    file_name    = params["file_name" ]
    s3           = boto3.client('s3', endpoint_url = config.G_WSB_URL, aws_access_key_id = config.WSB_ACCESS_ID, aws_secret_access_key = config.WSB_SECRET_KEY )
    pre_sign_url = s3.generate_presigned_url('put_object', Params={'Bucket':bucket,'Key':file_name}, ExpiresIn=3600, HttpMethod='PUT')

    resp         = requests.put(pre_sign_url, data=file_data)

    if resp .status_code != 200:
        response["message_action" ] = "ADD_WASABI_FILE_FAILED"
        response["message_code"   ] = "0"
        response["message_desc"   ] = resp.content
    #end if
    response["message_data"   ] = {"path":'key=/' + file_name + '&bucket=' + config.G_WSB_IMAGE_BUCKET + '&src=wsb' }
    return response
#enddef

def set_redirect_img(i):
    img_cat         = i.get('img').split('/')[1] if i and i['img'] else ''
    img_date        = i.get('img').split('/')[2] if i and i['img'] else ''
    img_file        = i.get('img').split('/')[3] if i and i['img'] else ''

    args            = urllib.parse.parse_qs(img_file)
    src             = args.get('src')[0] if 'src' in args else "cfs"

    return  '/assets/' + src + '/' + img_cat + '/' + img_date + "/" + img_file.split('&')[0] + ".jpg" if i and i['img'] else ""
#end def