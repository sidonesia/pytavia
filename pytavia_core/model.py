import time
import copy
import pymongo
import os
import sys

from bson.objectid import ObjectId


#
# Define the models/collections here for the mongo db
#
db = {
    "db_model_1"                : {
        "name"                  : "",
        "value"                 : "",
        "description"           : "",
        "rec_timestamp"         : 0
    },  
    "db_model_2"                : {
        "name"                  : "",
        "value"                 : "" ,
        "type"                  : "",
        "message"               : "",
        "description"           : "",
        "platform"              : "",
        "code"                  : 0,
        "type"                  : ""
    }
    #.....
}
