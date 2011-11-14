# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Local libs
from xml2rfc.writers.paginated_txt import PaginatedTextRfcWriter
from xml2rfc.writers.raw_txt import RawTextRfcWriter
from compiler.pyassem import RAW
import textwrap


class NroffRfcWriter(PaginatedTextRfcWriter):
    """ Writes to an nroff formatted file

        The page width is controlled by the *width* parameter.
    """

    default_header = ['.pl 10.0i',      # Page length
                      '.po 0',          # Page offset
                      '.ll 7.2i',       # Line length
                      '.lt 7.2i',       # Title length
                      '.nr LL 7.2i',    # Printer line length
                      '.nr LT 7.2i',    # Printer title length
                      '.hy 0',          # Disable hyphenation
                      '.ad l',          # Left margin adjustment only
                      ]

    def __init__(self, xmlrfc, width=72, quiet=False, verbose=False):
        PaginatedTextRfcWriter.__init__(self, xmlrfc, width=width, \
                                        quiet=quiet, verbose=verbose)
        self.curr_indent = 0    # Used like a state machine to control
                                # whether or not we print a .in command

    def _indent(self, amount):
        # Writes an indent command if it differs from the last
        if amount != self.curr_indent:
            self._write_line('.in ' + str(amount))
            self.curr_indent = amount

    # Override
    def _vspace(self, num=0):
        """ nroff uses a .sp command in addition to a literal blank line """
        self._write_line('.sp %s' % num)
        return self._lb(num=num)

    def _write_line(self, string):
        # Used by nroff to write a line with no nroff commands
        self.buf.append(string)

    # Override
    def _write_text(self, string, indent=0, sub_indent=0, bullet='',
                    align='left', lb=False, buf=None, strip=True, edit=False):
        #-------------------------------------------------------------
        # RawTextRfcWriter override
        #
        # We should be able to handle mostly all of the nroff commands by
        # intercepting the alignment and indentation arguments
        #-------------------------------------------------------------
        if not buf:
            buf = self.buf

        # Store buffer position for paging information
        begin = len(self.buf)

        if lb:
            if edit and self.pis.get('editing', 'no') == 'yes':
                # Render an editing mark
                self.edit_counter += 1
                self._lb(buf=buf, text=str('<' + str(self.edit_counter) + '>'))
            else:
                self._lb(buf=buf)
        if string:
            if strip:
                # Strip initial whitespace
                string = string.lstrip()
            if bullet:
                string = bullet + string
            par = self.wrapper.wrap(string)
            # TODO: Nroff alignment
            # Use bullet for indentation if sub not specified
            full_indent = sub_indent and indent + sub_indent or indent + len(bullet)
            self._indent(full_indent)
            if len(bullet) > 0:
                # Bullet line: title just uses base indent
                self._write_line('.ti ' + str(indent))
            buf.extend(par)

        # Page break information
        end = len(self.buf)
        self.break_hints[begin] = end - begin

        """
        elif bullet:
            # If the string is empty but a bullet was declared, just
            # print the bullet
            buf.append(initial)
        """

    def _post_write_toc(self, tmpbuf):
        # Wrap a nofill/fill block around TOC
        tmpbuf.append('.ti 0')
        tmpbuf.append('Table of Contents')
        tmpbuf.append('')
        tmpbuf.append('.in 3')
        tmpbuf.append('.nf')
        tmpbuf.extend(self.toc)
        tmpbuf.append('.fi')
        return tmpbuf

    # ---------------------------------------------------------
    # PaginatedTextRfcWriter overrides
    # ---------------------------------------------------------

    def write_title(self, text, docName=None):
        # Override to use .ti commands
        self._lb()
        if docName:
            self._write_line('.ce 2')
            self._write_line(text)
            self._write_line(docName)
        else:
            self._write_line('.ce 1')
            self._write_line(text)

    def write_raw(self, text, indent=3, align='left', blanklines=0, \
                  delimiter=None, lb=True):
        # Wrap in a no fill block
        self._indent(indent)
        self._write_line('.nf')
        PaginatedTextRfcWriter.write_raw(self, text, indent=0, align=align, \
                                         blanklines=blanklines, \
                                         delimiter=delimiter, lb=lb)
        self._write_line('.fi')

    def write_heading(self, text, bullet='', autoAnchor=None, anchor=None, \
                      level=1):
        # Override to use a .ti command
        self._lb()
        if bullet:
            bullet += '  '
        self._write_line('.ti 0')
        self._write_line(bullet + text)

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
        self._write_line('.ds RF FORMFEED[Page %]')

    def post_processing(self):
        """ Insert page break commands """

        # Write buffer to secondary buffer, inserting breaks every 58 lines
        page_len = 0
        page_maxlen = 55
        for line_num, line in enumerate(self.buf):
            if line_num in self.break_hints:
                # If this section will exceed a page, insert a break command
                if page_len + self.break_hints[line_num] > page_maxlen and \
                    self.pis.get('autobreaks', 'yes') == 'yes':
                    self.output.append('.bp')
                    page_len = 0
            if page_len + 1 > 55:
                self.output.append('.bp')
                page_len = 0
            self.output.append(line)
            page_len += 1