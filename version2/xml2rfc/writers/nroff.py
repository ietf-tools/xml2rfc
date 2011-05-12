# Local libs
from paginated_txt import PaginatedTextRfcWriter
from raw_txt import RawTextRfcWriter

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
    
    def write_label(self, text, type='figure'):
        """ Writes a label for a table or figure """
        self._write_line('.ce', lb=True)
        self._write_line(text)

    def write_title(self, text, docName=None):
        """ Writes the document title """
        self._lb()
        if docName:
            self._write_line('.ce 2')
            self._write_line(text)
            self._write_line(docName)
        else:
            self._write_line('.ce 1')
            self._write_line(text)
            
    def write_heading(self, text, bullet=None, idstring=None, anchor=None, \
                      level=1):
        self._write_line('.ti 0', lb=True)
        if bullet:
            self._write_line(bullet + ' ' + text)
        else:
            self._write_line(text)

    def write_top(self, left_header, right_header):
        """ Writes the document header """
        # No fill for top section
        self._write_line('.nf')  # Disable fill
        self._write_line('.in 0')
        PaginatedTextRfcWriter.write_top(self, left_header, right_header)
        self._write_line('.fi')  # Enable fill

    def pre_processing(self):
        """ Inserts an nroff header into the buffer """

        # Construct the RFC header and footer
        PaginatedTextRfcWriter.pre_processing(self)

        # Insert the standard nroff settings
        self.buf.extend(default_header)

        # Insert the RFC header and footer information
        self._write_line('.ds LH ' + self.left_header)
        self._write_line('.ds CH ' + self.center_header)
        self._write_line('.ds RH ' + self.right_header)
        self._write_line('.ds LF ' + self.left_footer)
        self._write_line('.ds CF ' + self.center_footer)
        self._write_line('.ds RF FORMFEED[Page] % ')

    def write_to_file(self, filename):
        # Use RawText's method instead of PaginatedText, so we dont get breaks.
        # Breaks are already handled by nroff commands
        RawTextRfcWriter.write_to_file(self, filename)
