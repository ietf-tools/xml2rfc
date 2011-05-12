# Local libs
from raw_txt import RawTextRfcWriter

default_header = ['.pl 10.0i',      # Page length
                  '.po 0',          # Page offset
                  '.ll 7.2i',       # Line length
                  '.lt 7.2i',       # Title length
                  '.nr LL 7.2i',    # Printer line length
                  '.nr LT 7.2i',    # Printer title length
                  ]

class NroffRfcWriter(RawTextRfcWriter):
    """ Writes to an nroff file """
    
    def __init__(self, xmlrfc):
        RawTextRfcWriter.__init__(self, xmlrfc)
        
    # ---------------------------------------------------------
    # RawTextRfcWriter overrides
    # ---------------------------------------------------------

    def pre_processing(self):
        """ Inserts the standard nroff header to the buffer """
        self.buf.extend(default_header)
