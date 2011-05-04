""" Writer classes to output rfc data to various formats """

import textwrap
import string


def justify_inline(left_str, center_str, right_str, width=72):
    """ Takes three string arguments and outputs a single string with the
        arguments left-justified, centered, and right-justified respectively.

        Throws an exception if the combined length of the three strings is
        greater than the width.
    """
    
    if (len(left_str) + len(center_str) + len(right_str)) > width:
        raise Exception("The given strings are greater than a width of: "\
                                                            + str(width))
    else:
        center_str_pos = width / 2 - len(center_str) / 2
        str = left_str + ' ' * (center_str_pos - len(left_str)) \
            + center_str + ' ' * (center_str_pos - len(right_str)) \
            + right_str
        return str


class XmlRfcWriter:
    """ Base class for all writers """
    rfc = None

    def __init__(self, rfc):
        self.rfc = rfc

    def write(self, filename):
        raise NotImplementedError('write() must be overridden')


class RawTextRfcWriter(XmlRfcWriter):
    """ Writes to a text file, unpaginated, no headers or footers. """
    width = None
    buf = None
    ref_index = None

    def __init__(self, rfc):
        XmlRfcWriter.__init__(self, rfc)
        self.width = 72
        self.buf = []
        self.ref_index = 1

    def lb(self):
        """ Write a blank line to the file """
        self.buf.append('')

    def write_line(self, str, indent=0, lb=True):
        """ Writes an (optionally) indented line preceded by a line break. """
        if len(str) > (self.width):
            raise Exception("The supplied line exceeds the page width!\n \
                                                                    " + str)
        if lb:
            self.lb()
        self.buf.append(' ' * indent + str)

    def write_par(self, str, indent=0, bullet=''):
        """ Writes an indented and wrapped paragraph, preceded by a lb. """
        # We can take advantage of textwraps initial_indent by using a bullet
        # parameter and treating it separately.  We still need to indent it.
        initial = ' ' * indent + bullet
        subsequent = ' ' * len(initial)
        par = textwrap.wrap(str, self.width, \
                            initial_indent=initial, \
                            subsequent_indent=subsequent)
        self.lb()
        self.buf.extend(par)

    def write_section_rec(self, section, indexstring, appendix=False):
        """ Recursively writes <section> elements """
        if indexstring:
            # Prepend a neat index string to the title
            self.write_line(indexstring + ' ' + section.attribs['title'])
        else:
            # Must be <middle> or <back> element -- no title or index.
            indexstring = ''

        for t in section['t']:
            self.write_t_rec(t)

        for figure in section['figure']:
            if 'preamble' in figure:
                self.write_par(figure['preamble'].text, indent=3)
            if 'artwork' in figure:
                self.write_par(figure['artwork'].text, indent=3)
            if 'postamble' in figure:
                self.write_par(figure['postamble'].text, indent=3)

        index = 1
        for sec in section['section']:
            if appendix == True:
                self.write_section_rec(sec, 'Appendix ' + \
                                       string.uppercase[index-1] + '.')
            else:
                self.write_section_rec(sec, indexstring + str(index) + '.')
            index += 1

        # Set the ending index number so we know where to begin references
        if indexstring == '' and appendix == False:
            self.ref_index = index

    def write_t_rec(self, t, indent=3, bullet=''):
        """ Recursively writes <t> elements """
        if t.text:
            self.write_par(t.text, indent=indent, bullet=bullet)

        for list in t['list']:
            # Default to the 'empty' list style -- 3 spaces
            bullet = '   '
            if 'style' in list.attribs:
                if list.attribs['style'] == 'symbols':
                    bullet = 'o  '
            for i, t in enumerate(list['t']):
                if list.attribs['style'] == 'numbers':
                    bullet = str(i + 1) + '.  '
                elif list.attribs['style'] == 'letters':
                    bullet = string.ascii_lowercase[i % 26] + '.  '
                self.write_t_rec(t, indent=indent, bullet=bullet)

        for figure in t['figure']:
            if 'preamble' in figure:
                self.write_par(figure['preamble'].text, indent=3)
            if 'artwork' in figure:
                self.write_par(figure['artwork'].text, indent=3)
            if 'postamble' in figure:
                self.write_par(figure['postamble'].text, indent=3)
    
    def write_reference_list(self, references):
        """ Writes a formatted list of <reference> elements """
        # [surname, initial.,] "title", (STD), (BCP), (RFC), (Month) Year.
        for i, ref in enumerate(references['reference']):
            refstring = []
            for j, author in enumerate(ref['front']['author']):
                refstring.append(author.attribs['surname'] + ', ' + \
                                 author.attribs['initials'] + '., ')
                if j == len(ref['front']['author']) - 2:
                    # Second-to-last, add an "and"
                    refstring.append('and ')
                    refstring.append(author.attribs['surname'] + ', ' + \
                                     author.attribs['initials'] + '., ')
            refstring.append('"' + ref['front']['title'].text + '", ')
            # TODO: Handle seriesInfo
            date = ref['front']['date']
            if 'month' in date.attribs:
                refstring.append(date.attribs['month'])
            refstring.append(date.attribs['year'] + '.')
            # TODO: Should reference list have [anchor] or [1] for bullets?
            bullet = '[' + str(i+1) + ']  '
            self.write_par(''.join(refstring), indent=3, bullet=bullet)

    def write_buffer(self):
        """ Internal method that writes the entire RFC tree to a buffer 
            
            Actual writing to a file, plus some post formatting is handled
            in self.write(), which is the public method to be called.
        """
        # Prepare front page left heading
        fp_left = [self.rfc.attribs['trad_header']]
        if 'number' in self.rfc.attribs:
            fp_left.append('Request for Comments: ' + self.rfc.attribs['number'])
        else:
            # No RFC number -- assume internet draft
            fp_left.append('Internet-Draft')
        if 'updates' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['updates'])
        if 'obsoletes' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['obsoletes'])
        if 'category' in self.rfc.attribs:
            fp_left.append('Category: ' + self.rfc.attribs['category'])

        # Prepare front page right heading
        fp_right = []
        for author in self.rfc['front']['author']:
            fp_right.append(author.attribs['initials'] + ' ' + \
                            author.attribs['surname'])
            if 'organization' in author:
                fp_right.append(author['organization'].text)
        date = self.rfc['front']['date']
        fp_right.append(date.attribs['month'] + ' ' + date.attribs['year'])

        # Front page heading
        for i in range(max(len(fp_left), len(fp_right))):
            if i < len(fp_left):
                left = fp_left[i]
            else:
                left = ''
            if i < len(fp_right):
                right = fp_right[i]
            else:
                right = ''
            self.buf.append(justify_inline(left, '', right))

        # Title & Optional docname
        self.write_line(self.rfc['front']['title'].text.center(self.width))
        if 'docName' in self.rfc.attribs:
            self.write_line(self.rfc.attribs['docName'].center(self.width), \
                            lb=False)

        # Abstract
        if 'abstract' in self.rfc['front']:
            self.write_line('Abstract')
            for t in self.rfc['front']['abstract']['t']:
                self.write_t_rec(t)

        # Status
        self.write_line('Status of this Memo')
        self.write_par(self.rfc.attribs['status'], indent=3)

        # Copyright
        self.write_line('Copyright Notice')
        self.write_par(self.rfc.attribs['copyright'], indent=3)

        # Table of contents
        # TODO: Look-ahead TOC or modify the buffer afterwards?

        # Middle sections
        self.write_section_rec(self.rfc['middle'], None)

        # References section
        ref_indexstring = str(self.ref_index) + '.'
        self.write_line(ref_indexstring + ' References')
        # Treat references as nested only if there is more than one <references>
        if len(self.rfc['back']['references']) > 1:
            for index, references in enumerate(self.rfc['back']['references']):
                title = references.attribs['title']
                self.write_line(ref_indexstring + str(index + 1) + '. ' + title)
                self.write_reference_list(references)
        else:
            self.write_reference_list(self.rfc['back']['references'][0])
        
        # Appendix sections
        self.write_section_rec(self.rfc['back'], None, appendix=True)
        
        # Authors address section
        if len(self.rfc['front']['author']) > 1:
            self.write_line("Authors' Addresses")
        else:
            self.write_line("Authors Address")
        for author in self.rfc['front']['author']:
            if 'role' in author.attribs:
                self.write_line(author.attribs['fullname'] + ', ' + \
                                author.attribs['role'], indent=3)
            else:
                self.write_line(author.attribs['fullname'], indent=3)
            if 'organization' in author:
                self.write_line(author['organization'].text, indent=3, lb=False)
            if 'address' in author:
                if 'postal' in author['address']:
                    for street in author['address']['postal']['street']:
                        if street.text:
                            self.write_line(street.text, indent=3, lb=False)
                    cityline = []
                    if 'city' in author['address']['postal']:
                        cityline.append(author['address']['postal']['city'].text)
                        cityline.append(', ')
                    if 'region' in author['address']['postal']:
                        cityline.append(author['address']['postal']['region'].text)
                        cityline.append(' ')
                    if 'code' in author['address']['postal']:
                        cityline.append(author['address']['postal']['code'])
                    self.write_line(''.join(cityline), indent=3, lb=False)
                    if 'country' in author['address']['postal']:
                        self.write_line(author['address']['postal']['country'].text, indent=3, lb=False)
                self.lb()
                if 'phone' in author['address']:
                    self.write_line('Phone: ' + author['address']['phone'].text, indent=3, lb=False)
                if 'fascimile' in author['address']:
                    self.write_line('Fax:   ' + author['address']['fascimile'].text, indent=3, lb=False)
                if 'email' in author['address']:
                    self.write_line('Email: ' + author['address']['email'].text, indent=3, lb=False)
                if 'uri' in author['address']:
                    self.write_line('URI:   ' + author['address']['uri'].text, indent=3, lb=False)

        # EOF 

    def write(self, filename):
        """ Public method to write rfc tree to a file """
        
        # Write RFC to buffer
        self.write_buffer()
        
        # Write buffer to file
        file = open(filename, 'w')
        for line in self.buf:
            file.write(line)
            # Separate lines by both carriages returns and line breaks.
            file.write('\r\n')

class PaginatedTextRfcWriter(RawTextRfcWriter):
    """ Writes to a text file, paginated with headers and footers """
    left_footer = None
    center_footer = None
    
    def __init__(self, rfc):
        RawTextRfcWriter.__init__(self, rfc)
        self.left_footer = ''
        self.center_footer = ''
        
    def make_footer(self, page):
        return justify_inline(self.left_footer, self.center_footer, \
                              '[Page ' + str(page) + ']')
        
    def write(self, filename):
        """ Public method to write rfc tree to a file """
        # Construct a header
        if 'number' in self.rfc.attribs:
            left_header = self.rfc.attribs['number']
        else:
            # No RFC number -- assume internet draft
            left_header = 'Internet-Draft'
        if 'abbrev' in self.rfc['front']['title'].attribs:
            center_header = self.rfc['front']['title'].attribs['abbrev']
        else:
            # No abbreviated title -- assume original title fits
            center_header = self.rfc['front']['title'].text
        right_header = ''
        if 'month' in self.rfc['front']['date'].attribs:
            right_header = self.rfc['front']['date'].attribs['month'] + ' '
        right_header += self.rfc['front']['date'].attribs['year']
        header = justify_inline(left_header, center_header, right_header)
        
        # Construct a footer
        self.left_footer = ''
        for i, author in enumerate(self.rfc['front']['author']):
            # Format: author1, author2 & author3 OR author1 & author2 OR author1
            if i < len(self.rfc['front']['author']) - 2:
                self.left_footer += author.attribs['surname'] + ', '
            elif i == len(self.rfc['front']['author']) - 2:
                self.left_footer += author.attribs['surname'] + ' & '
            else:
                self.left_footer += author.attribs['surname']
        self.center_footer = self.rfc.attribs['category']
        
        # Write RFC to buffer
        self.write_buffer()
        
        # Write buffer to file, inserting breaks every 58 lines
        file = open(filename, 'w')
        page = 0
        for i, line in enumerate(self.buf):
            file.write(line)
            file.write('\r\n')
            if i != 0 and i%54 == 0:
                page += 1
                file.write('\r\n')
                file.write(self.make_footer(page))
                file.write('\r\n')
                file.write('\f')
                file.write('\r\n')
                file.write(header)
                file.write('\r\n')
                file.write('\r\n')
        