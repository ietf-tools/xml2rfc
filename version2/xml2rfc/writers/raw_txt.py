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
        self.ref_index = 1      # Index number for the references section
        self.toc_marker = 0     # Line number in buffer to write toc too
        self.figure_count = 0
        self.table_count = 0
        
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

    def _write_par(self, str, indent=0, sub_indent=None,bullet='', \
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
        else: # align == left
            indent_str = ' ' * indent
            for line in lines:
                self.buf.append(indent_str + line) 

    def _write_t_rec(self, t, indent=3, sub_indent=None, bullet=''):
        """ Recursively writes <t> elements """
        line = []
        if t.text:
            line.append(t.text)

        for element in t:
            if element.tag == 'xref':
                if element.text:
                    line.append(element.text + ' ')
                line.append('[' + element.attrib['target'] + ']')
                if element.tail:
                    line.append(element.tail)
            elif element.tag == 'eref':
                if element.text:
                    line.append(element.text + ' ')
                line.append('[' + element.attrib['target'] + ']')
                if element.tail:
                    line.append(element.tail)
            elif element.tag == 'iref': pass
            elif element.tag == 'vspace':
                for i in range(int(element.attrib['blankLines'])):
                    line.append('\n')
                if element.tail:
                    line.append(element.tail)
            else:
                # Not an inline element.  Output what we have so far
                if len(line) > 0:
                    self._write_par(''.join(line), indent=indent, \
                                   sub_indent=sub_indent, bullet=bullet)
                    line = []
            
            if element.tag == 'list':
                # Default to the 'empty' list style -- 3 spaces
                bullet = '   '
                style = 'empty'
                hangIndent = None
                if 'style' in element.attrib:
                    style = element.attrib['style']
                if style == 'symbols':
                    bullet = 'o  '
                for i, t in enumerate(element.findall('t')):
                    if style == 'numbers':
                        bullet = str(i + 1) + '.  '
                    elif style == 'letters':
                        bullet = string.ascii_lowercase[i % 26] + '.  '
                    elif style == 'hanging':
                        bullet = t.attrib['hangText'] + ' '
                        hangIndent = element.attrib['hangIndent']
                    if hangIndent:
                        self._write_t_rec(t, indent=indent, bullet=bullet, \
                                         sub_indent=int(hangIndent))
                    else:
                        # Empty
                        self._write_t_rec(t, indent=indent, bullet=bullet)
                if element.tail:
                    self._write_par(element.tail, indent=3)

            elif element.tag == 'figure':
                self.write_figure(element)
                if element.tail:
                    self._write_par(element.tail, indent=3)
            elif element.tag == 'texttable':
                self.write_table(element)
                if element.tail:
                    self.write_par(element.tail, indent=3)

        if len(line) > 0:
            self._write_par(''.join(line), indent=indent, bullet=bullet, \
                           sub_indent=sub_indent)
    
    def _resolve_refs(self, element):
        """ Returns a string containing element text plus any inline refs """
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
            elif child.tag == 'iref': pass
        return ''.join(line)

    def write_section_rec(self, section, indexstring, appendix=False):
        """ Recursively writes <section> elements """
        if indexstring:
            # Prepend a neat index string to the title
            self.write_line(indexstring + ' ' + section.attrib['title'])
            # Write to TOC as well
            if section.attrib['toc'] != 'exclude':
                toc_indent = ' ' * ((indexstring.count('.') - 1) * 2)
                self.toc.append(toc_indent + indexstring + ' ' + \
                                section.attrib['title'])
        else:
            # Must be <middle> or <back> element -- no title or index.
            indexstring = ''
        
        for element in section:
            # Write elements in XML document order
            if element.tag == 't':
                self.write_t_rec(element)
            elif element.tag == 'figure':
                self.write_figure(element)
            elif element.tag == 'texttable':
                self.write_table(element)
        
        index = 1
        for child_sec in section.findall('section'):
            if appendix == True:
                self.write_section_rec(child_sec, 'Appendix ' + \
                                       string.uppercase[index-1] + '.')
            else:
                self.write_section_rec(child_sec, indexstring + \
                                       str(index) + '.')
            index += 1

        # Set the ending index number so we know where to begin references
        if indexstring == '' and appendix == False:
            self.ref_index = index
            
    def write_table(self, table):
        """ Writes <texttable> elements """
        align = table.attrib['align']
        
        # Write preamble
        preamble = table.find('preamble')
        if preamble is not None:
            self.write_par(self.resolve_refs(preamble), indent=3, \
                           align=align)
        
        self.table_count += 1
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
            borderstring.append('-' * (len(header)+2))
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
            cellstring.append(celltext.center(len(headers[column])+2))
            cellstring.append('|')
            if column == len(headers) - 1:
                # End of line
                lines.append(''.join(cellstring))
                cellstring = ['|']
            
        # Draw Bottom
        lines.append(''.join(borderstring))
        
        # Finally, write the table to the buffer with proper alignment
        self.lb()
        self.write_raw('\n'.join(lines), align=align)
        
        
        # Write postamble
        postamble = table.find('postamble')
        if postamble is not None:
            self.write_par(self.resolve_refs(postamble), indent=3, \
                           align=align)
        
        # Write label
        title = ''
        if table.attrib['title'] != '':
            title = ': ' + table.attrib['title']
        self.write_line('Table ' + str(self.figure_count) + title, \
                        align='center')

    def write_figure(self, figure):
        """ Writes <figure> elements """
        align = figure.attrib['align']
        
        # Write preamble
        preamble = figure.find('preamble')
        if preamble is not None:
            self.write_par(self.resolve_refs(preamble), indent=3, \
                           align=align)
        
        # Write figure
        self.figure_count += 1
        # TODO: Needs to be aligned properly
        # Insert artwork text directly into the buffer
        artwork = figure.find('artwork')
        artwork_align = align
        if 'align' in artwork.attrib:
            artwork_align = artwork.attrib['align']
        self.write_raw(figure.find('artwork').text, indent=3, \
                       align=artwork_align)
        
        # Write postamble
        postamble = figure.find('postamble')
        if postamble is not None:
            self.write_par(self.resolve_refs(postamble), indent=3, \
                           align=align)
        
        # Write label
        title = ''
        if figure.attrib['title'] != '':
            title = ': ' + figure.attrib['title']
        self.write_line('Figure ' + str(self.figure_count) + title, \
                        align='center')


    def write_reference_list(self, references):
        """ Writes a formatted list of <reference> elements """
        # Use very first reference's [bullet] length for indent amount
        sub_indent = len(references.find('reference').attrib['anchor']) + 4
        # [surname, initial.,] "title", (STD), (BCP), (RFC), (Month) Year.
        for i, ref in enumerate(references.findall('reference')):
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
                elif organization is not None and organization.text is not None:
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
            self.write_par(''.join(refstring), indent=3, bullet=bullet, \
                           sub_indent=sub_indent)
    
    def post_write_toc(self):
        """ Writes the table of contents to temporary buffer and returns
            
            This should only be called after the initial buffer is written.
        """
        tmpbuf = ['']
        self.write_line("Table of Contents", buf=tmpbuf)
        self.lb(buf=tmpbuf)
        for line in self.toc:
            self.write_line(line, indent=3, lb=False, buf=tmpbuf)
        return tmpbuf
    
#===============================================================================
# Abstract writer rewrite
#===============================================================================

    def mark_toc(self):
        """ Marks buffer position for post-writing table of contents """
        self.toc_marker = len(self.buf)

    def write_t(self, t):
        """ Writes a <t> element """
        self._write_t_rec(t)

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
    
    def write_title(self, title, docName=None):
        """ Write the document title and (optional) name """
        self._write_line(title.center(self.width))
        if docName is not None:
            self._write_line(docName.center(self.width), lb=False)
    
    def write_heading(self, text):
        """ Write a generic header """
        self._write_line(text, indent=0)
        
    def write_paragraph(self, text):
        """ Write a generic paragraph """
        self._write_par(text, indent=3)

    def write_buffer(self):
        """ Internal method that writes the entire RFC tree to a buffer

            Actual writing to a file, plus some post formatting is handled
            in self.write(), which is the public method to be called.
        """
        
        # Middle sections
        self.write_section_rec(self.r.find('middle'), None)

        # References section
        ref_indexstring = str(self.ref_index) + '.'
        # Treat references as nested only if there is more than one <references>
        references = self.r.findall('back/references')
        if len(references) > 1:
            ref_title = ref_indexstring + ' References'
            self.write_line(ref_title)
            self.toc.append(ref_title)
            for index, reference_list in enumerate(references):
                ref_title = ref_indexstring + str(index + 1) + '. ' + \
                            reference_list.attrib['title']
                self.write_line(ref_title)
                toc_indent = ' ' * ((ref_title.count('.') - 1) * 2)
                self.toc.append(toc_indent + ref_title)
                self.write_reference_list(reference_list)
        else:
            ref_title = ref_indexstring + ' ' + references[0].attrib['title']
            self.write_line(ref_title)
            self.toc.append(ref_title)
            self.write_reference_list(references[0])
        
        # Appendix sections
        self.write_section_rec(self.r.find('back'), None, appendix=True)

        # Authors address section
        authors = self.r.findall('front/author')
        if len(authors) > 1:
            self.write_line("Authors' Addresses")
            self.toc.append("Authors' Addresses")
        else:
            self.write_line("Authors Address")
            self.toc.append("Authors Address")
        for author in authors:
            if 'role' in author.attrib:
                self.write_line(author.attrib['fullname'] + ', ' + \
                                author.attrib['role'], indent=3)
            else:
                self.write_line(author.attrib['fullname'], indent=3)
            organization = author.find('organization')
            if organization is not None:
                self.write_line(organization.text, indent=3, lb=False)
            address = author.find('address')
            if address is not None:
                postal = address.find('postal')
                if postal is not None:
                    for street in postal.findall('street'):
                        if street.text:
                            self.write_line(street.text, indent=3, lb=False)
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
                        self.write_line(''.join(cityline), indent=3, lb=False)
                    country = postal.find('country')
                    if country is not None:
                        self.write_line(country.text, indent=3, lb=False)
                self.lb()
                phone = address.find('phone')
                if phone is not None and phone.text:
                    self.write_line('Phone: ' + phone.text, indent=3, lb=False)
                fascimile = address.find('fascimile')
                if fascimile is not None and fascimile.text:
                    self.write_line('Fax:   ' + fascimile.text, indent=3, lb=False)
                email = address.find('email')
                if email is not None and email.text:
                    self.write_line('EMail: ' + email.text, indent=3, lb=False)
                uri = address.find('uri')
                if uri is not None and uri.text:
                    self.write_line('URI:   ' + uri.text, indent=3, lb=False)
            self.lb()

        # EOF

    def write_to_file(self, filename):
        """ Public method to write rfc document to a file """

        # Write RFC to buffer
        # self.write_buffer()

        # Write buffer to file
        file = open(filename, 'w')
        for line_num, line in enumerate(self.buf):
            # Check for marks
            if line_num == self.toc_marker:
                # Write TOC
                # tmpbuf = self.post_write_toc()
                tmpbuf = []
                for tmpline in tmpbuf:
                    file.write(tmpline)
                    file.write('\r\n')
            file.write(line)
            file.write('\r\n')
        file.close()
