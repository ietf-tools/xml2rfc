# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Python libs
import datetime

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
    def write_raw(self, *args, **kwargs):
        """ Override text writer to add a marking """
        begin = len(self.buf)
        RawTextRfcWriter.write_raw(self, *args, **kwargs)
        end = len(self.buf)
        self.break_hints[begin] = (end - begin, "raw")

    def _write_text(self, *args, **kwargs):
        """ Override text writer to add a marking """
        begin = len(self.buf)
        RawTextRfcWriter._write_text(self, *args, **kwargs)
        end = len(self.buf)
        self.break_hints[begin] = (end - begin, "txt")
        
    def _force_break(self):
        """ Force a pagebreak at the current buffer position """
        self.break_hints[len(self.buf)] = (0, "break")
        
    def _toc_size_hint(self):
        return len(self._write_toc(paging=True))
    
    def _iref_size_hint(self):
        return len(self._write_iref_index())
    
    # ------------------------------------------------------------------------
    
    def write_heading(self, text, bullet='', autoAnchor=None, anchor=None, \
                      level=1):
        # Store the line number of this heading with its unique anchor, 
        # to later create paging info
        line_num = len(self.buf)
        self.heading_marks[line_num] = autoAnchor
        RawTextRfcWriter.write_heading(self, text, bullet=bullet, \
                                       autoAnchor=autoAnchor, anchor=anchor, \
                                       level=level)

    def pre_processing(self):
        """ Prepares the header and footer information """
        # Raw textwriters preprocessing will replace unicode with safe ascii
        RawTextRfcWriter.pre_processing(self)

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

    def post_processing(self):
        """ Add paging information to a secondary buffer """
        # Counters    
        current_page_length = 0
        current_page_number = 1
        max_page_length = 51

        def insertFooterAndHeader():
            self.output.append('')
            self.output.append('')
            self.output.append('')
            self.output.extend(self._make_footer_and_header(current_page_number))
            self.output.append('')
            self.output.append('')

        # Maintain a list of (start, end) pointers for elements to re-insert
        toc_pointers = []
        toc_prev_start = 0     
        iref_pointers = []
        iref_prev_start = 0

        for line_num, line in enumerate(self.buf):
            if line_num == self.toc_marker and self.toc_marker > 0:
                # Insert a dummy table of contents here
                toc_prev_start = len(self.output)
                for n in range(self._toc_size_hint()):
                    if current_page_length + 2 >= max_page_length:
                        # Store a pair of TOC pointers
                        toc_pointers.append((toc_prev_start, len(self.output)))
                        # New page
                        insertFooterAndHeader()
                        toc_prev_start = len(self.output)
                        # Update counters
                        current_page_length = 1
                        current_page_number += 1
                    # Write dummy line
                    self.output.append('')
                    current_page_length += 1
                # Store last pair of toc pointers
                toc_pointers.append((toc_prev_start, len(self.output)))
                
            if line_num == self.iref_marker and self.iref_marker > 0:
                # Add page number for index
                item = self._getItemByAnchor('rfc.index')
                if item:
                    item.page = current_page_number
                # Insert a dummy iref here
                iref_prev_start = len(self.output)
                for n in range(self._iref_size_hint()):
                    if current_page_length + 2 >= max_page_length:
                        # Store a pair of pointers
                        iref_pointers.append((iref_prev_start, len(self.output)))
                        # New page
                        insertFooterAndHeader()
                        iref_prev_start = len(self.output)
                        # Update counters
                        current_page_length = 1
                        current_page_number += 1
                    # Write dummy line
                    self.output.append('')
                    current_page_length += 1
                # Store last pair of pointers
                iref_pointers.append((iref_prev_start, len(self.output)))

            if line_num in self.break_hints:
                # If this size hint exceeds the rest of the page, or is set
                # to -1 (a forced break), insert a break.

                available = max_page_length - (current_page_length + 2)
                needed, text_type = self.break_hints[line_num]

                if line.strip() == "":
                    # discount initial blank line in what we're about to
                    # write when considering whether we're about to create
                    # orphans or widows
                    available -= 1
                    needed -= 1

                if (text_type == "break"
                    or (text_type == "raw" and needed > available and needed < max_page_length-2 )
                    or (self.pis.get('autobreaks', 'yes') == 'yes'
                        and needed > available
                        and needed < max_page_length-2
                        and (needed-available < 2 or available < 2) ) ):

                    # Insert break
                    remainder = max_page_length - current_page_length - 2
                    self.output.extend([''] * remainder)
                    current_page_length += remainder

            if current_page_length + 2 >= max_page_length:
                # New page
                insertFooterAndHeader()
                # Update counters -- done this way to preserve scope without reassigning
                current_page_length = 1
                current_page_number += 1
  
            # Write the line if it's not a blank line at the top of the page
            if not (line.strip() == "" and current_page_length == 1):
                self.output.append(line)
                current_page_length += 1

            # Store page numbers for any marked elements
            if line_num in self.heading_marks:
                item = self._getItemByAnchor(self.heading_marks[line_num])
                if item:
                    item.page = current_page_number
            if line_num in self.iref_marks:
                for item, subitem in self.iref_marks[line_num]:
                    # Store pages in item unless there are subitems
                    if subitem:
                        self._iref_index[item].subitems[subitem].\
                        pages.append(current_page_number)
                    else:
                        self._iref_index[item].\
                        pages.append(current_page_number)

        # Write final footer
        remainder = max_page_length - current_page_length
        self.output.extend([''] * remainder)
        self.output.extend(self._make_footer_and_header(current_page_number,
                                                             final=True))
        
        # Now we need to go back into the buffer and insert the real table 
        # of contents and iref based on the pointers we created
        if len(toc_pointers) > 0:
            tocbuf = self._write_toc(paging=True)
            ptr, end = toc_pointers.pop(0)
            for line in tocbuf:
                self.output[ptr] = line
                ptr += 1
                if ptr >= end:
                    if len(toc_pointers) > 0:
                        ptr, end = toc_pointers.pop(0)
                    else:
                        break

        if len(iref_pointers) > 0:
            irefbuf = self._write_iref_index()
            ptr, end = iref_pointers.pop(0)
            for line in irefbuf:
                self.output[ptr] = line
                ptr += 1
                if ptr >= end:
                    if len(iref_pointers) > 0:
                        ptr, end = iref_pointers.pop(0)
                    else:
                        break
