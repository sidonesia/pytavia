import time
import sys

class pytavia_event_loop:


    def __init__(self, params):
        pass
    # end def

    def execute(self, params):
        action_time = int(time.time() * 1000)
        print (
            "[event_loop_proc(): execute periodic tasks @ " + str( action_time )  + "]"
        )
        sys.stdout.flush()
        sys.stderr.flush()
    # end def
# end class
