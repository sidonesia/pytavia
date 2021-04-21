import sys

sys.path.append("pytavia_core"    ) 
sys.path.append("pytavia_stdlib"  ) 

from pytavia_stdlib import utils
from pytavia_core   import database
from pytavia_core   import config

ALL_PKEYS = True        # set to True if we want to automatically create an index for pkey
DROP_FIRST = True       # set to True if we want to drop the indexes first before creation

db_handle   = database.get_database(config.mainDB)
collections = database.db

# define indexes here
# for each collection, define the indexes that we want to create
defined_indexes = {
    # "db_wp_casino"  : [             
    #     [('wp_title', 'text'),('wp_translations.en.wp_excerpt', 'text')]
    # ],
    # "db_wp_article"    : [
    #     [('wp_title', 'text'),('wp_translations.en.wp_excerpt', 'text')]
    # ],
}

for collection, fields in collections.items():
    print("==================================================")
    print(collection.upper())
    print("==================================================")
    
    if DROP_FIRST:
        db_handle[config.mainDB][collection].drop_indexes()
    if ALL_PKEYS and "pkey" in fields:
        print(db_handle[config.mainDB][collection].create_index("pkey", unique=True))
    
    if collection in defined_indexes:
        for index in defined_indexes[collection]:
            print(db_handle[config.mainDB][collection].create_index(index))
    
    print("==================================================")