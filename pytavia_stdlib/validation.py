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
def find_one(response, db_handle, collection, query, projection = None, process_name = "", db=config.mainDB):
    record = db_handle[db][collection].find_one(query, projection)
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

#TODO: improve this to handle record updates. check every record except itself.
#TODO: also, how about allowing multiple fields to be checked to save query? maybe use an or
#TODO: even a compound unique can be done here.
def unique(response, db_handle, collection, query, process_name = "", db=config.mainDB):
    record = db_handle[db][collection].find_one(query)
    if record != None:

        field_key = str(list(query.keys())[0])
        db_readable_name = database.get_readable_name(collection)
        if db_readable_name:
            response_desc = "A {0} record with a given field '{1}' already exists".format(db_readable_name, field_key)
        else:
            response_desc = config.G_STATUS["NOT_UNIQUE"]['DESC']

        response.put( "status_code" ,  config.G_STATUS["NOT_UNIQUE"]['CODE']    )
        response.put( "status"      ,  _process_name(response, process_name)    )
        response.put( "desc"        ,  response_desc                            )
    return record

def unique_field(response, db_handle, collection, query, field_name, process_name = "", db=config.mainDB):
    record = db_handle[db][collection].find_one(query)
    if record != None:

        db_readable_name = database.get_readable_name(collection)
        if db_readable_name:
            response_desc = "A {0} record with a given field '{1}' already exists".format(db_readable_name, field_name)
        else:
            response_desc = config.G_STATUS["NOT_UNIQUE"]['DESC']

        response.put( "status_code" ,  config.G_STATUS["NOT_UNIQUE"]['CODE']    )
        response.put( "status"      ,  _process_name(response, process_name)    )
        response.put( "desc"        ,  response_desc                            )
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
    for key, value in field_dict.items():
        if value == None or value == '' or value == []:
            response.put( "status_code" ,  config.G_STATUS["FIELD_REQUIRED"]['CODE']    )
            response.put( "status"      ,  _process_name(response, process_name)        )
            response.put( "desc"        ,  "The field '{}' is required.".format(key)    )
            return False
    return True

# check if any of the fields in the dictionary is not a number
def is_number(response, field_dict, process_name = ""):
    for key, value in field_dict.items():
        value_type = type(value)
        if value_type != float and value_type != int:
            if value_type == str and value.replace('.', '', 1).isdigit():
                return True
            response.put( "status_code" ,  config.G_STATUS["NOT_NUMBER"]['CODE']            )
            response.put( "status"      ,  _process_name(response, process_name)            )
            response.put( "desc"        ,  "The field '{}' should be a number".format(key)  )
            return False
    return True

# check if any of the fields in the dictionary is not in snakecase
def is_snakecase(response, field_dict, process_name = ""):
    for key, value in field_dict.items():
        if " " in value or value.lower() != value:
            response.put( "status_code" ,  config.G_STATUS["NOT_SNAKECASE"]['CODE']         )
            response.put( "status"      ,  _process_name(response, process_name)            )
            response.put( "desc"        ,  "The field '{}' should be in snakecase format.".format(key)  )
            return False
    return True

# check if any of the fields in the dictionary is not greater than the target number
def greater_than(response, field_dict, num_target, process_name = ""):
    for key, value in field_dict.items():
        if value <= num_target:
            response.put( "status_code" ,  config.G_STATUS["NOT_GREATER_THAN"]['CODE']                          )
            response.put( "status"      ,  _process_name(response, process_name)                                )
            response.put( "desc"        ,  "The field '{0}' should be greater than {1}".format(key, num_target) )
            return False
    return True

# check if any of the fields in the dictionary is not less than the target number
def less_than(response, field_dict, num_target, process_name = ""):
    for key, value in field_dict.items():
        if value >= num_target:
            response.put( "status_code" ,  config.G_STATUS["NOT_LESS_THAN"]['CODE']                         )
            response.put( "status"      ,  _process_name(response, process_name)                            )
            response.put( "desc"        ,  "The field '{0}' should be less than {1}".format(key, num_target))
            return False
    return True

def language_supported(response, language_code, languages, process_name = ""):
    if language_code not in languages:
        response.put( "status_code" ,  config.G_STATUS["LANGUAGE_NOT_VALID"]['CODE']                            )
        response.put( "status"      ,  _process_name(response, process_name)                                    )
        response.put( "desc"        ,  "Language code provided ({}) not valid / supported.".format(language_code))
        return False
    return True
    
def _allowed_file(filename, extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions

def is_image(response, field_dict, process_name = ""):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'apng', 'avif', 'jfif', 'pjpeg', 'pjp', 'svg', 'webp', 'bmp', 'ico', 'cur'}
    for key, value in field_dict.items():
        print(value)
        if type(value) != str or _allowed_file(value, allowed_extensions) == False:
            response.put( "status_code" ,  config.G_STATUS["NOT_IMAGE"]['CODE']             )
            response.put( "status"      ,  _process_name(response, process_name)            )
            response.put( "desc"        ,  "The field '{}' should be an image".format(key)  )
            return False
    return True
