import time
import sys

class pytavia_event_handler:


    def __init__(self, params):
        pass
    # end def

    def event_handler_check(self):
        pass
    # end def

    def event_switch(self, event):
        operation_type   = event.get("action")
        handler_name     = event.get("handler_name")
        database_name    = event.get("db")
        collection_name  = event.get("collection")
        document_key     = event.get("rid")
        current_time     = int(time.time() * 1000)
        print (
            "[event_switch - " + handler_name + " - "+ str(current_time) + "] [" +\
                operation_type + "] [" + database_name + "] [" + collection_name +\
                "] [" + str(document_key) + "]"
        )
        sys.stdout.flush()
        sys.stderr.flush()
    # end def
# end class
