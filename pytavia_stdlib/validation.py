# common used validation
import config
import utils
import database

def _process_name(response, process_name):
    if process_name == "":
        process_name = response.get("status")
        process_name = process_name.replace("SUCCESS", "FAILED")
    return process_name

############################
### DATABASE VALIDATIONS ###
############################
# validation that expects to find one record
def find_one(response, db_handle, collection, query, process_name = "", db=config.mainDB):
    record = db_handle[db][collection].find_one(query)
    if record == None:
        
        db_readable_name = database.get_readable_name(collection)
        if db_readable_name:
            response_desc = "{} record does not exist.".format(db_readable_name)
        else:
            response_desc = config.G_STATUS["RECORD_NOT_FOUND"]['DESC']

        response.put( "status_code" ,  config.G_STATUS["RECORD_NOT_FOUND"]['CODE']  )
        response.put( "status"      ,  _process_name(response, process_name)        )
        response.put( "desc"        ,  response_desc                                )
    return record

def unique(response, db_handle, collection, query, process_name = "", db=config.mainDB):
    record = db_handle[db][collection].find_one(query)
    if record != None:

        field_key = str(list(query.keys())[0])
        db_readable_name = database.get_readable_name(collection)
        if db_readable_name:
            response_desc = "A {1} record with a given field '{2}' already exists".format(db_readable_name, field_key)
        else:
            response_desc = config.G_STATUS["NOT_UNIQUE"]['DESC']

        response.put( "status_code" ,  config.G_STATUS["NOT_UNIQUE"]['CODE']  )
        response.put( "status"      ,  _process_name(response, process_name)        )
        response.put( "desc"        ,  response_desc                                )
    return record

# internal function: looks for reference
def _has_reference(fk_reference, key, q):
    fk_reference_type   = type(fk_reference)
    reference_found     = False

    if fk_reference_type == dict:               # db_book["fk_author"]["pkey"] == "reference_pkey"
        if fk_reference[key] == q:
            reference_found = True

    elif fk_reference_type == list:             # db_book["fk_author"][x]["pkey"] == "reference_pkey"
        reference_found, reference = utils._get_records_in_list(fk_reference, key, q)
    
    elif fk_reference_type == str:
        if fk_reference == q:                   # db_book["fk_author"] == "reference_pkey"
            reference_found = True

    return reference_found

# validation that expects no reference
def no_reference(response, record, fk_list_key, q, key = "pkey", process_name = ""):
    fk_reference        = record[fk_list_key]  
    reference           = None

    reference_found = _has_reference(fk_reference, key, q)

    if reference_found:
        collection = fk_list_key.replace('fk','db', 1) 
        db_readable_name = database.get_readable_name(collection)
        if db_readable_name:
            response_desc = "{} record is already referenced.".format(db_readable_name)
        else:
            response_desc = config.G_STATUS["FK_EXISTS"]['DESC']

        response.put( "status_code" ,  config.G_STATUS["FK_EXISTS"]['CODE']         )
        response.put( "status"      ,  _process_name(response, process_name)        )
        response.put( "desc"        ,  response_desc                                )
        reference = q

    return reference_found, reference

# validation that expects reference
def find_reference(response, record, fk_list_key, q, key = "pkey", process_name = ""):
    fk_reference        = record[fk_list_key]   # db_book["fk_author"]
    reference           = q

    reference_found = _has_reference(fk_reference, key, q)

    if not reference_found:

        collection = fk_list_key.replace('fk','db', 1) 
        db_readable_name = database.get_readable_name(collection)
        if db_readable_name:
            response_desc = "{} record is not referenced.".format(db_readable_name)
        else:
            response_desc = config.G_STATUS["NO_FK_EXISTS"]['DESC']

        response.put( "status_code" ,  config.G_STATUS["NO_FK_EXISTS"]['CODE']      )
        response.put( "status"      ,  _process_name(response, process_name)        )
        response.put( "desc"        ,  response_desc                                )
        reference = q

    return reference_found, reference

###########################
### PAYLOAD VALIDATIONS ###
###########################
# check if any of the fields in the dictionary is empty
def required(response, field_dict, process_name = ""):
    for key, value in field_dict:
        if value == None or value == '':
            response.put( "status_code" ,  config.G_STATUS["FIELD_REQUIRED"]['CODE']    )
            response.put( "status"      ,  _process_name(response, process_name)        )
            response.put( "desc"        ,  "The field '{}' is required.".format(key)    )
            return False
    return True

# check if any of the fields in the dictionary is not a number
def is_number(response, field_dict, process_name = ""):
    for key, value in field_dict:
        value_type = type(value)
        if value_type != float and value_type != int:
            response.put( "status_code" ,  config.G_STATUS["NOT_NUMBER"]['CODE']            )
            response.put( "status"      ,  _process_name(response, process_name)            )
            response.put( "desc"        ,  "The field '{}' should be a number".format(key)  )
            return False
    return True

# check if any of the fields in the dictionary is not greater than the target number
def greater_than(response, field_dict, num_target, process_name = ""):
    for key, value in field_dict:
        if value <= num_target:
            response.put( "status_code" ,  config.G_STATUS["NOT_GREATER_THAN"]['CODE']                          )
            response.put( "status"      ,  _process_name(response, process_name)                                )
            response.put( "desc"        ,  "The field '{1}' should be greater than {2}".format(key, num_target) )
            return False
    return True

# check if any of the fields in the dictionary is not less than the target number
def less_than(response, field_dict, num_target, process_name = ""):
    for key, value in field_dict:
        if value => num_target:
            response.put( "status_code" ,  config.G_STATUS["NOT_LESS_THAN"]['CODE']                         )
            response.put( "status"      ,  _process_name(response, process_name)                            )
            response.put( "desc"        ,  "The field '{1}' should be less than {2}".format(key, num_target))
            return False
    return True