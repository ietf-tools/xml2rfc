# Local libs
from paginated_txt import PaginatedTextRfcWriter

default_header = ['.pl 10.0i',      # Page length
                  '.po 0',          # Page offset
                  '.ll 7.2i',       # Line length
                  '.lt 7.2i',       # Title length
                  '.nr LL 7.2i',    # Printer line length
                  '.nr LT 7.2i',    # Printer title length
                  '.hy 0',          # Disable hyphenation
                  '.ad l',          # Left margin adjustment only
                  ]

class NroffRfcWriter(PaginatedTextRfcWriter):
    """ Writes to an nroff file """
    
    def __init__(self, xmlrfc):
        PaginatedTextRfcWriter.__init__(self, xmlrfc)
        
    # ---------------------------------------------------------
    # PaginatedTextRfcWriter overrides
    # ---------------------------------------------------------

    def pre_processing(self):
        """ Inserts an nroff header into the buffer """

        # Construct the RFC header and footer
        PaginatedTextRfcWriter.pre_processing(self)
        
        # Insert the standard nroff settings
        self.buf.extend(default_header)
        
        # Insert the RFC header and footer information
        self._write_line('.ds LH ' + self.left_header, lb=False)
        self._write_line('.ds CH ' + self.center_header, lb=False)
        self._write_line('.ds RH ' + self.right_header, lb=False)
        self._write_line('.ds LF ' + self.left_footer, lb=False)
        self._write_line('.ds CF ' + self.center_footer, lb=False)
        self._write_line('.ds RF FORMFEED[Page] % ', lb=False)
        
        
        