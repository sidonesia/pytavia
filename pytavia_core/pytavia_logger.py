import logging
import sys

class pytavia_logger:

    logging_level = logging.INFO

    def __init__(self, params):

        self.log_file = params["file"]
        self.print_to = params["print_to"]

        self.logger   = logging.getLogger()
        self.handler  = logging.StreamHandler(sys.stdout)

        self.logger.setLevel  ( self.logging_level )
        self.handler.setLevel ( self.logging_level )

        formatter = logging.Formatter("%(asctime)s - %(message)s")
        self.handler.setFormatter  ( formatter    )
        self.logger.addHandler     ( self.handler )
    # end if

    def print_out(self, text):
        self.logger.info( text )
    # end def
# end class

