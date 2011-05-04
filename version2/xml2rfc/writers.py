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

    def __init__(self, rfc):
        self.rfc = rfc
        self.width = 72
        self.buf = []

    def lb(self):
        """ Write a blank line to the file """
        self.buf.append('')

    def write_line(self, str, indent=0):
        """ Writes an (optionally) indented line preceded by a line break. """
        if len(str) > (self.width):
            raise Exception("The supplied line exceeds the page width!\n \
                                                                    " + str)
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

    def write_section_rec(self, section, indexstring, index=1):
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

        for sec in section['section']:
            self.write_section_rec(sec, indexstring + str(index) + '.')
            index += 1

    def write_t_rec(self, t, indent=3, bullet=''):
        """ Recursively writes <t> elements """
        if t.text:
            self.write_par(t.text, indent=indent, bullet=bullet)

        for list in t['list']:
            # Default to the 'empty' list style -- 3 spaces
            bullet = '   '
            if 'style' in list.attribs:
                if list.attribs['style'] == 'symbol':
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

    def write(self, filename):
        # Prepare front page left heading
        fp_left = [self.rfc.attribs['trad_header']]
        if 'number' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['number'])
        if 'updates' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['updates'])
        if 'obsoletes' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['obsoletes'])
        if 'category' in self.rfc.attribs:
            fp_left.append(self.rfc.attribs['category'])

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

        # Title
        self.write_line(self.rfc['front']['title'].text.center(self.width))

        # Abstract
        if 'abstract' in self.rfc['front']:
            self.write_line('Abstract')
            for t in self.rfc['front']['abstract']['t']:
                self.write_par(t.text, indent=3)

        # Status
        self.write_line('Status of this Memo')
        self.write_par(self.rfc.attribs['status'], indent=3)

        # Copyright
        self.write_line('Copyright Notice')
        self.write_par(self.rfc.attribs['copyright'], indent=3)

        # Table of contents

        # Middle sections
        self.write_section_rec(self.rfc['middle'], None)

        # Back sections
        self.write_section_rec(self.rfc['back'], None, index=10)

        # Done!  Write buffer to file
        file = open(filename, 'w')
        for line in self.buf:
            file.write(line)
            file.write('\n')
