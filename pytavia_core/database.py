import time
import copy
import pymongo
import os
import sys
import model
import config
import random

from bson.objectid import ObjectId
from pytavia_stdlib import utils

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

def get_database(database_name):
    return db_active_con[database_name]
# end def

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

def _db_add_archive_field(record):
    record["archived_timestamp"]        = ""
    record["archived_timestamp_str"]    = ""

def db_fk_settings(record, add_archived_field = config.G_RECORD_ADD_ARCHIVED_TIMESTAMP):
    # in models.py, we may define the reference array with a single item for the structure. We will empty it here before insert.
    for key in record:
        if type(record[key]) == list and key.startswith('fk'):
            record[key] = []
        elif add_archived_field == True and type(record[key]) == dict and key.startswith('fk'):
            _db_add_archive_field(record[key])

    record.pop('__db__readable__name__', None)      # removes the readable name of the database before insertion
    record.pop('__db__referenced__names__', None)   

def get_record(db_table):
    record    = copy.deepcopy(db[db_table])
    
    db_fk_settings(record)

    timestamp, timestamp_str = utils._get_current_timestamp()
    record["rec_timestamp"    ] = timestamp
    record["rec_timestamp_str"] = timestamp_str


    record["_id" ] = ObjectId()
    record["pkey"] = str( record["_id"] )
    return copy.deepcopy( record )
#end def

def _traverse_record(record, keys, add_archived_field = config.G_RECORD_ADD_ARCHIVED_TIMESTAMP):
    if len(keys) == 0:
        if add_archived_field:
            _db_add_archive_field(record)
        return record
    
    traversal_key = keys.pop(0)
    if traversal_key == "$[]":
        if len(record) != 0:
            record[0] = _traverse_record(record[0], keys)
        else:
            return []
    elif traversal_key == "$[elem]":
        return []
    elif traversal_key in record:
        record[traversal_key] = _traverse_record(record[traversal_key], keys)
    
    return record


def _clean_record(record, table_fks, add_archived_field = config.G_RECORD_ADD_ARCHIVED_TIMESTAMP):
    # in models.py, we may define the reference array with a single item for the structure. We will empty it here before insert.
    for path in table_fks:
        keys = next(iter(path)).rstrip(".").split(".")
        record = _traverse_record(record, keys)

    record.pop('__db__readable__name__', None)      # removes the readable name of the database before insertion
    record.pop('__db__referenced__names__', None)   

    return record

def new_record(db_handle, db_table, db_table_fks, add_modified_field = config.G_RECORD_ADD_MODIFIED_TIMESTAMP, add_archived_field = config.G_RECORD_ADD_ARCHIVED_TIMESTAMP):
    record = copy.deepcopy(db[db_table])
    
    record = _clean_record(record, db_table_fks[db_table], add_archived_field)

    record["__db__name__"     ] = db_table

    timestamp, timestamp_str    = utils._get_current_timestamp()
    record["rec_timestamp"    ] = timestamp
    record["rec_timestamp_str"] = timestamp_str
    
    if add_modified_field:
        record["last_modified_timestamp"] = ""
        record["last_modified_timestamp_str"] = ""

    if add_archived_field:
        _db_add_archive_field(record)

    random_hex   = os.urandom(24).hex()
    random_int   = random.randint( config.G_RANDOM_START , config.G_RANDOM_END )
    req_id       = random_hex + "-" + str(random_int)

    record["_id"  ] = ObjectId()
    record["ipkey"] = str( record["_id"] )
    record["pkey" ] = record["ipkey"] + "-" + req_id
    mongo_record_model      = model.mongo_model( record , record , db_handle )
    return  mongo_record_model 
#end def

def new(db_handle, db_table, add_modified_field = config.G_RECORD_ADD_MODIFIED_TIMESTAMP, add_archived_field = config.G_RECORD_ADD_ARCHIVED_TIMESTAMP):
    record    = copy.deepcopy(db[db_table])

    db_fk_settings(record, add_archived_field)

    record["__db__name__"     ] = db_table

    timestamp, timestamp_str    = utils._get_current_timestamp()
    record["rec_timestamp"    ] = timestamp
    record["rec_timestamp_str"] = timestamp_str
    
    if add_modified_field:
        record["last_modified_timestamp"] = ""
        record["last_modified_timestamp_str"] = ""

    if add_archived_field:
        _db_add_archive_field(record)

    random_hex   = os.urandom(24).hex()
    random_int   = random.randint( config.G_RANDOM_START , config.G_RANDOM_END )
    req_id       = random_hex + "-" + str(random_int)

    record["_id"  ] = ObjectId()
    record["ipkey"] = str( record["_id"] )
    record["pkey" ] = record["ipkey"] + "-" + req_id
    mongo_record_model      = model.mongo_model( record , record , db_handle )
    return  mongo_record_model 
#end def

def load(db_handle, db_table):
    record    = copy.deepcopy(db[db_table])

    db_fk_settings(record)

    record["__db__name__" ] = db_table
    mongo_record_model      = model.mongo_model( {} , record , db_handle )
    return mongo_record_model
#end def
#

# we use this if we only need the lookup db record
# primarily used in deep update
def simple_load(db_table, complete=False):
    record    = copy.deepcopy(db[db_table])
    record.pop('__db__readable__name__', None)
    record.pop('__db__referenced__names__', None)

    if complete:
        record["rec_timestamp"    ] = ""
        record["rec_timestamp_str"] = ""
        record["archived_timestamp"]        = ""
        record["archived_timestamp_str"]    = ""
        record["last_modified_timestamp"] = ""
        record["last_modified_timestamp_str"] = ""
        record["_id"  ] = ""
        record["ipkey"] = ""
        
    return record

def get_fk_structure(db_table, fk_key, add_archived_field = config.G_RECORD_ADD_ARCHIVED_TIMESTAMP):
    main_table = simple_load(db_table)
    fk_structure = None

    if fk_key in main_table:
        fk_structure = main_table[fk_key]
        if add_archived_field:
            fk_structure_type = type(fk_structure)
            if fk_structure_type == dict:
                _db_add_archive_field(fk_structure)
            elif fk_structure_type == list:
                if len(fk_structure) > 0 and type(fk_structure[0]) == dict:
                    _db_add_archive_field(fk_structure[0])
    
    return fk_structure

def get_readable_name(db_table):
    db_readable_name = ""

    if not db_table:
        return db_readable_name

    record = copy.deepcopy(db[db_table])
    if "__db__readable__name__" in record:
        db_readable_name = record["__db__readable__name__"]
    
    return db_readable_name

def get_referenced_names(db_table):
    record = copy.deepcopy(db[db_table])
    db_referenced_names = []
    if "__db__referenced__names__" in record:
        db_referenced_names = record["__db__referenced__names__"]
    
    return db_referenced_names