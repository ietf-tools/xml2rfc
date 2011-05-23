# Python libs
import textwrap
import string
import math

# Local lib
from xml2rfc.writers.base import BaseRfcWriter
import xml2rfc.utils


class RawTextRfcWriter(BaseRfcWriter):
    """ Writes to a text file, unpaginated, no headers or footers.

        Callback methods from base class will all write to a buffer list, buf
    """

    def __init__(self, xmlrfc, width=72, **kwargs):
        BaseRfcWriter.__init__(self, xmlrfc, **kwargs)
        self.width = width      # Page width
        self.buf = []           # Main buffer
        self.toc = []           # Table of contents buffer
        self.toc_marker = 0     # Line number in buffer to write toc too

    def _lb(self, buf=None):
        """ Write a blank line to the file """
        if not buf:
            buf = self.buf
        buf.append('')

    def _write_line(self, string, indent=0, lb=False, align='left', buf=None, \
                    strip=True):
        """ Writes a line preceded by an (optional) line break. """
        if not buf:
            buf = self.buf
        if len(string) > (self.width):
            raise Exception("The supplied line exceeds the page width!\n \
                                                                " + string)
        if lb:
            self._lb(buf=buf)
        if string:
            # Strip initial whitespace
            if strip:
                string = string.lstrip()
            if align == 'left':
                buf.append(' ' * indent + string)
            elif align == 'center':
                buf.append(string.center(self.width))
            elif align == 'right':
                buf.append(string.rjust(self.width))

    def _write_par(self, string, indent=0, sub_indent=None, bullet='', \
                  align='left', lb=False, buf=None, strip=True):
        if not buf:
            buf = self.buf
        # We can take advantage of textwraps initial_indent by using a bullet
        # parameter and treating it separately.  We still need to indent it.
        initial = ' ' * indent
        if bullet:
            initial += bullet
        if not sub_indent:
            # No sub_indent specified, use bullet length for indent amount
            subsequent = ' ' * len(initial)
        else:
            subsequent = ' ' * (sub_indent + indent)
        if lb:
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
            if align == 'center':
                for line in par:
                    buf.append(line.center(self.width))
            elif align == 'right':
                for line in par:
                    buf.append(line.rjust(self.width))
        elif bullet:
            # If the string is empty but a bullet was declared, just
            # print the bullet
            buf.append(initial)

    def _write_list(self, list, indent=3):
        """ Writes a <list> element """
        bullet = '   '
        hangIndent = None
        style = list.attrib.get('style', 'empty')
        if style == 'symbols':
            bullet = 'o  '
        elif style == 'hanging':
            hangIndent = list.attrib.get('hangIndent', None)
            if not hangIndent:
                # Set from length of first bullet.
                hangIndent = len(list.find('t').attrib.get('hangText', '')) + 1
        for i, t in enumerate(list.findall('t')):
            if style == 'numbers':
                bullet = str(i + 1) + '.  '
            elif style == 'letters':
                bullet = string.ascii_lowercase[i % 26] + '.  '
            elif style == 'hanging':
                bullet = t.attrib.get('hangText', '')
                bullet += ' '
            if hangIndent:
                self.write_t_rec(t, bullet=bullet, indent=indent, \
                                 sub_indent=int(hangIndent))
            else:
                self.write_t_rec(t, bullet=bullet, indent=indent)

    def _post_write_toc(self):
        """ Writes the table of contents to temporary buffer and returns

            This should only be called after the initial buffer is written.
        """
        tmpbuf = ['']
        self._write_line("Table of Contents", lb=True, buf=tmpbuf)
        self._lb(buf=tmpbuf)
        for line in self.toc:
            self._write_par(line, indent=3, buf=tmpbuf, strip=False)
        return tmpbuf

    def _expand_refs(self, element):
        """ Returns a block of text with inline references expanded

            If <vspace> is encountered, the method halts returning that element
        """
        return 'DEBUG'

    # ---------------------------------------------------------
    # Base writer overrides
    # ---------------------------------------------------------

    def insert_toc(self):
        """ Marks buffer position for post-writing table of contents """
        self.toc_marker = len(self.buf)

    def write_raw(self, text, align='left'):
        """ Writes a raw stream of characters, preserving space and breaks """
        # Convert tabs into spaces
        text = text.expandtabs(4)
        # Append an indent to every newline of the data
        lines = text.split('\n')
        if align == 'center':
            # Find the longest line, and use that as a fixed center.
            longest_line = len(max(lines, key=len))
            indent_str = ' ' * ((self.width - longest_line) / 2)
            for line in lines:
                self.buf.append(indent_str + line)
        elif align == 'right':
            for line in lines:
                self.buf.append(line.rjust(self.width))
        else:  # align == left
            indent_str = ' ' * 3
            for line in lines:
                self.buf.append(indent_str + line)

    def write_label(self, text, type='figure'):
        """ Writes a centered label """
        self._write_par(text, align='center', lb=True)

    def write_title(self, title, docName=None):
        """ Write the document title and (optional) name """
        self._write_par(title, lb=True, align='center')
        if docName is not None:
            self._write_par(docName, align='center')

    def write_heading(self, text, bullet=None, idstring=None, anchor=None, \
                      level=1):
        """ Write a generic header """
        if bullet:
            bullet += '  '
        else:
            bullet = ''
        self._write_par(text, bullet=bullet, indent=0, lb=True)

    def write_paragraph(self, text, align='left', idstring=None):
        """ Write a generic paragraph of text """
        self._write_par(text, indent=3, align=align, lb=True)

    def write_t_rec(self, t, indent=3, sub_indent=0, bullet='', \
                     idstring=None, align='left'):
        """ Recursively writes a <t> element """
        line = ['']
        if t.text:
            line.append(t.text)
        for child in t:
            # Check inline elements first
            if child.tag == 'xref' or child.tag == 'eref':
                if child.text:
                    line.append(child.text + ' ')
                line.append('[' + child.attrib['target'] + ']')
                if child.tail:
                    line.append(child.tail)
            elif child.tag == 'iref':
                # TODO: Handle iref
                pass
            else:
                # Submit initial buffer with a linebreak, then continue
                if len(line) > 0:
                    self._write_par(''.join(line), indent=indent, lb=True, \
                                    sub_indent=sub_indent, bullet=bullet)
                    line = []

            # Elements that require a separate buffer
            # Allow for nested lists by appending the length of the bullet,
            # But without including the bullet itself.
            if sub_indent > 0:
                new_indent = sub_indent + indent
            else:
                new_indent = len(bullet) + indent
            if child.tag == 'vspace':
                blankLines = int(child.attrib.get('blankLines', 0))
                for i in range(blankLines):
                    self._lb()
                if child.tail:
                    self._write_par(child.tail, indent=new_indent)
            elif child.tag == 'list':
                self._write_list(child, indent=new_indent)
                if child.tail:
                    self._write_par(child.tail, indent=new_indent, lb=True)
            elif child.tag == 'figure':
                # Callback to base writer method
                self._write_figure(child)
            elif child.tag == 'texttable':
                # Callback to base writer method
                self._write_table(child)

        # Submit anything leftover in the buffer
        if len(line) > 0:
            self._write_par(''.join(line), indent=indent, lb=True, \
                            sub_indent=sub_indent, bullet=bullet)

    def write_top(self, left_header, right_header):
        """ Combines left and right lists to write a document heading """
        for i in range(max(len(left_header), len(right_header))):
            if i < len(left_header):
                left = left_header[i]
            else:
                left = ''
            if i < len(right_header):
                right = right_header[i]
            else:
                right = ''
            self._write_line(xml2rfc.utils.justify_inline(left, '', right), \
                             strip=False)

    def write_address_card(self, author):
        """ Writes a simple address card with no line breaks """
        if 'role' in author.attrib:
                self._write_line(author.attrib['fullname'] + ', ' + \
                                author.attrib['role'], indent=3, lb=True)
        else:
            self._write_line(author.attrib['fullname'], indent=3, lb=True)
        organization = author.find('organization')
        if organization is not None and organization.text:
            self._write_line(organization.text, indent=3)
        address = author.find('address')
        if address is not None:
            postal = address.find('postal')
            if postal is not None:
                for street in postal.findall('street'):
                    if street.text:
                        self._write_line(street.text, indent=3)
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
                    self._write_line(''.join(cityline), indent=3)
                country = postal.find('country')
                if country is not None:
                    self._write_line(country.text, indent=3)
            self._lb()
            phone = address.find('phone')
            if phone is not None and phone.text:
                self._write_line('Phone: ' + phone.text, indent=3)
            fascimile = address.find('fascimile')
            if fascimile is not None and fascimile.text:
                self._write_line('Fax:   ' + fascimile.text, indent=3)
            email = address.find('email')
            if email is not None and email.text:
                self._write_line('EMail: ' + email.text, indent=3)
            uri = address.find('uri')
            if uri is not None and uri.text:
                self._write_line('URI:   ' + uri.text, indent=3)
        self._lb()

    def write_reference_list(self, list):
        """ Writes a formatted list of <reference> elements """
        # Use very first reference's [bullet] length for indent amount
        # sub_indent = len(list.find('reference').attrib['anchor']) + 4
        # Use a hard coded indent amount
        sub_indent = 11
        # [surname, initial.,] "title", (STD), (BCP), (RFC), (Month) Year.
        for i, ref in enumerate(list.findall('reference')):
            refstring = []
            authors = ref.findall('front/author')
            for j, author in enumerate(authors):
                organization = author.find('organization')
                if 'surname' in author.attrib:
                    initials = author.attrib.get('initials', '')
                    refstring.append(author.attrib['surname'] + ', ' + \
                                     initials + ', ')
                    if j == len(authors) - 2:
                        # Second-to-last, add an "and"
                        refstring.append('and ')
                elif organization is not None and organization.text:
                    # Use organization instead of name
                    refstring.append(organization.text + ', ')
            title = ref.find('front.title')
            if title and title.text:
                refstring.append('"' + title.text + '", ')
            for seriesInfo in ref.findall('seriesInfo'):
                refstring.append(seriesInfo.attrib['name'] + ' ' + \
                                 seriesInfo.attrib['value'] + ', ')
            date = ref.find('front/date')
            month = date.attrib.get('month', '')
            if month:
                month += ' '
            year = date.attrib.get('year', '')
            refstring.append(month + year + '.')
            bullet = '[' + ref.attrib['anchor'] + ']  '
            self._write_par(''.join(refstring), indent=3, bullet=bullet, \
                           sub_indent=sub_indent, lb=True)

    def draw_table(self, table, table_num=None):
        # First construct a 2d matrix from the table
        matrix = []
        matrix.append([])
        row = 0
        for ttcol in table.findall('ttcol'):
            if ttcol.text:
                matrix[row].append(ttcol.text)
            else:
                matrix[row].append('')
        num_columns = len(matrix[0])
        for i, cell in enumerate(table.findall('c')):
            if i % num_columns == 0:
                row += 1
                matrix.append([])
            if cell.text:
                matrix[row].append(cell.text)
            else:
                matrix[row].append('')

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

        # Now construct the cells using textwrap against column_widths
        cell_lines = [
            [
                textwrap.wrap(cell, column_widths[j]) \
                for j, cell in enumerate(matrix[i])
            ] for i in range(1, len(matrix))
        ]

        output = []
        # Create the border
        borderstring = ['+']
        for i in range(num_columns):
            borderstring.append('-' * (column_widths[i] + 2))
            borderstring.append('+')
        output.append(''.join(borderstring))

        # Draw the table
        for i, cell_line in enumerate(cell_lines):
            for row in range(max(map(len, cell_line))):
                line = ['|']
                for col, cell in enumerate(cell_line):
                    if row < len(cell):
                        line.append(' ')
                        line.append(cell[row].ljust(column_widths[col]))
                        line.append(' |')
                    else:
                        line.append(' ' * (column_widths[col] + 2) + '|')
                output.append(''.join(line))
            if i == 0:
                # Header, so output an additional border
                output.append(''.join(borderstring))
        output.append(''.join(borderstring))

        # Finally, write the table to the buffer with proper alignment
        align = table.attrib.get('align', 'center')
        self._lb()
        self.write_raw('\n'.join(output), align=align)

    def add_to_toc(self, bullet, title, idstring=None, anchor=None):
        if bullet:
            toc_indent = ' ' * ((bullet.count('.')) * 2)
            self.toc.append(toc_indent + bullet + ' ' + title)
        else:
            self.toc.append(title)

    def insert_anchor(self, text):
        # No anchors for text
        pass

    def pre_processing(self):
        # Replace unicode characters in RFC with proper ascii equivalents
        self.xmlrfc.replaceUnicode()
        pass

    def post_processing(self):
        # Raw text, no post processing necessary
        pass

    def write_to_file(self, filename):
        """ Writes the buffer to the specified file """

        # Write buffer to file
        file = open(filename, 'w')
        for line_num, line in enumerate(self.buf):
            # Check for marks
            if line_num == self.toc_marker:
                # Write TOC
                tmpbuf = self._post_write_toc()
                for tmpline in tmpbuf:
                    file.write(tmpline)
                    file.write('\r\n')
            file.write(line)
            file.write('\r\n')
        file.close()
