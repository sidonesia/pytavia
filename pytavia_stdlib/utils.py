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

sys.path.append("pytavia_modules/security" )

from security     import security_proc
from pytavia_core import config
from pytavia_core import database
from flask import Flask
from flask import redirect
from flask import make_response

app            = Flask( __name__, config.G_STATIC_URL_PATH )
app.secret_key = config.G_FLASK_SECRET

wmsDB = database.get_db_conn( config.mainDB )

def _gen_color(params):
    n          = params["num_colors"]
    core_color = params["core_color"]
    ret = []
    step = 256 / n
    dont_repeat_dict = {}
    for i in range(n):
        while True:
            r   = random.randint(17, core_color)
            g   = random.randint(17, core_color)
            b   = core_color
            key = str(r) + "-" + str(g) + "-" + str(b) 
            if not key in dont_repeat_dict:
                ret.append( '#%02X%02X%02X' % (r,g,b)) 
                dont_repeat_dict[key] = key
                break
            # end if
        # end while
    return ret
# end def

"""
    Later when we do security we check the file type
    for uploads here in allow_type then use the proper engine 
    to check
"""
def _store_uploaded_files(params):
    ext          = params["ext"       ]
    folder       = params["folder"    ]
    allow_type   = params["allow_type"]
    file_data    = params["file_data" ]
    current_time = int(time.time() * 1000)
    random_int   = random.randint(1000000,9999999)
    if ext == "DEFAULT":
        ext = os.path.splitext(file_data.filename)[1].replace(".","")
    # end if
    file_name    = "file_" + str( current_time ) + "_" + str(random_int) + "." + ext
    save_file    = config.G_UPLOAD_PATH + params["folder"]   + "/" + file_name
   # url_location = config.G_BASE_URL    + config.G_UPLOAD_URL_PATH + params["folder"] + "/" + file_name
    url_location =  config.G_UPLOAD_URL_PATH + params["folder"] + "/" + file_name
    file_data.seek(0,2)
    file_size    = file_data.tell()
    response     = {
        "save_file_location" : save_file    ,
        "url_file_location"  : url_location ,
        "file_name"          : file_name    ,
        "file_size"          : file_size
    }
    file_data.seek(0,0)
    file_data.save( save_file ) 
    return response
# end def

def _get_pin_hash(params):
    wallet_id         = params["wallet_id"]
    pin               = params["pin"      ]
    length_wallet_id  = len( wallet_id )
    wallet_id_suffix  = wallet_id[
        length_wallet_id - config.G_WALLET_ID_SUFFIX : length_wallet_id
    ]
    pin_md5  = hashlib.md5()
    pin_md5.update(pin + wallet_id_suffix)
    pin_hash = pin_md5.hexdigest()
    return pin_hash
# end def

def _cmp_pin(params):
    pin_new   = params["pin"]
    wallet_id = params["wallet_id"]
    wallet_auth_rec   = wmsDB.db_wallet_auth.find_one({
        "fk_wallet_id" : wallet_id
    })
    pin_hash = wallet_auth_rec["pin"]
    if pin_new == pin_hash:
        return True
    else:
        return False
    # end if
# end def

def _get_passwd_hash(params):
    wallet_id         = params["id"]
    passwd            = params["password" ]
    length_wallet_id  = len( wallet_id )
    wallet_id_suffix  = wallet_id[
        length_wallet_id - config.G_WALLET_ID_SUFFIX : length_wallet_id
    ]
    password_md5      = hashlib.md5()
    password_md5.update((passwd + wallet_id_suffix).encode('utf-8'))
    password_hash     = password_md5.hexdigest()
    return password_hash
# end def

import datetime

def _get_last_day_of_the_month(params):
    y = params["year" ]
    m = params["month"]
    m += 1
    if m == 13:
        m = 1
        y += 1
    #end if
    first_of_next_month = datetime.date(y, m, 1)
    last_of_this_month = first_of_next_month + datetime.timedelta(-1)
    return last_of_this_month.day
# end def

def _cmp_su_password(params):
    username = params["username"]
    password = params["password"]
    wallet_auth_rec   = wmsDB.db_super_user.find_one({
        "username" : username
    })
    password_hash = wallet_auth_rec["password"]
    if password == password_hash:
        return True
    else:
        return False
    # end if
# end def

def generate_default_password(params):   
    response = {
            "message_id"     : 1,
            "message_action" : "GENERATE_PASSWORD_SUCCESS",
            "message_code"   : "0",
            "message_desc"   : "",
            "message_data"   : {}
    }
    password      = ""
    possible      = ""
    try : 
        setting_list    = wmsDB.db_setting_app.find_one({})
        set_pass_length = setting_list["password_length"  ]
        set_var_pass    = setting_list["variable_password"]
        use_numeric     = set_var_pass["numeric"          ]
        use_low_case    = set_var_pass["lower_case"       ]
        use_up_case     = set_var_pass["upper_case"       ]
        use_symbol      = set_var_pass["symbol"           ]    
        symbol          = set_var_pass["symbol_str"       ]

        alphabet_low    = "abcdefghijklmnopqrstuvwxyz"
        alphabet_high   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numeric         = "1234567890"

        possible += alphabet_low  if use_low_case != "FALSE" else possible
        possible += alphabet_high if use_up_case  != "FALSE" else possible
        possible += numeric       if use_numeric  != "FALSE" else possible
        possible += symbol        if use_symbol   != "FALSE" else possible

        possible     = possible if possible != "" else "abcdefghijklmnopqrstuvwxyz0123456789"
        possible     = "0123"
        possible_len = len( possible )
        for idx in range( 0,int(set_pass_length)):           
            char_pos = random.randint( 0, int(possible_len - 1) )
            char     = possible[int(char_pos)]
            password = password + char
        # end for
        response["message_data"] = {"password" : password } 
    except:
        response["message_action"   ] = "GENERATE_PASSWORD_FAILED"
        response["message_action"   ] = "GENERATE_PASSWORD_FAILED: " + str(sys.exc_info()) 
    # end for
    return response
#end def 
 
def _store_file_to_s3_blipcom(params):
    response = {
        "message_id"            : "",
        "message_action"        : "ADD_CSF_FILE_FAILED",
        "message_code"          : "0",
        "message_desc"          : "",
        "message_data"          : {},
    }
    bucket          = params["bucket"       ]
    file_data       = params["file_data"    ]
    extension       = params["extension"    ]
    allow_type      = params["allow_type"   ]
    label           = params["label"        ]
    current_time    = int(time.time() * 1000)
    random_int      = random.randint(1000000,9999999)   
    conType         = None
    
    file_name    = "file_" + str( current_time ) + "_" + str(random_int)          
    if "file_name" in params:
        file_name = params["file_name"]
    # end if
    file_data.seek(0,2)
    file_size    = file_data.tell()
    file_data.seek(0,0)    
    if extension == "DEFAULT":
        extension = os.path.splitext(file_data.filename)[1].replace(".","")
    #end if     
    #get content type file from extension     
    conType = _get_mime_types(extension)
    
    security_params   = {
        "login_url": config.G_BASE_S3_URL + "/v1/cfs/security/login", 
        "key"      : config.G_CFS_KEY, 
        "secret"   : config.G_CFS_ACCESS,
        "label"    : config.G_CFS_REGION,
        "sequence" : None
    }
    response_security_login =  security_proc.security_proc(app).login(security_params)    
    security_login_action   = response_security_login["message_action"]
    security_login_data     = response_security_login["message_data"  ]
    security_user_token     = security_login_data["token"]   
    security_user_id        = security_login_data["fk_user_id"] 
    if security_login_action == "SECURITY_LOGIN_FAILED":
        response["message_desc"] = "Add file failed in security login process"
        return response
    #end if
    security_sequence = file_name + bucket + label + extension + conType + security_user_id 
    security_params["fk_user_id"] = security_user_id
    security_params["sequence"] = security_sequence
    security_token    =  security_proc.security_proc(app).request_security_token(security_params)
    if security_token == None:
        response["message_desc"] = "Add file failed in security get token process"
        return response      
    # send file 
    cfs_url = config.G_BASE_S3_URL + "/v1/cfs/put-file"
    cfs_headers  = {
        #"Content-Type"  : "multipart/form-data",
        "auth-token"    : security_token,
        "auth-label"    : config.G_CFS_REGION,
    }    
    cfs_data        = {
        "key"        : file_name ,
        "bucket"     : bucket    ,
        "extension"  : extension ,
        "conType"    : conType   ,
        "file_size"  : file_size ,
        "label"      : label     ,
        "fk_user_id" : security_user_id
    }
    #set file for requets
    cfs_files = [
            ('document', ('document', file_data)),
    ]    
    response_put_file =  requests.post(cfs_url,files=cfs_files,data=cfs_data,headers=cfs_headers)        
    json_put_file = response_put_file.json()     
    if json_put_file["message_action"] != "ADD_CFS_FILE_SUCCES" :
        response = json_put_file
        response["message_desc"] = "Add file failed in send file to cfs process"
        return response
    response["message_data"   ] = json_put_file["message_data"   ]
    response["message_id"     ] = json_put_file["message_id"     ]
    response["message_action" ] = json_put_file["message_action" ]   
    return response
#end def

def get_file_from_cfs(params):
    response = {
        "message_id"            : "",
        "message_action"        : "GET_CSF_FILE_FAILED",
        "message_code"          : "0",
        "message_desc"          : "",
        "message_data"          : {},
    }
    bucket = params["bucket" ]
    key    = params["key"    ]
    security_params   = {
        "login_url": config.G_BASE_S3_URL + "/v1/cfs/security/login", 
        "key"      : config.G_CFS_KEY, 
        "secret"   : config.G_CFS_ACCESS,
        "label"    : config.G_CFS_REGION,
        "sequence" : None
    }
    
    response_security_login =  security_proc.security_proc(app).login(security_params)    
    security_login_action   = response_security_login["message_action"]
    security_login_data     = response_security_login["message_data"  ]
    security_user_id        = security_login_data["fk_user_id" ] 
    security_user_token     = security_login_data["token"      ]   
    if security_login_action == "SECURITY_LOGIN_FAILED":
        response["message_desc"] = "Get file failed in security login process"
        return response
    #end if
    security_sequence = str(bucket) +  security_user_id  + str(key) 
    security_params["fk_user_id"] = security_user_id
    security_params["sequence"] = security_sequence
    security_token    =  security_proc.security_proc(app).request_security_token(security_params)
    if security_token == None:
        response["message_desc"] = "Get file failed in security get token process"
        return response    
        
    cfs_url = config.G_BASE_S3_URL + "/v1/cfs/get-file-res-json"
    cfs_headers  = {
        "auth-token"    : security_token,
        "auth-label"    : config.G_CFS_REGION,
    }
    cfs_data        = {
        "key"        : key,
        "bucket"     : bucket,
        "fk_user_id" : security_user_id  
    }
    new_response = None
    response_get_file =  requests.post(cfs_url,data=cfs_data,headers=cfs_headers)     
    
    json_get_file = response_get_file.json()    
    if json_get_file["message_action"] != "GET_CFS_FILE_SUCCES" :
        response["message_desc"] = "Add file failed in send file to cfs process"
        response = json_get_file
        return response
    #end if
    
    list_data    = json_get_file["message_data"]
    content_type = list_data["conType"]
    data_encode  = list_data["file_dencode"].encode()
    data         = base64.b64decode(data_encode)
    new_response = make_response(data)
    new_response.headers["Content-Type"] = content_type
    return new_response
    
#end def 

def _get_mime_types(extension):
    types = None 
    mime_types = dict(
        txt='text/plain',
        htm='text/html',
        html='text/html',
        php='text/html',
        css='text/css',
        js='application/javascript',
        json='application/json',
        xml='application/xml',
        swf='application/x-shockwave-flash',
        flv='video/x-flv',

        # images
        png='image/png',
        jpe='image/jpeg',
        jpeg='image/jpeg',
        jpg='image/jpeg',
        gif='image/gif',
        bmp='image/bmp',
        ico='image/vnd.microsoft.icon',
        tiff='image/tiff',
        tif='image/tiff',
        svg='image/svg+xml',
        svgz='image/svg+xml',

        # archives
        zip='application/zip',
        rar='application/x-rar-compressed',
        exe='application/x-msdownload',
        msi='application/x-msdownload',
        cab='application/vnd.ms-cab-compressed',

        # audio/video
        mp3='audio/mpeg',
        ogg='audio/ogg',
        qt='video/quicktime',
        mov='video/quicktime',

        # adobe
        pdf='application/pdf',
        psd='image/vnd.adobe.photoshop',
        ai='application/postscript',
        eps='application/postscript',
        ps='application/postscript',

        # ms office
        doc='application/msword',
        docx='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        dotx='application/application/vnd.openxmlformats-officedocument.wordprocessingml.template',
        rtf='application/rtf',
        xls='application/vnd.ms-excel',
        xltx='application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        xlsx='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ppt='application/vnd.ms-powerpoint',
        pptx='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        sldx='application/vnd.openxmlformats-officedocument.presentationml.slide',
        csv='text/csv',

        # open office
        odt='application/vnd.oasis.opendocument.text',
        ods='application/vnd.oasis.opendocument.spreadsheet',
    )
    types = mime_types[extension]
    types = types if types else "application/octet-stream"
    return types   
#end def    
