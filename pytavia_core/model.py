import time
import copy
import pymongo
import os
import sys

from bson.objectid import ObjectId

class mongo_model:

    def __init__(self, record, lookup, db_handle):
        self._mongo_record  = copy.deepcopy(record)
        self._lookup_record = copy.deepcopy(lookup)
        self._db_handle     = db_handle
    # end def

    def put(self, key, value):
        if not (key in self._lookup_record):
            raise ValueError('SETTING_NON_EXISTING_FIELD', key, value)
        # end if
        self._mongo_record[key] = value
    # end def

    def get(self):
        return self._mongo_record
    # end def	

    def delete(self , query):
        collection_name = self._lookup_record["__db__name__"]
        self._db_handle[collection_name].remove( query )
    # end def

    def insert(self):
        collection_name = self._lookup_record["__db__name__"]
        del self._mongo_record["__db__name__"]
        self._db_handle[collection_name].insert(  
            self._mongo_record
        )
    # end def

    def update(self, query):
        collection_name = self._lookup_record["__db__name__"]
        self._db_handle[collection_name].update(
            query, 
            { "$set" : self._mongo_record }
        )
    # end def
# end class
#
#
# Define the models/collections here for the mongo db
#

db = {
    # SYSTEM TABLES WITH _sys_, do not modify
    "db_sys_resume_history"         : {
        "resume_token"              : {},
        "handler_name"              : "",
        "collection"                : "",
        "operation_type"            : "",
        "database"                  : "",
        "document_key"              : "",
        "cluster_time"              : 0 ,
        "rec_timestamp"             : "",
    },

    # USER TABLES BELOW HERE, MODIFYABLE

    "db_application_sys_log"          : {
        "fk_app_id"                   : "",
        "fk_user_id"                  : "",
        "fk_app_user_id"              : "",
        "status"                      : "",
        "status_timestamp"            : "",
        "updated_by"                  : "", 
        "pkey"                        : "",
        "misc"                        : {},
    },

}
