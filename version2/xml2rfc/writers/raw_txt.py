# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# Python libs
import textwrap
import string
import math

# Local lib
from xml2rfc.writers.base import BaseRfcWriter
import xml2rfc.utils


class RawTextRfcWriter(BaseRfcWriter):
    """ Writes to a text file, unpaginated, no headers or footers.

        The page width is controlled by the *width* parameter.
    """

    def __init__(self, xmlrfc, width=72, quiet=False, verbose=False):
        BaseRfcWriter.__init__(self, xmlrfc, quiet=quiet, verbose=verbose)
        self.width = width      # Page width
        self.buf = []           # Main buffer
        self.tocbuf = []        # Table of contents buffer
        self.toc_marker = 0     # Line number in buffer to write toc too
        self.list_counters = {} # Maintain counters for 'format' type lists
        self.edit_counter = 0   # Counter for edit marks
        self.eref_counter = 0   # Counter for <eref> elements

        self.list_symbols = self.pis.get('text-list-symbols', 'o*+-')
        self.inline_tags = ['xref', 'eref', 'iref', 'cref', 'spanx']

    def _lb(self, buf=None, text='', num=1):
        """ Write a blank line to the file, with optional filler text 
        
            Filler text is usually used by editing marks
        """
        if num > 0:
            if not buf:
                buf = self.buf
            buf.extend([text] * num)

    def _write_text(self, string, indent=0, sub_indent=0, bullet='', \
                  align='left', lb=False, buf=None, strip=True, edit=False):
        """ Writes a line or multiple lines of text to the buffer.

            Several parameters are included here.  All of the API calls
            for text writers use this as the underlying method to write data
            to the buffer, with the exception of write_raw() that handles
            preserving of whitespace.
        """
        if not buf:
            buf = self.buf
        # We can take advantage of textwraps initial_indent by using a bullet
        # parameter and treating it separately.  We still need to indent it.
        subsequent = ' ' * (indent + sub_indent)
        if bullet:
            initial = ' ' * indent + bullet
            if not sub_indent:
                # Use bullet length for subsequent indents
                subsequent = ' ' * len(initial)
        else:
            # No bullet, so combine indent and sub_indent
            initial = subsequent

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
            par = textwrap.wrap(string, self.width, \
                                initial_indent=initial, \
                                subsequent_indent=subsequent)
            if align == 'left':
                buf.extend(par)
            elif align == 'center':
                for line in par:
                    buf.append(line.center(self.width).rstrip())
            elif align == 'right':
                for line in par:
                    buf.append(line.rjust(self.width))
        elif bullet:
            # If the string is empty but a bullet was declared, just
            # print the bullet
            buf.append(initial)

    def _write_list(self, list, level=0, indent=3):
        """ Writes a <list> element """
        bullet = '   '
        hangIndent = None
        style = list.attrib.get('style', 'empty')
        # Check for optional hangIndent
        if style == 'hanging' or style.startswith('format'):
            hangIndent = list.attrib.get('hangIndent', 3)
        format_str = None
        counter_index = None
        if style.startswith('format'):
            format_str = style.partition('format ')[2]
            if not ('%c' in format_str or '%d' in format_str):
                xml2rfc.log.warn('No %c or %d found in list format '\
                                 'string: ' + style)
            counter_index = list.attrib.get('counter', None)
            if not counter_index:
                counter_index = 'temp'
                self.list_counters[counter_index] = 0
            elif counter_index not in self.list_counters:
                # Initialize if we need to
                self.list_counters[counter_index] = 0
        for i, t in enumerate(list.findall('t')):
            # Disable linebreak if subcompact=yes AND not first list element
            lb = True
            if i > 0 and self.pis.get('subcompact', \
                self.pis.get('compact', \
                self.pis.get('rfcedstyle', 'no'))) == 'yes':
                lb = False
            if style == 'symbols':
                bullet = self.list_symbols[level % len(self.list_symbols)]
                bullet += '  '
            elif style == 'numbers':
                bullet = str(i + 1) + '.  '
            elif style == 'letters':
                bullet = string.ascii_lowercase[i % 26] + '.  '
            elif style == 'hanging':
                bullet = t.attrib.get('hangText', '')
                # Add an extra space if there is a colon, and colonspace is on
                if bullet.endswith(':') and \
                self.pis.get('colonspace', 'no') == 'no':
                    bullet+= ' '
                else:
                    bullet += '  '
            elif style.startswith('format'):
                self.list_counters[counter_index] += 1
                count = self.list_counters[counter_index]
                if '%d' in format_str:
                    bullet = format_str.replace(r'%d', str(count) + ' ')
                elif '%c' in format_str:
                    bullet = format_str.replace(r'%c', \
                            str(string.ascii_lowercase[count % 26]) + ' ')
                else:
                    bullet = format_str
            if hangIndent:
                self.write_t_rec(t, bullet=bullet, indent=indent, \
                                 level=level + 1, \
                                 sub_indent=int(hangIndent), lb=lb)
            else:
                self.write_t_rec(t, bullet=bullet, indent=indent, \
                                 level=level + 1, lb=lb)

    def _write_toc(self, paging=False):
        # Write table of contents to a temporary buffer
        self.tocbuf.extend(['', 'Table of Contents', ''])
        # Retrieve toc from the index
        tocindex = self._getTocIndex()
        tocdepth = self.pis.get('tocdepth', '3')
        try:
            tocdepth = int(tocdepth)
        except ValueError:
            xml2rfc.log.warn('Invalid tocdepth specified, must be integer:', \
                             tocdepth)
            tocdepth = 3
        indent_scale = 2
        if self.pis.get('tocnarrow', 'yes') == 'no':
            indent_scale = 3
        for item in tocindex:
            # Add decoration to counter if it exists, otherwise leave empty
            counter = ''
            if item.counter:
                counter = item.counter + '. '
                # Extra space on single digit counters
                if len(item.counter.rsplit('.')[-1]) == 1:
                    counter += ' '
            # Get item depth based on its section 'level' attribute
            depth = item.level - 1
            if depth < 0 or self.pis.get('tocindent', 'yes') == 'no':
                depth = 0
            bullet = ' ' * (depth * indent_scale) + counter
            indent = 3
            sub_indent = indent + len(bullet)
            lines = textwrap.wrap(bullet + item.title, self.width, \
                                 initial_indent=' ' * indent, \
                                 subsequent_indent=' ' * sub_indent)
            if paging:
                # Construct dots
                dots = len(lines[-1]) % 2 and ' ' or '  '
                dots += '. ' * int((self.width - len(lines[-1]) - len(dots))/2)
                lines[-1] += dots
                # Insert page
                pagestr = ' ' + str(item.page)
                lines[-1] = lines[-1][:0 - len(pagestr)] + pagestr
            self.tocbuf.extend(lines)

    def _expand_xref(self, xref):
        """ Returns the proper text representation of an xref element """
        target = xref.attrib.get('target', '')
        format = xref.attrib.get('format', 'default')
        item = self._getItemByAnchor(target)
        if not item or format == 'none':
            target_text = '[' + target + ']'
        elif format == 'counter':
            target_text = item.counter
        elif format == 'title':
            target_text = item.title
        else: #Default
            target_text = item.autoName
        if xref.text:
            if not target_text.startswith('['):
                target_text = '(' + target_text + ')'
            return xref.text + ' ' + target_text
        else:
            return target_text

    def _write_ref_element(self, key, text, sub_indent):
        """ Render a single reference element """
        # Use an empty first line if key is too long
        min_spacing = 2
        if len(key) + min_spacing > sub_indent:
            self._write_text(key, indent=3, lb=True)
            self._write_text(text, indent=3 + sub_indent)
        else:
            # Fill space to sub_indent in the bullet
            self._write_text(text, indent=3, bullet=key.ljust(sub_indent), \
                     sub_indent=sub_indent, lb=True)
    
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
                # TODO iref
                pass
            elif element.tag == 'cref' and \
                self.pis.get('comments', 'no') == 'yes':                
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
                    edgechar = '-'
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
            
        

    # ---------------------------------------------------------
    # Base writer overrides
    # ---------------------------------------------------------

    def insert_toc(self):
        """ Marks buffer position for post-writing table of contents """
        self.toc_marker = len(self.buf)

    def write_raw(self, text, indent=3, align='left', blanklines=0, \
                  delimiter=None, lb=True):
        """ Writes a raw stream of characters, preserving space and breaks """
        if lb:
            # Start with a newline
            self._lb()
        # Delimiter?
        if delimiter:
            self.buf.append(delimiter)
        # Additional blank lines?
        self.buf.extend([''] * blanklines)
        # Format the input
        lines = [line.rstrip() for line in text.expandtabs(4).split('\n')]
        if align == 'center':
            # Find the longest line, and use that as a fixed center.
            longest_line = len(max(lines, key=len))
            center_indent = ((self.width - longest_line) / 2)
            indent_str = center_indent > indent and ' ' * center_indent or \
                                                    ' ' * indent
            for line in lines:
                self.buf.append(indent_str + line)
        elif align == 'right':
            for line in lines:
                self.buf.append(line.rjust(self.width))
        else:  # align == left
            indent_str = ' ' * indent
            for line in lines:
                self.buf.append(indent_str + line)
        # Additional blank lines?
        self.buf.extend([''] * blanklines)
        # Delimiter?
        if delimiter:
            self.buf.append(delimiter)

    def write_label(self, text, type='figure'):
        """ Writes a centered label """
        self._write_text(text, align='center', lb=True)

    def write_title(self, title, docName=None):
        """ Write the document title and (optional) name """
        self._write_text(title, lb=True, align='center')
        if docName is not None:
            self._write_text(docName, align='center')

    def write_heading(self, text, bullet='', autoAnchor=None, anchor=None, \
                      level=1):
        """ Write a generic header """
        if bullet:
            bullet += '  '
        self._write_text(text, bullet=bullet, indent=0, lb=True)

    def write_paragraph(self, text, align='left', autoAnchor=None):
        """ Write a generic paragraph of text """
        self._write_text(text, indent=3, align=align, lb=True)

    def write_t_rec(self, t, indent=3, sub_indent=0, bullet='', \
                     autoAnchor=None, align='left', level=0, lb=True):
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
                self._write_text(current_text, indent=indent, lb=lb, \
                                sub_indent=sub_indent, bullet=bullet, \
                                edit=True, align=align)
                
            # Reset settings after initial paragraph
            current_text = ''
            bullet = ''

            # Handle paragraph-based elements (list, figure, vspace)
            if len(remainder) > 0:
                # Get front element
                element = remainder.pop(0)

                if element.tag == 'list': 
                    # Calculate new indentation for list
                    if sub_indent > 0:
                        new_indent = sub_indent + indent
                    else:
                        new_indent = len(bullet) + indent
                    # Call sibling function to construct list
                    self._write_list(element, indent=new_indent, level=level)
                    # Auto-break for tail paragraph
                    lb = True

                elif element.tag == 'figure':
                    self._write_figure(element)
                    # Auto-break for tail paragraph
                    lb = True

                elif element.tag == 'vspace':
                    # Insert `blankLines` blank lines into document
                    self._lb(num=int(element.attrib.get('blankLines', 0)))
                    # Don't auto-break for tail paragraph
                    lb = False

                # Set tail of element as input text of next paragraph
                if element.tail:
                    current_text = element.tail

    def write_top(self, left_header, right_header):
        """ Combines left and right lists to write a document heading """
        # Begin with three blank lines
        self._lb(num=3)
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
        self.write_raw('\n'.join(heading), align='left', indent=0, lb=False)

    def write_address_card(self, author):
        """ Writes a simple address card with no line breaks """
        lines = []
        if 'role' in author.attrib:
                lines.append(author.attrib['fullname'] + ', ' + \
                             author.attrib['role'])
        else:
            lines.append(author.attrib['fullname'])
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
                        cityline.append(', ')
                region = postal.find('region')
                if region is not None and region.text:
                        cityline.append(region.text)
                        cityline.append(' ')
                code = postal.find('code')
                if code is not None and code.text:
                        cityline.append(code.text)
                if cityline is not None:
                    lines.append(''.join(cityline))
                country = postal.find('country')
                if country is not None and country.text:
                    lines.append(country.text)
            lines.append('')
            phone = address.find('phone')
            if phone is not None and phone.text:
                lines.append('Phone: ' + phone.text)
            fascimile = address.find('fascimile')
            if fascimile is not None and fascimile.text:
                lines.append('Fax:   ' + fascimile.text)
            email = address.find('email')
            if email is not None and email.text:
                lines.append('Email: ' + email.text)
            uri = address.find('uri')
            if uri is not None and uri.text:
                lines.append('URI:   ' + uri.text)
        self.write_raw('\n'.join(lines))
        self._lb()

    def write_reference_list(self, list):
        """ Writes a formatted list of <reference> elements """
        refdict = {}
        annotationdict = {}
        refkeys = []
        # [surname, initial.,] "title", (STD), (BCP), (RFC), (Month) Year.
        for i, ref in enumerate(list.findall('reference')):
            refstring = []
            authors = ref.findall('front/author')
            for j, author in enumerate(authors):
                organization = author.find('organization')
                surname = author.attrib.get('surname', '')
                if surname:
                    initials = author.attrib.get('initials', '')
                    if j == len(authors) - 1 and len(authors) > 1:
                        # Last author is rendered in reverse
                        refstring.append(' and ' + initials + ' ' + \
                                         surname + ', ')
                    else:
                        refstring.append(surname + ', ' + initials)
                        if j != len(authors) - 2:
                            # No comma before 'and'
                            refstring.append(', ')
                    if author.attrib.get('role', '') == 'editor':
                        refstring.append('Ed., ')
                elif organization is not None and organization.text:
                    # Use organization instead of name
                    refstring.append(organization.text + ', ')
            title = ref.find('front/title')
            if title is not None and title.text:
                refstring.append('"' + title.text + '", ')
            else:
                xml2rfc.log.warn('No title specified in reference', \
                                 ref.attrib.get('anchor', ''))
            for seriesInfo in ref.findall('seriesInfo'):
                refstring.append(seriesInfo.attrib['name'] + ' ' + \
                                 seriesInfo.attrib['value'] + ', ')
            date = ref.find('front/date')
            month = date.attrib.get('month', '')
            if month:
                month += ' '
            year = date.attrib.get('year', '')
            refstring.append(month + year)
            # Target?
            target = ref.attrib.get('target')
            if target:
                refstring.append(', <' + target + '>')
            refstring.append('.')
            annotation = ref.find('annotation')
            # Use anchor or num depending on PI
            if self.pis.get('symrefs', 'yes') == 'yes':
                bullet = '[' + ref.attrib.get('anchor', str(i + 1)) + ']'
            else:
                bullet = '[' + str(i + 1) + ']'
            refdict[bullet] = ''.join(refstring)
            refkeys.append(bullet)
            # Add annotation if it exists to a separate dict
            if annotation is not None and annotation.text:
                # Render annotation as a separate paragraph
                annotationdict[bullet] = annotation.text
        if self.pis.get('sortrefs', 'no') == 'yes':
            refkeys = sorted(refkeys)
        # Hard coded indentation amount
        refindent = 11
        for key in refkeys:
            self._write_ref_element(key, refdict[key], refindent)
            # Render annotation as a separate paragraph
            if key in annotationdict:
                self._write_text(annotationdict[key], indent=refindent + 3, \
                                 lb=True)

    def draw_table(self, table, table_num=None):
        # First construct a 2d matrix from the table
        matrix = []
        matrix.append([])
        row = 0
        column_aligns = []
        for ttcol in table.findall('ttcol'):
            column_aligns.append(ttcol.attrib.get('align', 'left'))
            if ttcol.text:
                matrix[row].append(ttcol.text)
            else:
                matrix[row].append('')
        num_columns = len(matrix[0])
        for i, cell in enumerate(table.findall('c')):
            if i % num_columns == 0:
                row += 1
                matrix.append([])
            text = cell.text or ''
            if len(cell) > 0:
                # <c> has children, render their text and add to line
                inline_text, null = \
                    self._combine_inline_elements(cell.getchildren())
                text += inline_text
            matrix[row].append(text)

        # Find the longest line in each column, and define column widths
        longest_lines = [0] * num_columns
        for col in range(num_columns):
            for row in matrix:
                if len(row[col]) > longest_lines[col]:
                    longest_lines[col] = len(row[col])
        max_width = self.width - 3 - 3 * num_columns - 1  # indent+border
        total_length = reduce(lambda x, y: x + y, longest_lines)

        if total_length > max_width:
            scale = float(max_width) / float(total_length)
            column_widths = [int(length * scale) for length in longest_lines]
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
            [
                textwrap.wrap(cell, column_widths[j]) \
                for j, cell in enumerate(matrix[i])
            ] for i in range(0, len(matrix))
        ]

        output = []
        style = table.attrib.get('style', 'full')
        # Create the border
        if style == 'headers':
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
            for row in range(max(map(len, cell_line))):
                if style == 'headers':
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
                        if style == 'headers':
                            line.append(text)
                            line.append(' ')
                        else:
                            line.append(' ')
                            line.append(text)
                            line.append(' |')
                    else:
                        if style == 'headers':
                            line.append(' ' * (column_widths[col] + 1))
                        else:
                            line.append(' ' * (column_widths[col] + 2) + '|')
                output.append(''.join(line))
            if i == 0:
                # This is the header row, append the header decoration
                output.append(''.join(borderstring))

        if style != 'headers':
            output.append(''.join(borderstring))

        # Finally, write the table to the buffer with proper alignment
        align = table.attrib.get('align', 'center')
        self.write_raw('\n'.join(output), align=align)

    def insert_anchor(self, text):
        # No anchors for text
        pass

    def write_iref_index(self):
        # No iref for text
        pass

    def pre_processing(self):
        # Discard buffer from indexing pass
        self.buf = []
        
        # Reset document counters from indexing pass
        self.edit_counter = 0   # Counter for edit marks
        self.eref_counter = 0   # Counter for <eref> elements
        
        # Replace unicode characters in RFC with proper ascii equivalents
        self.xmlrfc.replaceUnicode()
        pass

    def post_processing(self):
        self._write_toc()

    def write_to_file(self, file):
        """ Writes the buffer to the specified file """

        # Write buffer to file
        for line_num, line in enumerate(self.buf):
            # Check for marks
            if line_num == self.toc_marker and self.toc_marker > 0:
                for tmpline in self.tocbuf:
                    file.write(tmpline)
                    file.write('\r\n')
            file.write(line)
            file.write('\r\n')
