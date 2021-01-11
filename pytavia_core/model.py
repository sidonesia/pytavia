import copy

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

    def insert(self, lock=None):
        collection_name = self._lookup_record["__db__name__"]
        del self._mongo_record["__db__name__"]
        if lock == None:
            self._db_handle[collection_name].insert_one(  
                self._mongo_record
            )
        else:
            self._db_handle[collection_name].insert_one(  
                self._mongo_record,
                session=lock
            )
        # end if
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
    
"""
### New way to define tables -- required in using bulk_db_action.py
### Samples below

    "db_book"                       : {
        "__db__readable__name__"    : "Book",           ### define a readable table name here -- this will be used for returning meaningful status codes in pytavia validations
        "pkey"                      : "",               
        "name"                      : "",               ### some fields
        "fk_publisher"              : {                 ### 1:1 Relationship -- duplicate the publisher name -- notice the pattern of fk_fieldname. db_publisher -> fk_publisher
            "pkey"                  : "",
            "name"                  : "",               ### foreign key field name should be exactly the same to the origin table
        },
        "fk_author"                 : [{                ### 1:M Relationship -- same pattern from db_author to fk_author
            "pkey"                  : "",
            "name"                  : "",               ### same, field names should be exactly the same for the deduplication logic to work
            "picture"               : ""                ### duplicates the db_author's picture as well so we won't have to have a separate query
        }]
    },

    "db_publisher"                  : {                
        "__db__readable__name__"    : "Publisher",      ### same, define a readable name for the table -- to be displayed on response messages / descriptions
        "pkey"                      : "",               
        "name"                      : "",               ### duplicated in db_book
        "fk_book"                   : [{                ### 1:M Relationship
            "pkey"                  : "",
            "name"                  : ""                ### duplicates db_book's name to save a query
        }]
    },

    "db_author"                     : {                 
        "__db__readable__name__"    : "Author",         
        "pkey"                      : "",               
        "name"                      : "",
        "picture"                   : "",               ### duplicated in db_book -- notice how the field names are exactly the same
        "fk_book"                   : [{                ### 1:M Relationship
            "pkey"                  : "",
            "name"                  : ""                ### again, db_book's name is duplicated here
        }]
    }
"""

}
