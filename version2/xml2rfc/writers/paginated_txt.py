# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Local libs
from xml2rfc.writers.raw_txt import RawTextRfcWriter
from xml2rfc.writers.base import BaseRfcWriter
import xml2rfc.utils


class PaginatedTextRfcWriter(RawTextRfcWriter):
    """ Writes to a text file, paginated with headers and footers

        The page width is controlled by the *width* parameter.
    """

    def __init__(self, xmlrfc, width=72, quiet=False, verbose=False):
        RawTextRfcWriter.__init__(self, xmlrfc, width=width, quiet=quiet, \
                                  verbose=verbose)
        self.left_header = ''
        self.center_header = ''
        self.right_header = ''
        self.left_footer = ''
        self.center_footer = ''
        self.section_marks = {}
        self.paged_buf = []

    def make_footer(self, page):
        return xml2rfc.utils.justify_inline(self.left_footer, \
                                            self.center_footer, \
                                            '[Page ' + str(page) + ']')

    # Here we override some methods to mark line numbers for large sections.
    # We'll store each marking as a hash of line_num: section_length.  This way
    # we can step through these markings during writing to preemptively
    # construct appropriate page breaks.
    def write_raw(self, *args, **kwargs):
        """ Override text writer to add a marking """
        begin = len(self.buf)
        RawTextRfcWriter.write_raw(self, *args, **kwargs)
        end = len(self.buf)
        self.section_marks[begin] = end - begin

    def _write_text(self, *args, **kwargs):
        """ Override text writer to add a marking """
        begin = len(self.buf)
        RawTextRfcWriter._write_text(self, *args, **kwargs)
        end = len(self.buf)
        self.section_marks[begin] = end - begin
    # ------------------------------------------------------------------------

    def pre_processing(self):
        """ Prepares the header and footer information """
        RawTextRfcWriter.pre_processing(self)

        if 'number' in self.r.attrib:
            self.left_header = self.r.attrib['number']
        else:
            # No RFC number -- assume internet draft
            self.left_header = 'Internet-Draft'
        title = self.r.find('front/title')
        self.center_header = title.attrib.get('abbrev', title.text)
        date = self.r.find('front/date')
        month = date.attrib.get('month', '')
        year = date.attrib.get('year', '')
        self.right_header = month + ' ' + year
        authors = self.r.findall('front/author')
        for i, author in enumerate(authors):
            # Author1, author2 & author3 OR author1 & author2 OR author1
            surname = author.attrib.get('surname', '(surname)')
            if i < len(authors) - 2:
                self.left_footer += surname + ', '
            elif i == len(authors) - 2:
                self.left_footer += surname + ' & '
            else:
                self.left_footer += surname
        self.center_footer = self.r.attrib.get('category', '(Category)')

        # Check for PI override
        self.center_footer = self.pis.get('footer', self.center_footer)
        self.left_header = self.pis.get('header', self.left_header)

    def post_processing(self):
        """ Add paging information to a secondary buffer """

        # Construct header
        header = xml2rfc.utils.justify_inline(self.left_header, \
                                              self.center_header, \
                                              self.right_header)

        # Write buffer to secondary buffer, inserting breaks every 58 lines
        page_len = 0
        page_maxlen = 55
        page_num = 0
        for line_num, line in enumerate(self.buf):
            if line_num in self.section_marks:
                # If this section will exceed a page, force a page break by
                # inserting blank lines until the end of the page
                if page_len + self.section_marks[line_num] > page_maxlen and \
                    self.pis.get('autobreaks', 'yes') == 'yes':
                    for i in range(page_maxlen - page_len):
                        self.paged_buf.append('')
                        page_len += 1
            if page_len + 1 > 55:
                page_len = 0
                page_num += 1
                self.paged_buf.append('')
                self.paged_buf.append(self.make_footer(page_num))
                self.paged_buf.append('\f')
                self.paged_buf.append(header)
                self.paged_buf.append('')
            self.paged_buf.append(line)
            page_len += 1

    def write_to_file(self, filename):
        """ Override RawTextRfcWriter to use the paged buffer """
        file = open(filename, 'w')
        for line in self.paged_buf:
            file.write(line)
            file.write('\r\n')
        file.close()
