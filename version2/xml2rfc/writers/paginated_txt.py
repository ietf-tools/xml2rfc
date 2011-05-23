# Local libs
from raw_txt import RawTextRfcWriter
from base import XmlRfcWriter
import tools


class PaginatedTextRfcWriter(RawTextRfcWriter):
    """ Writes to a text file, paginated with headers and footers """

    def __init__(self, xmlrfc):
        RawTextRfcWriter.__init__(self, xmlrfc)
        self.left_header = ''
        self.center_header = ''
        self.right_header = ''
        self.left_footer = ''
        self.center_footer = ''
        self.section_marks = {}
        self.paged_buf = []

    def make_footer(self, page):
        return tools.justify_inline(self.left_footer, self.center_footer, \
                                    '[Page ' + str(page) + ']')

    # Here we override some methods to mark line numbers for large sections.
    # We'll store each marking as a hash of line_num: section_length.  This way
    # we can step through these markings during writing to preemptively
    # construct appropriate page breaks.
    def _write_figure(self, figure):
        """ Override base writer to add a marking """
        begin = len(self.buf)
        XmlRfcWriter._write_figure(self, figure)
        end = len(self.buf)
        self.section_marks[begin] = end - begin

    def pre_processing(self):
        """ Prepares the header and footer information """

        if 'number' in self.r.attrib:
            self.left_header = self.r.attrib['number']
        else:
            # No RFC number -- assume internet draft
            self.left_header = 'Internet-Draft'
        title = self.r.find('front/title')
        if 'abbrev' in title.attrib:
            self.center_header = title.attrib['abbrev']
        else:
            # No abbreviated title -- assume original title fits
            self.center_header = title.text
        date = self.r.find('front/date')
        if 'month' in date.attrib:
            self.right_header = date.attrib['month'] + ' '
        self.right_header += date.attrib['year']
        authors = self.r.findall('front/author')
        for i, author in enumerate(authors):
            # Author1, author2 & author3 OR author1 & author2 OR author1
            if i < len(authors) - 2:
                self.left_footer += author.attrib['surname'] + ', '
            elif i == len(authors) - 2:
                self.left_footer += author.attrib['surname'] + ' & '
            else:
                self.left_footer += author.attrib['surname']
        self.center_footer = self.r.attrib['category']

    def post_processing(self):
        """ Add paging information to a secondary buffer """

        # Construct header
        header = tools.justify_inline(self.left_header, self.center_header, \
                                      self.right_header)

        # Write buffer to secondary buffer, inserting breaks every 58 lines
        page_len = 0
        page_maxlen = 55
        page_num = 0
        for line_num, line in enumerate(self.buf):
            if line_num in self.section_marks:
                # If this section will exceed a page, insert blank lines
                # until the end of the page
                if page_len + self.section_marks[line_num] > page_maxlen:
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
