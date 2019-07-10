import datetime
import time
import random
import hashlib
import string

from pytavia_core import config
from pytavia_core import database

def _get_api_call_id():
    now_time     = int(time.time())
    current_date = datetime.datetime.now()
    month_tm     = current_date.month
    day_tm       = current_date.day
    hour_tm      = current_date.hour
    minute_tm    = current_date.minute
    second_tm    = current_date.second
    start_id     = str(now_time) + str(hour_tm) + str(minute_tm) + str(second_tm)
    random_num   = random.randint(1, 10000000)
    invoice_code = "API_CALL_" + str( start_id ) + "_" + str(random_num)
    return invoice_code
#end if

def _gen_email_verify(fk_user_id,customer_id):
    token_string = str(fk_user_id) + "%%%" + str(fk_user_id) + "%%%" + str(customer_id) +\
                "%%%" + config.G_VERIFY_SECRET
    token = hashlib.sha256(token_string.encode('ascii')).hexdigest()
    return token
# end def

#
# This will create a new transaction code everytime its called
#
def _get_req_id():
    request_rec = wmsDB.db_request_id.find_and_modify(
        query    = {},
        update   = { "$inc" : {"req_id" : 1}}
    )
    now_time     = int(time.time())
    req_id       = int(request_rec["req_id"]) + 100000000000
    return str(req_id)
# end def

def _get_alpha_req_id():
    request_rec = wmsDB.db_request_id.find_and_modify(
        query    = {},
        update   = { "$inc" : {"req_id" : 1}}
    )
    now_time     = int(time.time())
    req_id       = int(request_rec["req_id"]) + 1000000
    return  str(req_id)
# end def


def _get_token_gen():
    token_trx_rec = wmsDB.db_token_trx_id.find_and_modify(
        query     = {},
        update    = { "$inc" : {"token_counter" : 1}}
    )
    token_counter = int(token_trx_rec["token_counter"])
    return token_counter
# end def

def _get_code_gen():
    token_trx_rec = wmsDB.db_code_trx_id.find_and_modify(
        query    = {},
        update   = { "$inc" : {"code_counter" : 1}}
    )
    code_counter = int(token_trx_rec["code_counter"])
    byte1 = ''.join([
        random.choice(string.ascii_letters + string.digits) for n in range(7)
    ])
    byte2 = ''.join([
        random.choice(string.ascii_letters + string.digits) for n in range(7)
    ])
    byte3 = ''.join([
        random.choice(string.ascii_letters + string.digits) for n in range(7)
    ])
    byte4 = ''.join([
        random.choice(string.ascii_letters + string.digits) for n in range(7)
    ])
    issued_code = byte1 + str(code_counter) + byte2 + str(code_counter) + byte3 +\
                str(code_counter) + byte4
    if code_counter >= 9:
        wmsDB.db_code_trx_id.update(
            {},{"$set":{"code_counter":0}}
        )
    # end def
    issued_code = issued_code.lower()
    return issued_code
# end def

def _get_ticket_code_checksum(params):
    gen_tm       = params["gen_tm"      ]
    start_tm     = params["start_tm"    ]
    end_tm       = params["end_tm"      ]
    device_id    = params["device_code" ]
    fk_user_id   = params["fk_user_id"  ]
    fk_wallet_id = params["fk_wallet_id"]
    item_value   = params["item_value"  ]
    item_id      = params["item_id"     ]
    code         = params["code"        ]
    formula      = str( gen_tm     ) + "%%|%%" + str( start_tm     ) + "%%|%%" +\
                   str( end_tm     ) + "%%|%%" + str( device_id    ) + "%%|%%" +\
                   str( fk_user_id ) + "%%|%%" + str( item_value   ) + "%%|%%" +\
                   str( code       ) + "%%|%%" + str( fk_wallet_id ) + "%%|%%" +\
                   str( item_id    ) + str( config.G_DEVICE_TOKEN  )
    #
    # this is where the token value is
    #
    token = hashlib.sha256(formula.encode('ascii')).hexdigest()
    return token
# end def
