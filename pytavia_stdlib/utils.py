import datetime
import time
import random
import hashlib
import datetime
import os

from pytavia_core import config
from pytavia_core import database

wmsDB = database.get_db_conn( config.mainDB )

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
    url_location = config.G_BASE_URL    + config.G_UPLOAD_URL_PATH + params["folder"] + "/" + file_name
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
