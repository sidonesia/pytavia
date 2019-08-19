import database

class bulk_db_insert:

    insert_list = []
    db_handle   = None

    def __init__(self, params):
        self.db_handle   = params["db_handle"]
        self.webapp      = params["app"]
        self.insert_list = []
    # end def

    def add( self, insert_item ):
        self.insert_list.append( insert_item )
    # end def

    def execute(self, params):
        with self.db_handle.start_session() as lock:
            lock.start_transaction()
            for record in self.insert_list:
                record.insert( lock )
            # end for
            lock.commit_transaction()
        # end with
    # end def
# end class
