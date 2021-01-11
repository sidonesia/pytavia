import sys
import traceback

sys.path.append("pytavia_core"    )
sys.path.append("pytavia_modules" )
sys.path.append("pytavia_settings")
sys.path.append("pytavia_stdlib"  )
sys.path.append("pytavia_storage" )

from pytavia_core   import database
from pytavia_core   import config
from pytavia_core   import helper
from pytavia_core   import bulk_db_action
from pytavia_stdlib import utils
from pytavia_stdlib import validation

class generic_proc:

    mgdDB       = database.get_db_conn(config.mainDB)
    db_handle   = database.get_database(config.mainDB)

    def __init__(self, app):
        self.webapp = app
    # end def

    def archive(self, params):
        try:
            collection  = params["collection"]

            db_readable_name = database.get_readable_name(collection)
            process_name        = "ARCHIVE_" + db_readable_name.upper().replace(" ", "_")
            proc_success_status = process_name + "_SUCCESS"
            proc_failed_status  = process_name + "_FAILED" 
            response = helper.response_msg(
                status = proc_success_status,
                desc = "Archiving {} record successful.".format(db_readable_name),
                data = {}
            )

            #####   PAYLOAD     #####
            pkey        = params["pkey"]

            #####   VALIDATION  #####
            record = validation.find_one(response, self.db_handle, collection,
                { "pkey" : pkey }
            )
            if record == None:
                return response

            #####   DB OPERATION  #####
            timestamp, timestamp_str = utils._get_current_timestamp()

            bulk_action = bulk_db_action.bulk_db_action({
                "db_handle" : self.db_handle,
                "app"       : self.webapp
            })

            bulk_action.deep_update(
                collection, 
                {
                    "pkey"  : pkey
                }, 
                {
                    "$set" : {
                        "archived_timestamp"       : timestamp,
                        "archived_timestamp_str"   : timestamp_str
                    }
                }
            )

            bulk_action.execute({})

            #####   RESPONSE    #####
            record["archived_timestamp"     ] = timestamp
            record["archived_timestamp_str" ] = timestamp_str
            response.put( "status_code" , config.G_STATUS['SUCCESS']['CODE'] )
            response.put( "data", record )

        except :
            self.webapp.logger.debug (traceback.format_exc())
            response.put( "status_code" ,  config.G_STATUS['UNEXPECTED_ERROR']['CODE']  )
            response.put( "status"      ,  proc_failed_status                           )
            response.put( "desc"        ,  config.G_STATUS['UNEXPECTED_ERROR']['DESC']  )
        # end try
        return response
    # end def

    def restore(self, params):
        try:
            collection  = params["collection"]

            db_readable_name = database.get_readable_name(collection)
            process_name        = "RESTORE_" + db_readable_name.upper().replace(" ", "_")
            proc_success_status = process_name + "_SUCCESS"
            proc_failed_status  = process_name + "_FAILED" 
            response = helper.response_msg(
                status = proc_success_status,
                desc = "Restoring {} record successful.".format(db_readable_name),
                data = {}
            )

            #####   PAYLOAD     #####
            pkey        = params["pkey"]

            #####   VALIDATION  #####
            record = validation.find_one(response, self.db_handle, collection,
                { "pkey" : pkey }
            )
            if record == None:
                return response

            #####   DB OPERATION  #####
            timestamp, timestamp_str = utils._get_current_timestamp()

            bulk_action = bulk_db_action.bulk_db_action({
                "db_handle" : self.db_handle,
                "app"       : self.webapp
            })

            bulk_action.deep_update(
                collection, 
                {
                    "pkey"  : pkey
                }, 
                {
                    "$set" : {
                        "archived_timestamp"       : "",
                        "archived_timestamp_str"   : ""
                    }
                }
            )

            bulk_action.execute({})
            
            #####   RESPONSE    #####
            record["archived_timestamp"     ] = ""
            record["archived_timestamp_str" ] = ""
            response.put( "status_code" , config.G_STATUS['SUCCESS']['CODE'] )
            response.put( "data", record )

        except :
            self.webapp.logger.debug (traceback.format_exc())
            response.put( "status_code" ,  config.G_STATUS['UNEXPECTED_ERROR']['CODE']  )
            response.put( "status"      ,  proc_failed_status                           )
            response.put( "desc"        ,  config.G_STATUS['UNEXPECTED_ERROR']['DESC']  )
        # end try
        return response
    # end def

    def add_two_way_reference(self, params, return_record=False):
        try:
            main_collection     = params["main"]["collection"]
            sub_collection      = params["sub"]["collection"]

            main_db_readable_name   = database.get_readable_name(main_collection)
            sub_db_readable_name    = database.get_readable_name(sub_collection)

            main_process_name       = utils._to_process_name(main_db_readable_name)
            sub_process_name        = utils._to_process_name(sub_db_readable_name)

            process_name        = "ADD_REFERENCE_BETWEEN_{}_AND_{}".format(main_process_name, sub_process_name)
            proc_success_status = process_name + "_SUCCESS"
            proc_failed_status  = process_name + "_FAILED" 
            response = helper.response_msg(
                status = proc_success_status,
                desc = "Adding reference between {} and {} successful.".format(main_db_readable_name, sub_db_readable_name),
                data = {}
            )
            #####   PAYLOAD     #####
            main_record_pkey    = params["main"]["pkey"]
            sub_record_pkey     = params["sub"]["pkey"]

            #####   VALIDATION  #####
            main_rec = validation.find_one(response, self.db_handle, main_collection,
                { "pkey"       : main_record_pkey }
            )
            if main_rec == None:
                return response

            # ----------------------- #
            fk_sub_collection_key = utils._db_name_to_fk_name(sub_collection)
            reference_found, reference = validation.no_reference(response, main_rec, fk_sub_collection_key, sub_record_pkey)
            if reference_found:
                return response

            # ----------------------- #
            sub_rec = validation.find_one(response, self.db_handle, sub_collection,
                { "pkey"       : sub_record_pkey }
            )
            if sub_rec == None:
                return response

            # ----------------------- #
            fk_main_collection_key = utils._db_name_to_fk_name(main_collection)
            reference_found, reference = validation.no_reference(response, sub_rec, fk_main_collection_key, main_record_pkey)
            if reference_found:
                return response

            #####   DB OPERATION  #####
            bulk_action = bulk_db_action.bulk_db_action({
                "db_handle" : self.db_handle,
                "app"       : self.webapp
            })

            bulk_action.two_way_reference(
                {
                    "collection"    : main_collection,
                    "record"        : main_rec
                },
                {
                    "collection"    : sub_collection,
                    "record"        : sub_rec
                }
            )

            bulk_action.execute({})

            #####   RESPONSE    #####
            main_response_name  = utils._db_name_to_response_name(main_collection)
            sub_response_name   = utils._db_name_to_response_name(sub_collection)

            if return_record:       # get updated records
                main_rec = validation.find_one(response, self.db_handle, main_collection,
                    { "pkey"       : main_record_pkey }
                )
                sub_rec = validation.find_one(response, self.db_handle, sub_collection,
                    { "pkey"       : sub_record_pkey }
                )
            else:
                main_rec = main_record_pkey
                sub_rec = sub_record_pkey

            response.put( "status_code" , config.G_STATUS['SUCCESS']['CODE'] )
            response.put( "data", {
                main_response_name  : main_rec,
                sub_response_name   : sub_rec,
            })

        except :
            self.webapp.logger.debug (traceback.format_exc())
            response.put( "status_code" ,  config.G_STATUS['UNEXPECTED_ERROR']['CODE']  )
            response.put( "status"      ,  proc_failed_status                           )
            response.put( "desc"        ,  config.G_STATUS['UNEXPECTED_ERROR']['DESC']  )
        # end try
        return response
    # end def

    def remove_two_way_reference(self, params, return_record=False):
        try:
            main_collection     = params["main"]["collection"]
            sub_collection      = params["sub"]["collection"]

            main_db_readable_name   = database.get_readable_name(main_collection)
            sub_db_readable_name    = database.get_readable_name(sub_collection)

            main_process_name       = utils._to_process_name(main_db_readable_name)
            sub_process_name        = utils._to_process_name(sub_db_readable_name)

            process_name        = "REMOVE_REFERENCE_BETWEEN_{}_AND_{}".format(main_process_name, sub_process_name)
            proc_success_status = process_name + "_SUCCESS"
            proc_failed_status  = process_name + "_FAILED" 
            response = helper.response_msg(
                status = proc_success_status,
                desc = "Removing reference between {} and {} successful.".format(main_db_readable_name, sub_db_readable_name),
                data = {}
            )
            #####   PAYLOAD     #####
            main_record_pkey    = params["main"]["pkey"]
            sub_record_pkey     = params["sub"]["pkey"]

            #####   VALIDATION  #####
            main_rec = validation.find_one(response, self.db_handle, main_collection,
                { "pkey"       : main_record_pkey }
            )
            if main_rec == None:
                return response

            # ----------------------- #
            fk_sub_collection_key = utils._db_name_to_fk_name(sub_collection)
            reference_found, reference = validation.find_reference(response, main_rec, fk_sub_collection_key, sub_record_pkey)
            if not reference_found:
                return response

            # ----------------------- #
            sub_rec = validation.find_one(response, self.db_handle, sub_collection,
                { "pkey"       : sub_record_pkey }
            )
            if sub_rec == None:
                return response

            # ----------------------- #
            fk_main_collection_key = utils._db_name_to_fk_name(main_collection)
            reference_found, reference = validation.find_reference(response, sub_rec, fk_main_collection_key, main_record_pkey)
            if not reference_found:
                return response

            #####   DB OPERATION  #####
            bulk_action = bulk_db_action.bulk_db_action({
                "db_handle" : self.db_handle,
                "app"       : self.webapp
            })

            bulk_action.remove_two_way_reference(
                {
                    "collection"    : main_collection,
                    "record"        : main_rec
                },
                {
                    "collection"    : sub_collection,
                    "record"        : sub_rec
                }
            )

            bulk_action.execute({})

            #####   RESPONSE    #####
            main_response_name  = utils._db_name_to_response_name(main_collection)
            sub_response_name   = utils._db_name_to_response_name(sub_collection)

            if return_record:       # get updated records
                main_rec = validation.find_one(response, self.db_handle, main_collection,
                    { "pkey"       : main_record_pkey }
                )
                sub_rec = validation.find_one(response, self.db_handle, sub_collection,
                    { "pkey"       : sub_record_pkey }
                )
            else:
                main_rec = main_record_pkey
                sub_rec = sub_record_pkey

            response.put( "status_code" , config.G_STATUS['SUCCESS']['CODE'] )
            response.put( "data", {
                main_response_name  : main_rec,
                sub_response_name   : sub_rec,
            })

        except :
            self.webapp.logger.debug (traceback.format_exc())
            response.put( "status_code" ,  config.G_STATUS['UNEXPECTED_ERROR']['CODE']  )
            response.put( "status"      ,  proc_failed_status                           )
            response.put( "desc"        ,  config.G_STATUS['UNEXPECTED_ERROR']['DESC']  )
        # end try
        return response
    # end def