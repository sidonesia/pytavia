
import config
import database

class bulk_db_update:

    update_list = []
    db_handle   = None
    

    def __init__(self, params):
        self.db_handle   = params["db_handle"]
        self.webapp      = params["app"]
        self.update_list = []
    # end def

    def add( self, collection , query , update ):
        self.update_list.append({
            "collection" : collection,
            "query"      : query,
            "update"     : update
        })
    # end def

    def execute(self, params):
        with self.db_handle.start_session() as lock:
            lock.start_transaction()
            for record in self.update_list:
                collection = record["collection"]
                cmd_query  = record["query"]    
                cmd_update = record["update"]
                self.db_handle[config.mainDB][collection].update_one(
                    cmd_query , cmd_update, session=lock
                )
            # end for
            lock.commit_transaction()
        # end with
    # end def
# end class
