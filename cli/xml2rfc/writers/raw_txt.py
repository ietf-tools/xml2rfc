# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Python libs
import os
import textwrap
import string
import math
import lxml
import datetime
import re
try:
    import debug
except ImportError:
    pass

# Local lib
from xml2rfc.writers.base import BaseRfcWriter
import xml2rfc.utils


class RawTextRfcWriter(BaseRfcWriter):
    """ Writes to a text file, unpaginated, no headers or footers.

        The page width is controlled by the *width* parameter.
    """

    def __init__(self, xmlrfc, width=72, margin=3, quiet=False, verbose=False, date=datetime.date.today()):
        BaseRfcWriter.__init__(self, xmlrfc, quiet=quiet, verbose=verbose, date=date)
        # Document processing data
        self.width = width      # Page width
        self.margin = margin    # Page margin
        self.buf = []           # Main buffer during processing
        self.output = []        # Final buffer that gets written to disk
        self.toc_marker = 0     # Line number in buffer to write toc to
        self.iref_marker = 0    # Line number in buffer to write index to
        self.list_counters = {} # Maintain counters for 'format' type lists
        self.edit_counter = 0   # Counter for edit marks
        self.eref_counter = 0   # Counter for <eref> elements
        self.ascii = True       # Enable ascii flag

        # Marks position of iref elements
        self.iref_marks = {}

        # Text lookups
        self.list_symbols = self.pis['text-list-symbols']
        self.inline_tags = ['xref', 'eref', 'iref', 'cref', 'spanx']
        
        # Custom textwrapper object
        self.wrapper = xml2rfc.utils.MyTextWrapper(width=self.width,
                                                   fix_sentence_endings=True)

    def _lb(self, buf=None, text='', num=1):
        """ Write a blank line to the file, with optional filler text 
        
            Filler text is usually used by editing marks
        """
        if num > 0:
            if not buf:
                buf = self.buf
            buf.extend([text] * num)

    def _vspace(self, num=0):
        """ <vspace> line break wrapper to allow for overrides """
        return self._lb(num=num)

    def write_text(self, string, indent=0, sub_indent=0, bullet='',
                  align='left', leading_blankline=False, buf=None,
                  strip=True, edit=False, wrap_urls=True,
                  fix_sentence_endings=True, source_line=None):
        """ Writes a line or multiple lines of text to the buffer.

            Several parameters are included here.  All of the API calls
            for text writers use this as the underlying method to write data
            to the buffer, with the exception of write_raw() that handles
            preserving of whitespace.
        """
        if buf is None:
            buf = self.buf

        if leading_blankline:
            if edit and self.pis['editing'] == 'yes':
                # Render an editing mark
                self.edit_counter += 1
                self._lb(buf=buf, text=str('<' + str(self.edit_counter) + '>'))
            else:
                self._lb(buf=buf)

        # We can take advantage of textwrap's initial_indent by using a bullet
        # parameter and treating it separately.  We still need to indent it.
        subsequent = ' ' * (indent + sub_indent)
        if bullet:
            initial = ' ' * indent
            bullet_parts = self.wrapper.wrap(bullet, initial_indent=initial, subsequent_indent=initial,
                                             fix_doublespace=False, drop_whitespace=False)
            if len(bullet_parts) > 1:
                buf.extend(bullet_parts[:-1])
            initial = bullet_parts[-1]
            if not sub_indent:
                # Use bullet length for subsequent indents
                subsequent = ' ' * len(initial)
        else:
            # No bullet, so combine indent and sub_indent
            initial = subsequent

        if string:
            if strip:
                # Strip initial whitespace
                string = string.lstrip()
            if wrap_urls:
                par = self.wrapper.wrap(string, initial_indent=initial, subsequent_indent=subsequent,
                                        fix_sentence_endings=fix_sentence_endings)
            else:
                par = self.wrapper.wrap(xml2rfc.utils.urlkeep(string), initial_indent=initial,
                                        subsequent_indent=subsequent, fix_sentence_endings=fix_sentence_endings)                    
            if align == 'left':
                buf.extend(par)
            elif align == 'center':
                for line in par:
                    margin = ' ' * (indent//2*2)
                    if line.startswith(margin):
                        centered = margin + line[len(margin):].center(self.width-(indent//2*2)).rstrip()
                        buf.append(centered)
                    else:
                        buf.append(line.center(self.width).rstrip())
            elif align == 'right':
                for line in par:
                    buf.append(line.rjust(self.width))
        elif bullet:
            # If the string is empty but a bullet was declared, just
            # print the bullet
            buf.append(initial)

    def write_list(self, list, level=0, indent=3):
        """ Writes a <list> element """
        bullet = '   '
        hangIndent = None
        # style comes from the node if one exists
        style = list.attrib.get('style', '')
        if not style:
            # otherwise look for the nearest list parent with a style and use it
            for parent in list.iterancestors():
                if parent.tag == 'list':
                    style = parent.attrib.get('style', '')
                    if style:
                        break
        if not style:
            style = 'empty'
        listlength = len(list.findall('t'))        
        if style == 'hanging' or style.startswith('format'):
            # Check for optional hangIndent
            try:
                hangIndent = int(list.attrib.get('hangIndent', 3+level*3))
            except (ValueError, TypeError):
                hangIndent = 3 + level*3
        format_str = None
        counter_index = None
        if style.startswith('format'):
            format_str = style.partition('format ')[2]
            allowed_formats = ('%c', '%C', '%d', '%i', '%I', '%o', '%x', '%X')
            if not any(map(lambda format: format in format_str, allowed_formats)):
                xml2rfc.log.warn('Invalid format specified: %s ' 
                                 '(Must be one of %s)' % (style,
                                    ', '.join(allowed_formats)))
            counter_index = list.attrib.get('counter', None)
            if not counter_index:
                counter_index = 'temp'
                self.list_counters[counter_index] = 0
            elif counter_index not in self.list_counters:
                # Initialize if we need to
                self.list_counters[counter_index] = 0
        t_count = 0
        for element in list:
            # Check for PI
            if element.tag is lxml.etree.PI:
                self.xmlrfc.parse_pi(element)
            elif element.tag == 't':
                # Disable linebreak if subcompact=yes AND not first list element
                leading_blankline = True
                if t_count > 0 and self.pis['subcompact'] == 'yes':
                    leading_blankline = False
                if style == 'symbols':
                    bullet = self.list_symbols[level % len(self.list_symbols)]
                    bullet += '  '
                elif style == 'numbers':
                    bullet = self._format_counter("%d.", t_count+1, listlength)
                elif style == 'letters':
                    bullet = self._format_counter("%c.", t_count+1, listlength)
                elif style == 'hanging':
                    bullet = element.attrib.get('hangText', '')
                    if len(bullet) < hangIndent:
                        # Insert whitespace up to hangIndent
                        bullet = bullet.ljust(hangIndent)
                    else:
                        # Insert a single space
                        bullet += '  '
                    # Add an extra space in front of colon if colonspace enabled
                    if bullet.endswith(':') and \
                    self.pis['colonspace'] == 'yes':
                        bullet+= ' '
                    if element.text and len(bullet) > self.width//2:
                        # extra check of remaining space if the bullet is
                        # very long
                        first_word = self.wrapper._split(element.text)[0]
                        if len(first_word) > (self.width - len(bullet) - indent):
                            self.write_text('', bullet=bullet, indent=indent,
                                leading_blankline=leading_blankline)
                            self._vspace()
                            leading_blankline=False
                            indent = hangIndent
                            bullet = ''
                elif style.startswith('format'):
                    self.list_counters[counter_index] += 1
                    count = self.list_counters[counter_index]
                    bullet = self._format_counter(format_str, count, listlength)
                if hangIndent:
                    sub_indent = hangIndent
                else:
                    sub_indent = len(bullet)
                self.write_t_rec(element, bullet=bullet, indent=indent, \
                                 level=level + 1, \
                                 sub_indent=sub_indent, leading_blankline=leading_blankline)
                t_count += 1

        
    def pre_write_toc(self):
        return ['', 'Table of Contents', '']

    def post_write_toc(self):
        return []

    def write_toc(self, paging=False):
        """ Write table of contents to a temporary buffer and return """
        if self.toc_marker < 1:
            # Toc is either disabled, or the pointer was messed up
            return ['']
        tmpbuf = []
        tmpbuf.extend(self.pre_write_toc())
        # Retrieve toc from the index
        tocindex = self._getTocIndex()
        tocdepth = self.pis['tocdepth']
        try:
            tocdepth = int(tocdepth)
        except ValueError:
            xml2rfc.log.warn('Invalid tocdepth specified, must be integer:', \
                             tocdepth)
            tocdepth = 3
        indent_scale = 2
        if self.pis['tocnarrow'] == 'no':
            indent_scale = 3
        for item in tocindex:
            # Add decoration to counter if it exists, otherwise leave empty
            if item.level <= tocdepth:
                counter = ''
                if item.counter:
                    counter = item.counter + '. '
                    # Extra space on single digit counters
                    if len(item.counter.rsplit('.')[-1]) == 1:
                        counter += ' '
                # Get item depth based on its section 'level' attribute
                depth = item.level - 1
                if depth < 0 or self.pis['tocindent'] == 'no':
                    depth = 0
                # Prepend appendix at first level
                if item.level == 1 and item.appendix:
                    counter = "Appendix " + counter
                bullet = ' ' * (depth * indent_scale) + counter
                indent = 3
                sub_indent = indent + len(bullet)
                pagestr = '%4s' % item.page
                lines = textwrap.wrap(bullet + item.title, 
                                      self.width - len(pagestr),
                                      initial_indent=' ' * indent,
                                      subsequent_indent=' ' * sub_indent)
                if paging:
                    # Construct dots
                    dots = len(lines[-1]) % 2 and ' ' or ''
                    dots += ' .' * int((self.width - len(lines[-1]) - len(dots) + 1)//2)
                    lines[-1] += dots
                    # Insert page
                    lines[-1] = lines[-1][:0 - len(pagestr)] + pagestr
                tmpbuf.extend(lines)
        tmpbuf.extend(self.post_write_toc())
        return tmpbuf
            
    def write_iref_index(self):
        """ Write iref index to a temporary buffer and return """
        if self.iref_marker < 1:
            # iref is either disabled, or the pointer was messed up
            return ['']
        tmpbuf = ['', 'Index']
        # Sort iref items alphabetically, store by first letter 
        alpha_bucket = {}
        for key in sorted(self._iref_index.keys()):
            letter = key[0].upper()
            if letter in alpha_bucket:
                alpha_bucket[letter].append(key)
            else:
                alpha_bucket[letter] = [key]
        for letter in sorted(alpha_bucket.keys()):
            # Write letter
            self.write_text(letter, indent=3, leading_blankline=True, buf=tmpbuf)
            for item in sorted(alpha_bucket[letter]):
                pages = self._iref_index[item].pages
                # Write item
                self.write_text(item + '  ' + ', '.join(map(str, pages))
                                                        , indent=6, buf=tmpbuf)
                for subitem in sorted(self._iref_index[item].subitems.keys()):
                    pages = self._iref_index[item].subitems[subitem].pages
                    # Write subitem
                    self.write_text(subitem + '  ' + ', '.join(map(str,pages))
                                                        , indent=9, buf=tmpbuf)
        return tmpbuf

    def _expand_xref(self, xref):
        """ Returns the proper text representation of an xref element """
        target = xref.attrib.get('target', '')
        format = xref.attrib.get('format', self.defaults['xref_format'])
        item = self._getItemByAnchor(target)
        if not item or format == 'none':
            target_text = '[' + target + ']'
        elif format == 'counter':
            target_text = item.counter
        elif format == 'title':
            target_text = item.title
        else: #Default
            target_text = item.autoName
        target_text = re.sub("([./-])", r"\1&#8288;", target_text)   # word joiner, to prevent line breaks
        if xref.text:
            if not target_text.startswith('['):
                target_text = '(' + target_text + ')'
            return xref.text.rstrip() + ' ' + target_text
        else:
            return target_text

    def write_ref_element(self, key, text, sub_indent, source_line=None):
        """ Render a single reference element """
        # Use an empty first line if key is too long
        min_spacing = 2
        if len(key) + min_spacing > sub_indent:
            self.write_text(key, indent=3, leading_blankline=True, wrap_urls=False, fix_sentence_endings=False, source_line=source_line)
            self.write_text(text, indent=3 + sub_indent, wrap_urls=False, fix_sentence_endings=False, source_line=source_line)
        else:
            # Fill space to sub_indent in the bullet
            self.write_text(text, indent=3, bullet=key.ljust(sub_indent), \
                     sub_indent=sub_indent, leading_blankline=True, wrap_urls=False, fix_sentence_endings=False, source_line=source_line)
    
    def _combine_inline_elements(self, elements):
        """ Shared function for <t> and <c> elements
        
            Aggregates all the rendered text of the following elements:
                - xref
                - eref
                - iref
                - cref
                - spanx
            
            Plus their tails.  If an element is encountered that isn't one
            of these (such as a list, figure, etc) then the function
            returns.
            
            This function takes a list of elements as its argument.
            
            This function returns TWO arguments, the aggregated text, and 
            a list containing the rest of the elements that were not processed,
            so that the calling function can deal with them.
        """
        line = ['']
        for i, element in enumerate(elements):
            # Check for a PI first
            if element.tag is lxml.etree.PI:
                self.xmlrfc.parse_pi(element)
            if element.tag not in self.inline_tags:
                # Not an inline element, exit
                return ''.join(line), elements[i:]

            if element.tag == 'xref':
                line.append(self._expand_xref(element))
            elif element.tag == 'eref':
                if element.text:
                    line.append(element.text + ' ')
                self.eref_counter += 1
                line.append('[' + str(self.eref_counter) + ']')
            elif element.tag == 'iref':
                item = element.attrib.get('item', None)
                if item:
                    subitem = element.attrib.get('subitem', None)
                    self._make_iref(item, subitem)
                    # Store the buffer position for pagination data later
                    pos = len(self.buf)
                    if pos not in self.iref_marks:
                        self.iref_marks[pos] = []
                    self.iref_marks[pos].append((item, subitem))
            elif element.tag == 'cref' and \
                self.pis['comments'] == 'yes':                
                # Render if processing instruction is enabled
                anchor = element.attrib.get('anchor', '')
                if anchor:
                    # TODO: Add anchor to index
                    anchor = ': ' + anchor
                if element.text:
                    line.append('[[' + anchor + element.text + ']]')
            elif element.tag == 'spanx':
                style = element.attrib.get('style', 'emph')
                edgechar = '?'
                if style == 'emph':
                    edgechar = '_'
                elif style == 'strong':
                    edgechar = '*'
                elif style == 'verb':
                    edgechar = '"'
                text = ''
                if element.text:
                    text = element.text
                line.append(edgechar + text + edgechar)
            
            # Add tail text before next element
            if element.tail:
                line.append(element.tail)

            # Go to next sibling
            element = element.getnext()

        # Went through all elements, return text with an empty list
        return ''.join(line), []
            
    def _check_long_lines(self, buf_line, source_line):
        long_lines = [ (num, line) for num, line in enumerate(self.buf[buf_line:]) if (len(line) > self.width) ]
        for num, line in long_lines:
            if source_line:
                xml2rfc.log.warn("Output line (from source around line %s) is %s characters; longer than %s.  Excess characters: '%s':\n  '%s'\n"
                    % (source_line+num, len(line), self.width, line[self.width:], line))
            else:
                xml2rfc.log.warn("Output line (from source around line %s) is %s characters; longer than %s.  Excess characters: '%s':\n  '%s'\n"
                    % (buf_line+num, len(line), self.width, line[self.width:], line))

    # ---------------------------------------------------------
    # Base writer overrides
    # ---------------------------------------------------------

    def insert_toc(self):
        """ Marks buffer position for post-writing table of contents """
        self.toc_marker = len(self.buf)
        
    def insert_iref_index(self):
        """ Marks buffer position for post-writing index """
        self.iref_marker = len(self.buf)

    def write_raw(self, text, indent=3, align='left', blanklines=0, \
                  delimiter=None, leading_blankline=True, source_line=None):
        """ Writes a raw stream of characters, preserving space and breaks """
        
        if text:
            if leading_blankline:
                # Start with a newline
                self._lb()
            # Delimiter?
            if delimiter:
                self.buf.append(delimiter)
            # Additional blank lines?
            self.buf.extend([''] * blanklines)
            start_line = len(self.buf)
            # Format the input
            lines = [line.rstrip() for line in text.expandtabs(4).split('\n')]
            # Trim first and last lines if they are blank, whitespace is handled
            # by the `blanklines` and `delimiter` arguments
            if len(lines) > 1:
                if lines[0] == '':
                    lines.pop(0)
                if lines[-1] == '':
                    lines.pop(-1)
            if align == 'center':
                # Find the longest line, and use that as a fixed center.
                longest_line = len(max(lines, key=len))
                center_indent = indent + ((self.width - indent - longest_line) // 2)
                indent_str = center_indent > indent and ' ' * center_indent or \
                                                        ' ' * indent
                for line in lines:
                    self.buf.append(indent_str + line)
            elif align == 'right':
                for line in lines:
                    self.buf.append(line.rjust(self.width))
            else:  # align == left
                # Enforce a minimum indentation if any of the lines are < indent
                extra = indent - \
                        min([len(line) - len(line.lstrip()) for line in lines])
                indent_str = extra > 0 and ' ' * extra or ''
                for line in lines:
                    self.buf.append(indent_str + line)
            # Additional blank lines?
            self.buf.extend([''] * blanklines)
            # Delimiter?
            if delimiter:
                self.buf.append(delimiter)
            if not self.indexmode:
                self._check_long_lines(start_line, source_line)

    def write_label(self, text, type='figure', source_line=None):
        """ Writes a centered label """
        self.write_text(text, indent=3, align='center', leading_blankline=True, source_line=source_line)

    def write_title(self, title, docName=None, source_line=None):
        """ Write the document title and (optional) name """
        self.write_text(title, leading_blankline=True, align='center', source_line=source_line)
        if docName:
            self.write_text(docName, align='center')

    def write_heading(self, text, bullet='', autoAnchor=None, anchor=None, \
                      level=1):
        """ Write a generic header """
        if bullet:
            bullet += '  '
        self.write_text(text, bullet=bullet, indent=0, leading_blankline=True)

    def write_paragraph(self, text, align='left', autoAnchor=None):
        """ Write a generic paragraph of text.  Used for boilerplate. """
        text = xml2rfc.utils.urlkeep(text)
        self.write_text(text, indent=3, align=align, leading_blankline=True)

    def write_t_rec(self, t, indent=3, sub_indent=0, bullet='',
                     autoAnchor=None, align='left', level=0, leading_blankline=True):
        """ Recursively writes a <t> element """
        # Grab any initial text in <t>
        current_text = t.text or ''
        
        # Render child elements
        remainder = t.getchildren()
        while len(remainder) > 0 or current_text:
            # Process any inline elements
            inline_text, remainder = self._combine_inline_elements(remainder)
            current_text += inline_text
            if (current_text and not current_text.isspace()) or bullet:
                # Attempt to write a paragraph of inline text
                self.write_text(current_text, indent=indent,
                                leading_blankline=leading_blankline,
                                sub_indent=sub_indent, bullet=bullet,
                                edit=True, align=align, source_line=t.sourceline)
            # Clear text
            current_text = ''

            # Handle paragraph-based elements (list, figure, vspace)
            if len(remainder) > 0:
                # Get front element
                element = remainder.pop(0)

                if element.tag == 'list': 
                    if sub_indent > 0:
                        new_indent = sub_indent + indent
                    else:
                        new_indent = len(bullet) + indent
                    # Call sibling function to construct list
                    self.write_list(element, indent=new_indent, level=level)
                    # Auto-break for tail paragraph
                    leading_blankline = True
                    bullet = ''

                elif element.tag == 'figure':
                    self.write_figure(element)
                    # Auto-break for tail paragraph
                    leading_blankline = True
                    bullet = ''

                elif element.tag == 'vspace':
                    # Insert `blankLines` blank lines into document
                    self._vspace(num=int(element.attrib.get('blankLines',
                                         self.defaults['vspace_blanklines'])))
                    # Don't auto-break for tail paragraph
                    leading_blankline = False
                    # Keep indentation
                    bullet = ' ' * sub_indent

                # Set tail of element as input text of next paragraph
                if element.tail:
                    current_text = element.tail
                    

    def write_top(self, left_header, right_header):
        """ Combines left and right lists to write a document heading """
        # Begin with a blank line on the first page.  We'll add additional
        # blank lines at the top later, but those won't be counted as part
        # of the page linecount.
        #self._lb(num=3)
        self._lb()
        heading = []
        for i in range(max(len(left_header), len(right_header))):
            if i < len(left_header):
                left = left_header[i]
            else:
                left = ''
            if i < len(right_header):
                right = right_header[i]
            else:
                right = ''
            heading.append(xml2rfc.utils.justify_inline(left, '', right, \
                                                        self.width))
        self.write_raw('\n'.join(heading), align='left', indent=0,
                        leading_blankline=False, source_line=None)
        # Extra blank line underneath top block
        self._lb()

    def write_address_card(self, author):
        """ Writes a simple address card with no line breaks """
        lines = []
        if 'role' in author.attrib:
            lines.append("%s (%s)" % (author.attrib.get('fullname', ''),
                                      author.attrib.get('role', '')))
        else:
            lines.append(author.attrib.get('fullname', ''))
        organization = author.find('organization')
        if organization is not None and organization.text:
            lines.append(organization.text)
        address = author.find('address')
        if address is not None:
            postal = address.find('postal')
            if postal is not None:
                for street in postal.findall('street'):
                    if street.text:
                        lines.append(street.text)
                cityline = []
                city = postal.find('city')
                if city is not None and city.text:
                    cityline.append(city.text)
                region = postal.find('region')
                if region is not None and region.text:
                    if len(cityline) > 0: cityline.append(', ');
                    cityline.append(region.text)
                code = postal.find('code')
                if code is not None and code.text:
                    if len(cityline) > 0: cityline.append('  ');
                    cityline.append(code.text)
                if len(cityline) > 0:
                    lines.append(''.join(cityline))
                country = postal.find('country')
                if country is not None and country.text:
                    lines.append(country.text)
            lines.append('')
            phone = address.find('phone')
            if phone is not None and phone.text:
                lines.append('Phone: ' + phone.text)
            facsimile = address.find('facsimile')
            if facsimile is not None and facsimile.text:
                lines.append('Fax:   ' + facsimile.text)
            email = address.find('email')
            if email is not None and email.text:
                label = self.pis['rfcedstyle'] == 'yes' and 'EMail' or 'Email'
                lines.append('%s: %s' % (label, email.text))
            uri = address.find('uri')
            if uri is not None and uri.text:
                lines.append('URI:   ' + uri.text)
        self.write_raw('\n'.join(lines), indent=self.margin)
        self._lb()

    def write_reference_list(self, list):
        """ Writes a formatted list of <reference> elements """
        refdict = {}
        annotationdict = {}
        refkeys = []
        refsource = {}
        # [surname, initial.,] "title", (STD), (BCP), (RFC), (Month) Year.
        for i, ref in enumerate(list.findall('reference')):
            refstring = []
            authors = ref.findall('front/author')
            refstring.append(self._format_author_string(authors))
            refstring.append(', ')
            title = ref.find('front/title')
            if title is not None and title.text:
                refstring.append('"' + title.text + '", ')
            else:
                xml2rfc.log.warn('No title specified in reference',
                                 ref.attrib.get('anchor', ''))
            for seriesInfo in ref.findall('seriesInfo'):
                if seriesInfo.attrib['name'] == "Internet-Draft":
                    refstring.append(seriesInfo.attrib['value'] + ' (work in progress), ')
                else:
                    refstring.append(seriesInfo.attrib['name'] + ' ' +
                                     seriesInfo.attrib['value'] + ', ')
            date = ref.find('front/date')
            if date is not None:
                month = date.attrib.get('month', '')
                year = date.attrib.get('year', '')
                if month or year:
                    if month:
                        month += ' '
                    refstring.append(month + year)
            # Target?
            target = ref.attrib.get('target')
            if target:
                if not refstring[-1].endswith(', '):
                    refstring.append(', ')
                refstring.append('<' + target + '>')
            refstring.append('.')
            annotation = ref.find('annotation')
            # Use anchor or num depending on PI
            if self.pis['symrefs'] == 'yes':
                bullet = '[' + ref.attrib.get('anchor', str(i + self.ref_start)) + ']'
            else:
                bullet = '[' + str(i + self.ref_start) + ']'
            refdict[bullet] = ''.join(refstring)
            refsource[bullet] = ref.sourceline
            refkeys.append(bullet)
            # Add annotation if it exists to a separate dict
            if annotation is not None and annotation.text:
                # Render annotation as a separate paragraph
                annotationdict[bullet] = annotation.text
        self.ref_start += i + 1
        # Don't sort if we're doing numbered refs; they are already in
        # numeric order, and if we sort, they will be sorted alphabetically,
        # rather than numerically ... ( i.e., [10], [11], ... [19], [1], ... )
        if self.pis['sortrefs'] == 'yes' and self.pis['symrefs'] == 'yes' :
            refkeys = sorted(refkeys)
        # Hard coded indentation amount
        refindent = 11
        for key in refkeys:
            self.write_ref_element(key, refdict[key], refindent, source_line=refsource[key])
            # Render annotation as a separate paragraph
            if key in annotationdict:
                self.write_text(annotationdict[key], indent=refindent + 3,
                                 leading_blankline=True, source_line=refsource[key])

    def draw_table(self, table, table_num=None):
        # First construct a 2d matrix from the table
        matrix = []
        matrix.append([])
        row = 0
        column_aligns = []
        ttcol_width_attrs = []
        style = table.attrib.get('style', self.defaults['table_style'])        
        for ttcol in table.findall('ttcol'):
            column_aligns.append(ttcol.attrib.get('align',
                                                  self.defaults['ttcol_align']))
            ttcol_width_attrs.append(ttcol.attrib.get('width', ''))
            if ttcol.text:
                matrix[row].append(ttcol.text)
            else:
                matrix[row].append('')
        num_columns = len(matrix[0])
        for i, cell in enumerate(table.findall('c')):
            if i % num_columns == 0:
                # Insert blank row if PI 'compact' is 'no'
                if self.pis["compact"] == "no":
                    if (style == 'none' and row == 0) or (style in ['headers', 'full'] and row != 0):
                        row += 1
                        matrix.append(['']*num_columns)
                        pass
                row += 1
                matrix.append([])


            text = cell.text or ''
            if len(cell) > 0:
                # <c> has children, render their text and add to line
                inline_text, null = \
                    self._combine_inline_elements(cell.getchildren())
                text += inline_text
            text = self.wrapper.replace(text)
            matrix[row].append(text)

        # Get table style and determine maximum width of table
        if style == 'none':
            table_max_chars = self.width - 3
        elif style == 'headers':
            table_max_chars = self.width - 3 - num_columns + 1
        else:
            table_max_chars = self.width - 3 - 3 * num_columns - 1  # indent+border

        # Find the longest line and longest word in each column
        longest_lines = [0] * num_columns
        longest_words = [0] * num_columns
        for col in range(num_columns):
            for row in matrix:
                if col < len(row) and len(row[col]) > 0:  # Column exists
                    # Longest line
                    if len(row[col]) > longest_lines[col]:
                        longest_lines[col] = len(row[col])
                    # Longest word
                    word = max(row[col].split(), key=len)
                    if len(word) > longest_words[col]:
                        longest_words[col] = len(word)
        
        # If longest_lines sum exceeds max width, apply weighted algorithm
        if sum(longest_lines) > table_max_chars:
            # Determine weights for each column.  If any ttcol has a width attribute
            # then we can determine all weights based on that.  Otherwise, apply
            # a custom algorithm
            column_weights = [None] * num_columns
            for i, width in enumerate(ttcol_width_attrs):
                try:
                    int_width = int(width)
                    if 0 < int_width < 100:
                        column_weights[i] = int_width / 100.0
                except ValueError:
                    pass
            spec_weights = [ c for c in column_weights if c ]
            if 0 < len(spec_weights) < num_columns:
                # Use explicit weights and divvy remaining equally
                avg = (1 - sum(spec_weights)) //  num_columns - len(spec_weights)
                for i, weight in enumerate(column_weights):
                    if not weight:
                        column_weights[i] = avg
            elif len(spec_weights) == 0:
                # Determine weights programatically.  First, use the longest word of
                # each column as its minimum width.  If this sum exceeds max, cut
                # each column from high to low until they all fit, and use those as
                # weights.  Else, use longest_lines to fill in weights.
                lwtot = sum(longest_words)
                if lwtot > table_max_chars:
                    column_weights = [ float(l)/lwtot for l in longest_words ]
                else:
                    column_weights = [ float(l)/table_max_chars for l in longest_words ]
                    remainder = 1 - sum(column_weights)
                    for i, weight in enumerate(column_weights):
                        column_weights[i] += remainder * \
                                             (float(longest_lines[i]) / sum(longest_lines))
            else:
                # Weights given for all TTCOLs, nothing to do
                pass

            # Compile column widths and correct floating point error
            column_widths = [ int(w*table_max_chars) for w in column_weights ]
            while(sum(column_widths) < table_max_chars):
                broken = False
                for i, wordlen in enumerate(longest_words):
                    if (column_widths[i] - wordlen) % 2 == 1:
                        column_widths[i] += 1
                        broken = True
                        break
                if not broken:
                    column_widths[column_widths.index(min(column_widths))] += 1
        else:
            column_widths = longest_lines

        # Force any column widths that got set to 0 to 1, raise warning
        for i, width in enumerate(column_widths):
            if width < 1:
                column_widths[i] = 1
                xml2rfc.log.warn('Table column width was forced to 1 from 0,' \
                                 ' it may exceed the page width.')
        
        # Now construct the cells using textwrap against column_widths
        cell_lines = [
            [ textwrap.wrap(cell, column_widths[j]) or [''] for j, cell in enumerate(matrix[i]) ]
            for i in range(0, len(matrix))
        ]

        output = []
        # Create the border
        if style == 'none':
            pass
        elif style == 'headers':
            borderstring = []
            for i in range(num_columns):
                borderstring.append('-' * column_widths[i])
                borderstring.append(' ')
        else:
            borderstring = ['+']
            for i in range(num_columns):
                borderstring.append('-' * (column_widths[i] + 2))
                borderstring.append('+')
            output.append(''.join(borderstring))

        # Draw the table
        for i, cell_line in enumerate(cell_lines):
            if i==0 and cell_line==[['']]:
                continue
            # produce as many outpur rows as the number of wrapped
            # text lines in the cell with most lines, but at least 1
            for row in range(0, max(map(len, cell_line))):
                if style == 'headers' or style == 'none':
                    line = ['']
                else:
                    line = ['|']
                for col, cell in enumerate(cell_line):
                    align = column_aligns[col]
                    width = column_widths[col]
                    if row < len(cell):
                        if align == 'center':
                            text = cell[row].center(width)
                        elif align == 'right':
                            text = cell[row].rjust(width)
                        else:  # align == left
                            text = cell[row].ljust(width)
                        if style == 'headers' or style == 'none':
                            line.append(text)
                            line.append(' ')
                        else:
                            line.append(' ')
                            line.append(text)
                            line.append(' |')
                    else:
                        if style == 'headers' or style == 'none':
                            line.append(' ' * (column_widths[col] + 1))
                        else:
                            line.append(' ' * (column_widths[col] + 2) + '|')
                output.append(''.join(line))
            if style in ['headers', 'full']:
                if i == 0:
                    # This is the header row, append the header decoration
                    output.append(''.join(borderstring))
            if style in ['full']:
                if i == len(cell_lines)-1:
                    output.append(''.join(borderstring))
            if style in ['all']:
                output.append(''.join(borderstring))


        # Finally, write the table to the buffer with proper alignment
        align = table.attrib.get('align', 'center')
        self.write_raw('\n'.join(output), align=align, indent=self.margin,
                        source_line=table.sourceline)

    def insert_anchor(self, text):
        # No anchors for text
        pass

    def pre_indexing(self):
        pass

    def pre_rendering(self):
        # Discard buffer from indexing pass
        self.buf = []
        
        # Reset document counters from indexing pass
        self.list_counters = {}
        self.edit_counter = 0   # Counter for edit marks
        self.eref_counter = 0   # Counter for <eref> elements

    def post_rendering(self):
        # Insert the TOC and IREF into the main buffer
        self.output = self.buf[:self.toc_marker] + \
                      self.write_toc() + \
                      self.buf[self.toc_marker:self.iref_marker] + \
                      self.write_iref_index() + \
                      self.buf[self.iref_marker:]

    def write_to_file(self, file):
        """ Writes the buffer to the specified file """
        # write initial blank lines, not counted against page size...
        if self.draft:
            file.write("\n"*3)
        else:
            file.write("\n"*6)
        for line in self.output:
            file.write(line.rstrip(" \t"))
            file.write("\n")
