# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Python libs
import datetime
try:
    import debug
except ImportError:
    pass

# Local libs
from xml2rfc.writers.base import BaseRfcWriter
from xml2rfc.writers.raw_txt import RawTextRfcWriter
import xml2rfc.utils

class PaginatedTextRfcWriter(RawTextRfcWriter):
    """ Writes to a text file, paginated with headers and footers

        The page width is controlled by the *width* parameter.
    """

    def __init__(self, xmlrfc, width=72, quiet=False, verbose=False, date=datetime.date.today()):
        RawTextRfcWriter.__init__(self, xmlrfc, width=width, quiet=quiet, \
                                  verbose=verbose, date=date)
        self.left_header = ''
        self.center_header = ''
        self.right_header = ''
        self.left_footer = ''
        self.center_footer = ''
        self.break_hints = {}
        self.heading_marks = {}
        self.paged_toc_marker = 0
        self.page_line = 0

    def _make_footer_and_header(self, page, final=False):
        tmp = []
        tmp.append(xml2rfc.utils.justify_inline(self.left_footer,
                                                self.center_footer,
                                                '[Page ' + str(page) + ']'))
        if not final:
            tmp.append('\f')
            tmp.append(xml2rfc.utils.justify_inline(self.left_header,
                                                    self.center_header,
                                                    self.right_header))
        return tmp

    # Here we override some methods to mark line numbers for large sections.
    # We'll store each marking as a dictionary of line_num: section_length.
    # This way we can step through these markings during writing to
    # preemptively construct appropriate page breaks.
    def write_figure(self, *args, **kwargs):
        """ Override base writer to add a marking """
        begin = len(self.buf)
        BaseRfcWriter.write_figure(self, *args, **kwargs)
        end = len(self.buf)
        self.break_hints[begin] = (end - begin, "txt")

    def write_table(self, *args, **kwargs):
        """ Override base writer to add a marking """
        begin = len(self.buf)
        BaseRfcWriter.write_table(self, *args, **kwargs)
        end = len(self.buf)
        self.break_hints[begin] = (end - begin, "txt")

    def write_raw(self, *args, **kwargs):
        """ Override text writer to add a marking """
        begin = len(self.buf)
        RawTextRfcWriter.write_raw(self, *args, **kwargs)
        end = len(self.buf)
        self.break_hints[begin] = (end - begin, "raw")

    def write_text(self, *args, **kwargs):
        """ Override text writer to add a marking """
        begin = len(self.buf)
        RawTextRfcWriter.write_text(self, *args, **kwargs)
        end = len(self.buf)
        self.break_hints[begin] = (end - begin, "txt")
        
    def _force_break(self):
        """ Force a pagebreak at the current buffer position """
        self.break_hints[len(self.buf)] = (0, "break")
        
    def _toc_size_hint(self):
        return len(self.write_toc(paging=True))
    
    def _iref_size_hint(self):
        return len(self.write_iref_index())
    
    # ------------------------------------------------------------------------
    
    def write_heading(self, text, bullet='', autoAnchor=None, anchor=None, \
                      level=1):
        # Store the line number of this heading with its unique anchor, 
        # to later create paging info
        begin = len(self.buf)
        self.heading_marks[begin] = autoAnchor
        RawTextRfcWriter.write_heading(self, text, bullet=bullet, \
                                       autoAnchor=autoAnchor, anchor=anchor, \
                                       level=level)
        # Reserve room for a blankline and some lines of section content
        # text, in order to prevent orphan headings
        end = len(self.buf) + self.pis["sectionorphan"]
        self.break_hints[begin] = (end - begin, "txt")
                                        

    def pre_indexing(self):
        pass

    def pre_rendering(self):
        """ Prepares the header and footer information """
        # Raw textwriters preprocessing will replace unicode with safe ascii
        RawTextRfcWriter.pre_rendering(self)

        # Discard hints and marks from indexing pass
        self.break_hints = {}
        self.heading_marks = {}

        if self.draft:
            self.left_header = 'Internet-Draft'
        else:
            self.left_header = 'RFC %s' % self.r.attrib.get('number', '')
        title = self.r.find('front/title')
        if title is not None:
            self.center_header = title.attrib.get('abbrev', title.text)
        date = self.r.find('front/date')
        if date is not None:
            month = date.attrib.get('month', '')
            year = date.attrib.get('year', '')
            self.right_header = month + ' ' + year
        authors = self.r.findall('front/author')
        surnames = map(lambda author: author.attrib.get('surname', ''), authors)
        surnames = filter(lambda surname: bool(surname), surnames)
        if len(surnames) == 1:
            self.left_footer = surnames[0]
        elif len(surnames) == 2:
            self.left_footer = '%s & %s' % (surnames[0], surnames[1],)
        elif len(surnames) > 2:
            self.left_footer = '%s, et al.' % surnames[0]
        if self.draft:
            self.center_footer = 'Expires %s' % self.expire_string
        else:
            self.center_footer = self.boilerplate.get(
                                 self.r.attrib.get('category', ''), '(Category')

        # Check for PI override
        self.center_footer = self.pis.get('footer', self.center_footer)
        self.left_header = self.pis.get('header', self.left_header)

    def page_break(self, final=False):
        self.output.append('')
        self.output.append('')
        self.output.append('')
        self.output.extend(self._make_footer_and_header(self.page_num, final))
        if not final:
            self.output.append('')
            self.output.append('')
        self.page_length = 1
        self.page_num += 1

    def emit(self, text):
        """Write text to the output buffer if it's not just a blank
           line at the top of the page"""
        if self.page_length == 1 and text.strip() == '':
            return 
        if isinstance(text, basestring):
            self.output.append(text)
            self.page_length += 1
        elif isinstance(text, list):
            self.output.extend(text)
            self.page_length += len(text)
        else:
            raise TypeError("a string or a list of strings is required")

    def post_rendering(self):
        """ Add paging information to a secondary buffer """
        # Counters    
        self.page_length = 0
        self.page_num = 1
        max_page_length = 51


        # Maintain a list of (start, end) pointers for elements to re-insert
        toc_pointers = []
        toc_prev_start = 0     
        iref_pointers = []
        iref_prev_start = 0

        for line_num, line in enumerate(self.buf):
            if line_num == self.toc_marker and self.toc_marker > 0:
                # Don't start ToC too close to the end of the page
                if self.page_length + 10 >= max_page_length:
                    remainder = max_page_length - self.page_length - 2
                    self.emit([''] * remainder)
                    self.page_break()

                # Insert a dummy table of contents here
                toc_prev_start = len(self.output)
                preliminary_toc = self.write_toc(paging=True)
                for l in preliminary_toc:
                    if self.page_length + 2 >= max_page_length:
                        # Store a pair of TOC pointers
                        toc_pointers.append((toc_prev_start, len(self.output)))
                        # New page
                        self.page_break()
                        toc_prev_start = len(self.output)
                    # Write dummy line
                    self.emit(l)
                # Store last pair of toc pointers
                toc_pointers.append((toc_prev_start, len(self.output)))
                
            if line_num == self.iref_marker and self.iref_marker > 0:
                # Add page number for index
                item = self._getItemByAnchor('rfc.index')
                if item:
                    item.page = self.page_num
                # Insert a dummy iref here
                iref_prev_start = len(self.output)
                for n in range(self._iref_size_hint()):
                    if self.page_length + 2 >= max_page_length:
                        # Store a pair of pointers
                        iref_pointers.append((iref_prev_start, len(self.output)))
                        # New page
                        self.page_break()
                        iref_prev_start = len(self.output)
                    # Write dummy line
                    self.emit('')
                # Store last pair of pointers
                iref_pointers.append((iref_prev_start, len(self.output)))

            if line_num in self.break_hints:
                # If this size hint exceeds the rest of the page, or is set
                # to -1 (a forced break), insert a break.

                available = max_page_length - (self.page_length + 2)
                needed, text_type = self.break_hints[line_num]

                if line.strip() == "":
                    # discount initial blank line in what we're about to
                    # write when considering whether we're about to create
                    # orphans or widows
                    available -= 1
                    needed -= 1

                if (text_type == "break"
                    or (text_type == "raw" and needed > available and needed < max_page_length-2 )
                    or (self.pis['autobreaks'] == 'yes'
                        and needed > available
                        and needed < max_page_length-2
                        and (needed-available < 2 or available < 2) ) ):

                    # Insert break
                    remainder = max_page_length - self.page_length - 2
                    self.emit([''] * remainder)

            if self.page_length + 2 >= max_page_length:
                # New page
                self.page_break()

            self.emit(line)

            # Store page numbers for any marked elements
            if line_num in self.heading_marks:
                item = self._getItemByAnchor(self.heading_marks[line_num])
                if item:
                    item.page = self.page_num
            if line_num in self.iref_marks:
                for item, subitem in self.iref_marks[line_num]:
                    # Store pages in item unless there are subitems
                    if subitem:
                        self._iref_index[item].subitems[subitem].\
                        pages.append(self.page_num)
                    else:
                        self._iref_index[item].\
                        pages.append(self.page_num)

        # Write final footer
        remainder = max_page_length - self.page_length - 2
        self.emit([''] * remainder)
        self.page_break(final=True)
        
        # Now we need to go back into the buffer and insert the real table 
        # of contents and iref based on the pointers we created
        if len(toc_pointers) > 0:
            tocbuf = self.write_toc(paging=True)
            ptr, end = toc_pointers.pop(0)
            for line in tocbuf:
                if self.output[ptr] != '' and line == '':
                    continue
                self.output[ptr] = line
                ptr += 1
                if ptr >= end:
                    if len(toc_pointers) > 0:
                        ptr, end = toc_pointers.pop(0)
                    else:
                        break

        if len(iref_pointers) > 0:
            irefbuf = self.write_iref_index()
            ptr, end = iref_pointers.pop(0)
            for line in irefbuf:
                self.output[ptr] = line
                ptr += 1
                if ptr >= end:
                    if len(iref_pointers) > 0:
                        ptr, end = iref_pointers.pop(0)
                    else:
                        break
