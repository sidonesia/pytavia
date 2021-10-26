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

def _get_current_timestamp(time_format = None):
    if time_format == None:
        try:
            time_format = config.G_STR_TIME_FORMAT
        except:
            time_format = "%Y-%m-%d %H:%M:%S"
            
    curr_time = int(time.time())
    timestamp = curr_time * 1000
    timestamp_str = time.strftime(
        time_format, time.localtime(curr_time)
    )

    return timestamp, timestamp_str

def _get_records_in_list(array, key, q):
    record_list = list(filter(lambda dictionary: dictionary[key] == q, array))
    found = False
    
    if len(record_list) > 0:
        found = True
        
    return found, record_list

def _to_process_name(text):
    return text.upper().replace(" ", "_")

def _db_name_to_fk_name(db_name):
    return db_name.replace('db','fk', 1) 

def _fk_name_to_db_name(db_name):
    return db_name.replace('fk','db', 1) 

def _db_name_to_response_name(db_name):
    return db_name.replace('db_','', 1) 

def _set_dict_defaults(record, defaults):
    for key, value in defaults.items():
        if key not in record:
            record[key] = value
    return record

def _boolean(variable):
    true_list = [ "true", "yes", 1, True ]
    if type(variable) == str:
        variable = variable.lower()
    
    return True if variable in true_list else False

# replace last 'x' occurrences of old to new
# source: https://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)