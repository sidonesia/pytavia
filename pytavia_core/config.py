import os

G_FLASK_SECRET=b'PUT YOUR SECRET HERE'

# This is the home path for the home of this project
G_HOME_PATH=os.getcwd()

# This is where all the cookies are stored
G_SESSION_STORAGE           = G_HOME_PATH + "/settings/storage"
G_STATIC_URL_PATH           = G_HOME_PATH + "/static"
G_STATIC_URL_PATH           = "/static"
G_UPLOAD_PATH               = G_HOME_PATH + G_STATIC_URL_PATH + "/upload"
G_UPLOAD_URL_PATH           = G_STATIC_URL_PATH + "/upload"

G_BASE_URL                 = "http://127.0.0.1:17003"
mainDB                     = "re-develop-db"
mainDB_string              = "mongodb://127.0.0.1:27017/"  + mainDB

# This is where we have all the databases we want to connect to
G_DATABASE_CONNECT=[
    {"dbname" : mainDB , "dbstring" : mainDB_string},
]
