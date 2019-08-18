import os
import sys
import copy

sys.path.append("pytavia_core"    )
sys.path.append("pytavia_modules" )
sys.path.append("pytavia_settings")
sys.path.append("pytavia_stdlib"  )
sys.path.append("pytavia_storage" )

from pytavia_stdlib import idgen

G_FLASK_SECRET=b'_5#y2L"F4Q8z\n\xec]/'

# This is the home path for the home of this project
G_HOME_PATH=os.getcwd()

# This is where all the cookies are stored
G_SESSION_STORAGE           = G_HOME_PATH + "/settings/storage"
G_STATIC_URL_PATH           = G_HOME_PATH + "/static"
G_STATIC_URL_PATH           = "/static"
G_UPLOAD_PATH               = G_HOME_PATH + G_STATIC_URL_PATH + "/upload"
G_UPLOAD_URL_PATH           = G_STATIC_URL_PATH + "/upload"

# CORE DATABASES DO NOT MODIFY

pytavia_dispatchDB  = "pytavia_dispatchDB"
pytavia_dispatch    = "mongodb://127.0.0.1:27017/" + pytavia_dispatchDB

###################### USER DATABASES BELOW HERE (MODIFYABLE) 


mainDB                      = "cc-credit-scoring-DB-2"
mongo_main_db_report_string = "mongodb://127.0.0.1:27017/" + mainDB

# This is where we have all the databases we want to connect to
G_DATABASE_CONNECT  = [
    {"dbname" : pytavia_dispatchDB , "dbstring" : pytavia_dispatch },

    # USER DATABASES MODIFY BELOW
    {"dbname" : mainDB , "dbstring" : mongo_main_db_report_string  },
]

G_RANDOM_START = 1000000
G_RANDOM_END   = 9999999
