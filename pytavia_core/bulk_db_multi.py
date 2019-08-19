
import config
import database

ACTION_INSERT = "INSERT"
ACTION_DELETE = "DELETE"
ACTION_UPDATE = "UPDATE"

class bulk_db_multi:

    action_list = []
    db_handle   = None

    

    def __init__(self, params):
        self.db_handle   = params["db_handle"]
        self.webapp      = params["app"]
        self.action_list = []
    # end def

    def add_action( self, action ,collection , query=None , update=None ):
        self.action_list.append({
            "action"     : action,
            "collection" : collection,
            "query"      : query,
            "update"     : update
        })
    # end def

    def execute(self, params):
        with self.db_handle.start_session() as lock:
            lock.start_transaction()
            for record in self.action_list:
                action = record["action"]
                if action == ACTION_UPDATE:
                    collection = record["collection"]
                    cmd_query  = record["query"]    
                    cmd_update = record["update"]
                    self.db_handle[config.mainDB][collection].update_one(
                        cmd_query , cmd_update, session=lock
                    )
                elif action == ACTION_INSERT:
                    collection = record["collection"]
                    collection.insert()
                elif action == ACTION_DELETE:
                    collection = record["collection"]
                    cmd_query  = record["query"]    
                    self.db_handle[config.mainDB][collection].delete_one(
                        cmd_query , session=lock
                    )
                # end if
            # end for
            lock.commit_transaction()
        # end with
    # end def
# end class
