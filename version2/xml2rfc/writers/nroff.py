# Local libs
from xml2rfc.writers.paginated_txt import PaginatedTextRfcWriter
from xml2rfc.writers.raw_txt import RawTextRfcWriter


class NroffRfcWriter(PaginatedTextRfcWriter):
    """ Writes to an nroff file """

    default_header = ['.pl 10.0i',      # Page length
                      '.po 0',          # Page offset
                      '.ll 7.2i',       # Line length
                      '.lt 7.2i',       # Title length
                      '.nr LL 7.2i',    # Printer line length
                      '.nr LT 7.2i',    # Printer title length
                      '.hy 0',          # Disable hyphenation
                      '.ad l',          # Left margin adjustment only
                      ]

    def __init__(self, xmlrfc, **kwargs):
        PaginatedTextRfcWriter.__init__(self, xmlrfc, **kwargs)

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

    def write_t_rec(self, t, indent=3, sub_indent=0, bullet='', \
                    align='left', idstring=None):
        # Write with no indentation -- nroff commands are used instead
        self._write_line('.in ' + str(indent))
        PaginatedTextRfcWriter.write_t_rec(self, t, indent=0, sub_indent=0, \
                                           bullet=bullet, align=align, \
                                           idstring=idstring)

    def write_paragraph(self, text, align='left', idstring=None):
        # Write with no indentation -- nroff commands are used instead
        self._write_line('.in 3')
        self._write_par(text, indent=0, align='left', lb=True)

    def write_top(self, left_header, right_header):
        """ Writes the document header """
        # No fill for top section
        self._write_line('.nf')
        self._write_line('.in 0')
        PaginatedTextRfcWriter.write_top(self, left_header, right_header)
        self._write_line('.fi')

    def write_raw(self, text, align='left'):
        self._write_line('.nf')
        PaginatedTextRfcWriter.write_raw(self, text, align=align)
        self._write_line('.fi')

    def draw_table(self, table, table_num=None):
        self._write_line('.nf')
        PaginatedTextRfcWriter.draw_table(self, table, table_num=table_num)
        self._write_line('.fi')

    def pre_processing(self):
        """ Inserts an nroff header into the buffer """

        # Construct the RFC header and footer
        PaginatedTextRfcWriter.pre_processing(self)

        # Insert the standard nroff settings
        self.buf.extend(NroffRfcWriter.default_header)

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
