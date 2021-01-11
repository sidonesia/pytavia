
import config
import database

from model import mongo_model

from pytavia_stdlib import utils

INSERT = "INSERT"
DELETE = "DELETE"
UPDATE = "UPDATE"

class bulk_db_action:

    action_list = []
    db_handle   = None
    
    def __init__(self, params):
        self.db_handle   = params["db_handle"]
        self.webapp      = params["app"]
        self.action_list = []
    # end def

    def add( self, action, collection , query=None , update=None , multi_operation = False , array_filters=None ):
        self.action_list.append({
            "action"            : action,
            "collection"        : collection,
            "query"             : query,
            "update"            : update,
            "array_filters"     : array_filters,
            "multi_operation"   : multi_operation
        })
    # end def


    # IMPORTANT NOTES:
    # 1. Collection name and Reference key should follow the following pattern: db_main -> fk_main e.g db_book.fk_author // db_author
    # 2. Expects Two Way References -- If sub collection is not referenced in main collection, main record will not be updated in sub record 
        # Pattern: parent/child reference (fk_something = ''), embedded (fk_something = {}), list of embedded (fk_something = [{}])
    # 3. Collection fields and referenced fields should be exactly the same. e.g. db_book.name -> db_author.fk_book.name
    # 4. Currently, deep update of pkeys are not supported
    # 5. Strictly uses the key 'pkey'. 
        # Supported patterns for fk_pkey. Integers and ObjectIds are currently not supported.
        # ... str   - fk_author = 'some_pkey'
        # ... dict  - fk_author['pkey'] = 'some_pkey'
        # ... list  - fk_author[x]['pkey'] = 'some_pkey'
    # 6. If an array of reference is used in a collection, a pattern should be defined in models.py
        # e.g. db_author { fk_book : [{ 'pkey' : '', 'name' : '' } ] }
        # This is very important. This single item will be cleared when database.new() is used to instantiate a record before insertion.
    # 7. Currently, it only runs on config.mainDB
    # 8. Not tested on updating fk_fields.. Probably it will still work.
    def deep_update(self, collection , query , update):
        # main - main collection being updated
        # sub - sub collection where main is referenced and duplicated and needs to be updated as well
        
        # update for the main record
        self.add(UPDATE, collection, query, update, multi_operation=True)

        # referred key of main located in sub collection
        # if main collection == db_book and sub collection == db_author
        # ... then fk_book is the expected and supposed referenced key of main in sub collection
        sub_main_field_key = collection.replace('db','fk', 1)
        # let us get all the keys updated in the main collection
        # we will check if these fields are duplicated and 
        # ... needs to be updated as well in sub collection
        main_updated_fields = list(update['$set'].keys())  #do we need to check if key starts with fk???

        # find all records in main collection that are affected by the update
        main_record_view = self.db_handle[config.mainDB][collection].find(query)
        # for each record in main, we will update any duplicated fields in sub / foreign collection
        # most likely, this will only run once because we commonly use update on one record only
        for main_record in main_record_view:   
            for key in main_record:
                if not key.startswith('fk'):    # fk is a standard for defining foreign keys to other collection
                    continue                    # skip -- if key in main record is not a foreign key to another collection
                                                # this is VERY important, if the main collection is duplicated in other sub collection but
                                                # ... sub collection is not referenced on the main colleciton, THIS UPDATE WILL NOT WORK!
                
                main_record_id = main_record['pkey']
                main_record_field = main_record[key]
                main_record_field_type = type(main_record_field)
                if main_record_field_type == str:
                    if main_record_field == '':                 # skip -- if main_collection['fk_sub_collection'] is not set -- nothing is referenced
                        continue
                    sub_record_id = main_record[key]
                elif main_record_field_type == dict:            
                    if 'pkey' not in main_record_field or main_record_field['pkey'] == '':
                        continue                                # skip -- if main_collection['fk_sub_collection']['pkey'] is not set -- nothing is referenced
                    sub_record_id = main_record[key]['pkey']
                elif main_record_field_type == list:            # skip -- if main_collection['fk_sub_collection'] does not contain any key -- nothing is referenced
                    if len(main_record_field) == 0:
                        continue
                else:                                           # skip -- if reference is not supported. The following are the only ones supported:
                    continue                                    # ... str   - fk_author = 'some_pkey'
                                                                # ... dict  - fk_author['pkey'] = 'some_pkey'
                                                                # ... list  - fk_author[x]['pkey'] = 'some_pkey'
                
                # if fk key is found in main collection, replace fk by db to get the sub collection
                # e.g. if main collection = db_books and fk_author is found then we do the replace
                # ... to get the sub collection which is db_author
                # THIS is the standard if we want to use this functionality
                sub_collection  = key.replace('fk','db', 1) 
                # db_sub_lookup   = database.simple_load(sub_collection)    # get the sub collection pattern defined in the schema
                # if sub_main_field_key in db_sub_lookup:                 # if the main collection is referenced inside the sub collection
                #     sub_main_field = db_sub_lookup[sub_main_field_key]
                # else:
                #     continue                                            # skip -- if one way reference only -- nothing to update in sub collection -- this is a bad case
                sub_main_field  = database.get_fk_structure(sub_collection, sub_main_field_key)
                if sub_main_field == None:
                    continue
                
                sub_main_field_type = type(sub_main_field)
                if sub_main_field_type == dict:                                         # if main is referenced as a dict in sub collection. e.g. db_author.fk_book['name']
                    sub_main_field_subkeys = list(sub_main_field.keys())                # get all the keys of db_author.fk_book
                    set_operation = '.'                                                 # key operation to be used in update.$set. e.g. fk_book.name
                elif sub_main_field_type == list:                                       
                    if len(sub_main_field) > 0 and type(sub_main_field[0]) == dict:     # if main is referenced as a list in sub collection. e.g. db_author.fk_book[x]['name']
                        sub_main_field_subkeys = list(sub_main_field[0].keys())         # schema in model contains one record for structure                                           
                        set_operation = '.$[elem].'                                     # if list, this will be used as key in update.$set operation. e.g. fk_book.$[elem].name
                        sub_array_filters = [ { "elem.pkey": main_record_id } ]         # array filter for mongo update
                    else:
                        continue                    # skip -- dict structure not defined inside the list. e.g. db_author.fk_book = [some_pkeys]. 
                else:                               # ... it may be possible that it is intended to be used as list of pkeys
                    continue                        # most likely, main is referenced as a string pkey in sub collection e.g. db_author.fk_book = "some_pkey"
                                                    # ... we do not support deep updates for pkeys yet
                                                    # ... alternatively, defined it as dict with a single key pkey

                duplicate_fields = list(set(main_updated_fields).intersection(sub_main_field_subkeys))   # get duplicated fields to be updated in sub collection

                sub_update_set = {}                 # following code constructs our update.$set for the sub record
                for field in duplicate_fields:
                    if field == 'pkey':             # skip -- updating pkey -- this function does not support deep updates of pkey!
                        continue                    # maybe throw an exception???
                    sub_update_set[sub_main_field_key + set_operation + field] = update['$set'][field]      # if main == db_book, sub == db_author then 
                                                                                                            # ... this results to: fk_book.name or fk_book.$[elem].name in db_author
                
                if sub_update_set == {}:           
                    continue                         # skip -- nothing to update in sub collection

                sub_record_main_key = sub_main_field_key + '.' + 'pkey'     # will be used for filter  e.g. fk_book.pkey in db_author
                sub_update_set = { '$set' : sub_update_set}

                if main_record_field_type == list:                          # if field in main collection contains an array of reference of sub collection
                    sub_query = []
                    for sub_record in main_record_field:                    # update each sub record
                        if type(sub_record) == dict:                        # reference may be a list of pkeys or a list of dictionaries with expected pkeys on it
                            sub_record_id = sub_record['pkey']              # e.g. db_book.fk_author[x]['pkey'] = 'some_pkey'
                        else:
                            sub_record_id = sub_record                      # e.g. db_book.fk_author[x] = 'some_pkey'
                        
                        if sub_main_field_type == list:
                            sub_query.append({ 'pkey' : sub_record_id})     # faster query if reference of main in sub collection is an array
                        else:
                            sub_query.append({ 'pkey' : sub_record_id, sub_record_main_key : main_record_id })

                    if len(sub_query) > 1:
                        sub_query = {"$or" : sub_query}
                    else:
                        sub_query = sub_query[0]
                else:                                                       # if field type is str or dict,  we only need to update one record in sub collection
                    if sub_main_field_type == list:
                        sub_query = { 'pkey' : sub_record_id }              # faster query if reference of main in sub collection is an array
                    else:
                        sub_query = { 'pkey' : sub_record_id, sub_record_main_key : main_record_id }
                
                if sub_main_field_type == list:                             # if reference of main in sub collection is an array -- add array filters!
                    self.add(UPDATE, sub_collection, sub_query, sub_update_set, multi_operation=True, array_filters=sub_array_filters)     # bulk_update.execute must use update_many!
                else:
                    self.add(UPDATE, sub_collection, sub_query, sub_update_set, multi_operation=True)

    def _deep_link_update_constructor(self, fk_structure, record, record_ref_key, touch_timestamp=True):
        
        # construct update for collection
        fk_structure_type = type(fk_structure)
        if fk_structure_type == str:              # pkey reference only
            fk_update = record["pkey"]
            update = { "$set" : { record_ref_key : fk_update } }

        elif fk_structure_type == dict:           # dict reference
            fk_update = {}
            for key in fk_structure:
                fk_update[key]  = record[key]
            update = { "$set" : { record_ref_key : fk_update } }

        elif fk_structure_type == list:           # list of reference
            if len(fk_structure) > 0 and type(fk_structure[0]) == dict:             # list of dict reference
                fk_update = {}
                for key in fk_structure[0]:
                    fk_update[key]  = record[key]
            else:                                 # list of pkeys
                fk_update = record["pkey"]

            update = { "$push" : { record_ref_key : fk_update } }

        if touch_timestamp:
            if "$set" not in update:
                update["$set"] = {}
            timestamp, timestamp_str = utils._get_current_timestamp()
            update["$set"]["last_modified_timestamp"    ] = timestamp
            update["$set"]["last_modified_timestamp_str"] = timestamp_str

        return update

    def two_way_reference(self, main, sub, touch_timestamp=True):
        main_collection = main["collection" ]       # db_main    
        sub_collection  = sub["collection"  ]       # db_sub   
        main_record     = main["record"     ]       
        sub_record      = sub["record"      ]

        # in some cases where record is not yet inserted, we have an object of mongo_model instead of a dict
        # we don't have to deep copy if we'll just use it as reference
        if isinstance(main_record, mongo_model):
            main_record = main_record.get()         # returns the record in dict

        if isinstance(sub_record, mongo_model):
            sub_record  = sub_record.get()          # returns the record in dict

        main_ref_key    = main_collection.replace('db','fk', 1  )       #db_main -> fk_main
        sub_ref_key     = sub_collection.replace('db','fk', 1   )       #db_sub -> fk_sub

        # db_main_lookup  = database.simple_load(main_collection  )       #db_main's collection pattern in model.py
        # db_sub_lookup   = database.simple_load(sub_collection   )       #db_sub's collection pattern in model.py

        # fk_sub_struct   = db_main_lookup[sub_ref_key]   # reference structure of fk_sub in db_main
        fk_sub_struct   = database.get_fk_structure(main_collection, sub_ref_key)
        # fk_main_struct  = db_sub_lookup[main_ref_key]   # reference structure of fk_main in db_sub
        fk_main_struct  = database.get_fk_structure(sub_collection, main_ref_key)

        # construct update for main collection
        main_update = self._deep_link_update_constructor(fk_sub_struct, sub_record, sub_ref_key, touch_timestamp)
        self.add(
            UPDATE,
            main_collection,
            { "pkey"    : main_record["pkey"] },
            main_update
        )

        # construct update for sub collection
        sub_update = self._deep_link_update_constructor(fk_main_struct, main_record, main_ref_key, touch_timestamp)
        self.add(
            UPDATE, 
            sub_collection,
            { "pkey"    : sub_record["pkey"] },
            sub_update
        )

    def _deep_unlink_update_constructor(self, fk_structure, fk_pkey, record_ref_key, touch_timestamp=True):
        
        # construct update for collection
        fk_structure_type = type(fk_structure)

        if fk_structure_type == list:
            if len(fk_structure) > 0 and type(fk_structure[0]) == dict:         # list of dictionary reference
                fk_update = { "pkey" : fk_pkey }
            else:                                                               # list of pkeys reference
                fk_update = fk_pkey
            update = { "$pull" : { record_ref_key : fk_update } }

        elif fk_structure_type == dict or fk_structure_type == str:
            fk_update = fk_structure
            update = { "$set" : { record_ref_key : fk_update } }

        if touch_timestamp:
            if "$set" not in update:
                update["$set"] = {}
            timestamp, timestamp_str = utils._get_current_timestamp()
            update["$set"]["last_modified_timestamp"    ] = timestamp
            update["$set"]["last_modified_timestamp_str"] = timestamp_str
        
        return update

    def remove_two_way_reference(self, main, sub, touch_timestamp=True):
        main_collection = main["collection" ]       #db_main    
        sub_collection  = sub["collection"  ]       #db_sub   
        main_record     = main["record"     ]       
        sub_record      = sub["record"      ]       

        # in some cases where record is not yet inserted, we have an object of mongo_model instead of a dict
        # we don't have to deep copy if we'll just use it as reference
        if isinstance(main_record, mongo_model):
            main_record = main_record.get()         # returns the record in dict

        if isinstance(sub_record, mongo_model):
            sub_record  = sub_record.get()          # returns the record in dict
        
        main_ref_key    = main_collection.replace('db','fk', 1  )       #db_main -> fk_main
        sub_ref_key     = sub_collection.replace('db','fk', 1   )       #db_sub -> fk_sub

        # db_main_lookup  = database.simple_load(main_collection  )       #db_main's collection pattern in model.py
        # db_sub_lookup   = database.simple_load(sub_collection   )       #db_sub's collection pattern in model.py

        # fk_sub_struct   = db_main_lookup[sub_ref_key]   # reference structure of fk_sub in db_main
        # fk_main_struct  = db_sub_lookup[main_ref_key]   # reference structure of fk_main in db_sub
        fk_sub_struct   = database.get_fk_structure(main_collection, sub_ref_key)
        fk_main_struct  = database.get_fk_structure(sub_collection, main_ref_key)


        main_record_pkey = main_record["pkey"   ]
        sub_record_pkey = sub_record["pkey"     ]

        # construct update for main collection
        main_update = self._deep_unlink_update_constructor(fk_sub_struct, sub_record_pkey, sub_ref_key, touch_timestamp)
        self.add(
            UPDATE,
            main_collection,
            { "pkey"    : main_record_pkey },
            main_update
        )

        # construct update for sub collection
        sub_update = self._deep_unlink_update_constructor(fk_main_struct, main_record_pkey, main_ref_key, touch_timestamp)
        self.add(
            UPDATE,
            sub_collection,
            { "pkey"    : sub_record_pkey },
            sub_update
        )

    def execute(self, params):
        with self.db_handle.start_session() as lock:
            lock.start_transaction()
            for record in self.action_list:
                action = record["action"]

                if action == UPDATE:
                    collection          = record["collection"       ]
                    cmd_query           = record["query"            ]    
                    cmd_update          = record["update"           ]
                    cmd_array_filters   = record["array_filters"    ]
                    cmd_multi_operation = record["multi_operation"  ]

                    if not cmd_multi_operation:         # default: update_one
                        if cmd_array_filters == None:   # default: not dealing with array
                            self.db_handle[config.mainDB][collection].update_one(
                                cmd_query , cmd_update, session=lock
                            )
                        else:                           # with array filters
                            self.db_handle[config.mainDB][collection].update_one(
                                cmd_query , cmd_update, array_filters=cmd_array_filters, session=lock
                            )
                    else:                               # multi operation
                        if cmd_array_filters == None:   # default: not dealing with array
                            self.db_handle[config.mainDB][collection].update_many(
                                cmd_query , cmd_update, session=lock
                            )
                        else:                           # with array filters
                            self.db_handle[config.mainDB][collection].update_many(
                                cmd_query , cmd_update, array_filters=cmd_array_filters, session=lock
                            )

                elif action == INSERT:
                    collection = record["collection"]
                    collection.insert()

                elif action == DELETE:
                    collection = record["collection"]
                    cmd_query  = record["query"]

                    if not cmd_multi_operation:
                        self.db_handle[config.mainDB][collection].delete_one(
                            cmd_query , session=lock
                        )
                    else:
                        self.db_handle[config.mainDB][collection].delete_many(
                            cmd_query , session=lock
                        )

            # end for
            lock.commit_transaction()
        # end with
    # end def

# end class
