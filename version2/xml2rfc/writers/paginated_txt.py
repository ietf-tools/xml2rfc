# Local libs
from raw_txt import RawTextRfcWriter
import tools


class PaginatedTextRfcWriter(RawTextRfcWriter):
    """ Writes to a text file, paginated with headers and footers """
    
    def __init__(self, xmlrfc):
        RawTextRfcWriter.__init__(self, xmlrfc)
        self.header = ''
        self.left_footer = ''
        self.center_footer = ''
        self.section_marks = {}

    def make_footer(self, page):
        return tools.justify_inline(self.left_footer, self.center_footer, \
                                    '[Page ' + str(page) + ']')
        
    # Here we override some methods to mark line numbers for large sections.
    # We'll store each marking as a hash of line_num: section_length.  This way 
    # we can step through these markings during writing to preemptively 
    # construct appropriate page breaks.
    def write_figure(self, figure, table=False):
        begin = self.mark()
        RawTextRfcWriter.write_figure(self, figure, table)
        end = self.mark()
        self.section_marks[begin] = end-begin

    def write(self, filename):
        """ Public method to write rfc tree to a file """
        # Construct a header
        if 'number' in self.r.attrib:
            left_header = self.r.attrib['number']
        else:
            # No RFC number -- assume internet draft
            left_header = 'Internet-Draft'
        title = self.r.find('front/title')
        if 'abbrev' in title.attrib:
            center_header = title.attrib['abbrev']
        else:
            # No abbreviated title -- assume original title fits
            center_header = title.text
        right_header = ''
        date = self.r.find('front/date')
        if 'month' in date.attrib:
            right_header = date.attrib['month'] + ' '
        right_header += date.attrib['year']
        self.header = tools.justify_inline(left_header, center_header, \
                                           right_header)

        # Construct a footer
        self.left_footer = ''
        authors = self.r.findall('front/author')
        for i, author in enumerate(authors):
            # Format: author1, author2 & author3 OR author1 & author2 OR author1
            if i < len(authors) - 2:
                self.left_footer += author.attrib['surname'] + ', '
            elif i == len(authors) - 2:
                self.left_footer += author.attrib['surname'] + ' & '
            else:
                self.left_footer += author.attrib['surname']
        self.center_footer = self.r.attrib['category']

        # Write RFC to buffer
        self.write_buffer()

        # Write buffer to secondary buffer, inserting breaks every 58 lines
        newbuf = []
        page_len = 0
        page_maxlen = 55
        page_num = 0
        for line_num, line in enumerate(self.buf):
            if line_num in self.section_marks:
                # If this section will exceed a page, insert blank lines
                # until the end of the page
                if page_len + self.section_marks[line_num] > page_maxlen:
                    for i in range(page_maxlen - page_len):
                        newbuf.append('')
                        page_len += 1
            if page_len + 1 > 55:
                page_len = 0
                page_num += 1
                newbuf.append('')
                newbuf.append(self.make_footer(page_num))
                newbuf.append('\f')
                newbuf.append(self.header)
                newbuf.append('')
            newbuf.append(line)
            page_len += 1
                
        # Finally, write secondary buffer to file
        file = open(filename, 'w')
        for line in newbuf:
            file.write(line)
            file.write('\r\n')
        file.close()
