import time
import copy
import pymongo
import os
import sys
import model
import config

from bson.objectid import ObjectId

db_conn_completed = False

db_conn = {}
for row in config.G_DATABASE_CONNECT:
    db_conn[row["dbname"]] = row["dbstring"]
#end for

db_active_con = {}
for row in config.G_DATABASE_CONNECT:
    db_active_con[row["dbname"]] = None
#end for

db = model.db

def connect_db():
    for row in config.G_DATABASE_CONNECT:
        if db_active_con[row["dbname"]] == None:
            db_active_con[row["dbname"]] = pymongo.MongoClient( db_conn[row["dbname"]] )
        # end if
    #end for
    db_conn_completed = True
#end def

def get_db_conn(db_conn):
    # make sure we are connected to the database
    if not db_conn_completed:
        connect_db()
    #end if

    # get the specific handle we want to connect to
    handle = db_active_con[db_conn][db_conn]
    handle.db_conn.find({})
    return handle
#end def

def get_record(db_table):
    timestamp = int(time.time()) * 1000
    record    = db[db_table]
    record["rec_timestamp"] = timestamp
    record["_id"]           = ObjectId()
    record["pkey"]          = str( record["_id"] )
    return copy.deepcopy( record )
#end def
