# Python libs
import textwrap
import string

# Local lib
from base import XmlRfcWriter
import tools


class RawTextRfcWriter(XmlRfcWriter):
    """ Writes to a text file, unpaginated, no headers or footers.

        Callback methods from base class will all write to a buffer list, buf
    """

    def __init__(self, xmlrfc, width=72):
        XmlRfcWriter.__init__(self, xmlrfc)
        self.width = width      # Page width
        self.buf = []           # Main buffer
        self.toc = []           # Table of contents buffer
        self.toc_marker = 0     # Line number in buffer to write toc too

    def _lb(self, buf=None):
        """ Write a blank line to the file """
        if not buf:
            buf = self.buf
        buf.append('')

    def _write_line(self, str, indent=0, lb=True, align='left', buf=None):
        """ Writes an (optionally) indented line preceded by a line break. """
        if not buf:
            buf = self.buf
        if len(str) > (self.width):
            raise Exception("The supplied line exceeds the page width!\n \
                                                                    " + str)
        if lb:
            self._lb(buf=buf)
        if align == 'left':
            buf.append(' ' * indent + str)
        elif align == 'center':
            buf.append(str.center(self.width))
        elif align == 'right':
            buf.append(str.rjust(self.width))

    def _write_par(self, str, indent=0, sub_indent=None, bullet='', \
                  align='left', buf=None):
        """ Writes an indented and wrapped paragraph, preceded by a lb. """
        if not buf:
            buf = self.buf
        # We can take advantage of textwraps initial_indent by using a bullet
        # parameter and treating it separately.  We still need to indent it.
        initial = ' ' * indent + bullet
        if not sub_indent:
            # No sub_indent specified, use bullet length for indent amount
            subsequent = ' ' * len(initial)
        else:
            subsequent = ' ' * (sub_indent + indent)
        par = textwrap.wrap(str, self.width, \
                            initial_indent=initial, \
                            subsequent_indent=subsequent)
        self._lb()
        if align == 'left':
            buf.extend(par)
        if align == 'center':
            for line in par:
                buf.append(line.center(self.width))
        elif align == 'right':
            for line in par:
                buf.append(line.rjust(self.width))

    def _write_raw(self, data, indent=0, align='left'):
        """ Writes a raw stream of characters, preserving space and breaks """
        # Append an indent to every newline of the data
        lines = data.split('\n')
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
            indent_str = ' ' * indent
            for line in lines:
                self.buf.append(indent_str + line)

    def _post_write_toc(self):
        """ Writes the table of contents to temporary buffer and returns

            This should only be called after the initial buffer is written.
        """
        tmpbuf = ['']
        self._write_line("Table of Contents", buf=tmpbuf)
        self._lb(buf=tmpbuf)
        for line in self.toc:
            self._write_line(line, indent=3, lb=False, buf=tmpbuf)
        return tmpbuf

    # ---------------------------------------------------------
    # Base writer overrides
    # ---------------------------------------------------------

    def mark_toc(self):
        """ Marks buffer position for post-writing table of contents """
        self.toc_marker = len(self.buf)

    def write_raw(self, text, align='left'):
        """ Writes a raw stream of characters, preserving space and breaks """
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

    def write_label(self, text, type='figure', align='center'):
        """ Writes a label for a table or figure """
        self._write_line(text, align=align)

    def write_title(self, title, docName=None):
        """ Write the document title and (optional) name """
        self._write_line(title.center(self.width))
        if docName is not None:
            self._write_line(docName.center(self.width), lb=False)

    def write_heading(self, text, bullet=None, idstring=None, anchor=None):
        """ Write a generic header """
        if bullet:
            self._write_line(bullet + ' ' + text, indent=0)
        else:
            self._write_line(text, indent=0)

    def write_paragraph(self, text, align='left', idstring=None):
        """ Write a generic paragraph """
        self._write_par(text, indent=3, align=align)

    def write_list(self, list):
        """ Writes a <list> element """
        # TODO: Does this need to be recursive?
        bullet = '   '
        style = 'empty'
        hangIndent = None
        if 'style' in list.attrib:
            style = list.attrib['style']
        if style == 'symbols':
            bullet = 'o  '
        for i, t in enumerate(list.findall('t')):
            if style == 'numbers':
                bullet = str(i + 1) + '.  '
            elif style == 'letters':
                bullet = string.ascii_lowercase[i % 26] + '.  '
            elif style == 'hanging':
                bullet = t.attrib['hangText'] + ' '
                hangIndent = list.attrib['hangIndent']
            if hangIndent:
                self._write_par(self.expand_refs(t), bullet=bullet, \
                                indent=3, sub_indent=int(hangIndent))
            else:
                # Empty
                self._write_par(self.expand_refs(t), bullet=bullet, \
                                indent=3)

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
            self.buf.append(tools.justify_inline(left, '', right))

    def write_address_card(self, author):
        """ Writes a simple address card with no line breaks """
        if 'role' in author.attrib:
                self._write_line(author.attrib['fullname'] + ', ' + \
                                author.attrib['role'], indent=3)
        else:
            self._write_line(author.attrib['fullname'], indent=3)
        organization = author.find('organization')
        if organization is not None:
            self._write_line(organization.text, indent=3, lb=False)
        address = author.find('address')
        if address is not None:
            postal = address.find('postal')
            if postal is not None:
                for street in postal.findall('street'):
                    if street.text:
                        self._write_line(street.text, indent=3, lb=False)
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
                    self._write_line(''.join(cityline), indent=3, lb=False)
                country = postal.find('country')
                if country is not None:
                    self._write_line(country.text, indent=3, lb=False)
            self._lb()
            phone = address.find('phone')
            if phone is not None and phone.text:
                self._write_line('Phone: ' + phone.text, indent=3, lb=False)
            fascimile = address.find('fascimile')
            if fascimile is not None and fascimile.text:
                self._write_line('Fax:   ' + fascimile.text, indent=3, \
                                 lb=False)
            email = address.find('email')
            if email is not None and email.text:
                self._write_line('EMail: ' + email.text, indent=3, lb=False)
            uri = address.find('uri')
            if uri is not None and uri.text:
                self._write_line('URI:   ' + uri.text, indent=3, lb=False)
        self._lb()

    def write_reference_list(self, list):
        """ Writes a formatted list of <reference> elements """
        # Use very first reference's [bullet] length for indent amount
        sub_indent = len(list.find('reference').attrib['anchor']) + 4
        # [surname, initial.,] "title", (STD), (BCP), (RFC), (Month) Year.
        for i, ref in enumerate(list.findall('reference')):
            refstring = []
            authors = ref.findall('front/author')
            for j, author in enumerate(authors):
                organization = author.find('organization')
                if 'surname' in author.attrib:
                    refstring.append(author.attrib['surname'] + ', ' + \
                                     author.attrib['initials'] + ', ')
                    if j == len(authors) - 2:
                        # Second-to-last, add an "and"
                        refstring.append('and ')
                        refstring.append(author.attrib['surname'] + ', ' + \
                                         author.attrib['initials'] + '., ')
                elif organization is not None and organization.text:
                    # Use organization instead of name
                    refstring.append(organization.text + ', ')
            refstring.append('"' + ref.find('front/title').text + '", ')
            for seriesInfo in ref.findall('seriesInfo'):
                refstring.append(seriesInfo.attrib['name'] + ' ' + \
                                 seriesInfo.attrib['value'] + ', ')
            date = ref.find('front/date')
            if 'month' in date.attrib:
                refstring.append(date.attrib['month'] + ', ')
            refstring.append(date.attrib['year'])
            refstring.append('.')
            bullet = '[' + ref.attrib['anchor'] + ']  '
            self._write_par(''.join(refstring), indent=3, bullet=bullet, \
                           sub_indent=sub_indent)

    def draw_table(self, table):
        headers = []
        lines = []
        align = table.attrib['align']
        for column in table.findall('ttcol'):
            if column.text:
                headers.append(column.text)
            else:
                headers.append('')

        # Format headers to not exceed line width.  If it does exceed, the
        # algorithm takes the longest column header and splits it into another
        # line, breaking at the median space character.

        # Draw header
        borderstring = ['+']
        for header in headers:
            borderstring.append('-' * (len(header) + 2))
            borderstring.append('+')
        lines.append(''.join(borderstring))
        headerstring = ['|']
        for header in headers:
            headerstring.append(' ' + header + ' |')
        lines.append(''.join(headerstring))
        lines.append(''.join(borderstring))

        # Draw Cells
        cellstring = ['|']
        for i, cell in enumerate(table.findall('c')):
            column = i % len(headers)
            celltext = ''
            if cell.text:
                celltext = cell.text
            cellstring.append(celltext.center(len(headers[column]) + 2))
            cellstring.append('|')
            if column == len(headers) - 1:
                # End of line
                lines.append(''.join(cellstring))
                cellstring = ['|']

        # Draw Bottom
        lines.append(''.join(borderstring))

        # Finally, write the table to the buffer with proper alignment
        self._lb()
        self._write_raw('\n'.join(lines), align=align)

    def expand_refs(self, element):
        """ Returns a string with inline references expanded properly """
        line = []
        if element.text:
            line.append(element.text)
        for child in element:
            if child.tag == 'xref':
                if child.text:
                    line.append(child.text + ' ')
                line.append('[' + child.attrib['target'] + ']')
                if child.tail:
                    line.append(child.tail)
            elif child.tag == 'eref':
                if child.text:
                    line.append(child.text + ' ')
                line.append('[' + child.attrib['target'] + ']')
                if child.tail:
                    line.append(child.tail)
            # TODO: Handle iref
            elif child.tag == 'iref':
                pass
            # TODO: Handle vspace
            elif child.tag == 'vspace':
                if child.tail:
                    line.append(child.tail)
        return ''.join(line)

    def add_to_toc(self, bullet, title, anchor=None):
        if bullet:
            toc_indent = ' ' * ((bullet.count('.') - 1) * 2)
            self.toc.append(toc_indent + bullet + ' ' + title)
        else:
            self.toc.append(title)

    def post_processing(self):
        # Raw text, no post processing done here
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
