# External libs
from lxml.builder import E
import lxml.etree

# Local libs
from base import XmlRfcWriter

# HTML Specific Defaults that are not provided in XML document
# TODO: This could possibly go in parser.py, as a few defaults already do.
defaults = {'doctype': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">',
            'style_title': 'Xml2Rfc (sans serif)',
            }


class HtmlRfcWriter(XmlRfcWriter):
    """ Writes to an HTML file with embedded CSS """

    def __init__(self, xmlrfc, css_document='templates/rfc.css',
                 expanded_css=True, lang='en'):
        XmlRfcWriter.__init__(self, xmlrfc)
        self.html = E.html(lang=lang)
        self.css_document = css_document
        self.expanded_css = expanded_css

        # Create head element, add style/metadata/etc information
        self.html.append(self._build_head())

        # Create body element -- everything will be added to this
        self.body = E.body()
        self.html.append(self.body)

    def _build_stylesheet(self):
        """ Returns either a <link> or <style> element for css data.

            The element returned is dependent on the value of expanded_css
        """
        if self.expanded_css:
            file = open(self.css_document, 'r')
            element = E.style(file.read(), title=defaults['style_title'])
        else:
            element = E.link(rel='stylesheet', href=self.css_document)
        element.attrib['type'] = 'text/css'
        return element

    def _build_head(self):
        """ Returns the constructed <head> element """
        head = E.head()
        head.append(self._build_stylesheet())
        return head

    # -----------------------------------------
    # Base writer interface methods to override
    # -----------------------------------------

    def mark_toc(self):
        pass

    def write_raw(self, text, align='left'):
        pre = E.pre(text)
        self.body.append(pre)

    def write_label(self, text, type='figure', align='center'):
        # Ignore labels for table, they are handled in draw_table
        if type == 'figure':
            p = E.p(text)
            p.attrib['class'] = 'figure'
            self.body.append(p)

    def write_title(self, title, docName=None):
        p = E.p(title)
        p.attrib['class'] = 'title'
        if docName:
            p.append(E.br())
            span = E.span(docName)
            span.attrib['class'] = 'filename'
            p.append(span)
        self.body.append(p)

    def write_heading(self, text, bullet=None, idstring=None, anchor=None, \
                      level=1):
        if level > 1:
            h = E.h2()
        else:
            h = E.h1()
        if idstring:
            h.attrib['id'] = idstring
        if bullet:
            # Use separate elements for bullet and text
            a_bullet = E.a(bullet)
            if idstring:
                a_bullet.attrib['href'] = '#' + idstring
            h.append(a_bullet)
            if anchor:
                # Use an anchor link for heading
                a_text = E.a(text, href='#' + anchor)
                h.append(a_text)
            else:
                # Plain text
                a_bullet.tail = ' ' + text
        else:
            # Only use one <a> pointing to idstring
            a = E.a(text)
            if idstring:
                a.attrib['href'] = '#' + idstring
            h.append(a)
        self.body.append(h)

    def write_paragraph(self, text, align='left', idstring=None):
        if text:
            p = E.p(text)
            if idstring:
                p.attrib['id'] = idstring
            self.body.append(p)

    def write_list(self, list):
        pass

    def write_top(self, left_header, right_header):
        """ Adds the header table """
        table = E.table()
        table.attrib['class'] = 'header'
        tbody = E.tbody()
        for i in range(max(len(left_header), len(right_header))):
            if i < len(left_header):
                left_string = left_header[i]
            else:
                left_string = ''
            if i < len(right_header):
                right_string = right_header[i]
            else:
                right_string = ''
            td_left = E.td(left_string)
            td_left.attrib['class'] = 'left'
            td_right = E.td(right_string)
            td_right.attrib['class'] = 'right'
            tbody.append(E.tr(td_left, td_right))
        table.append(tbody)
        self.body.append(table)

    def write_address_card(self, author):
        pass

    def write_reference_list(self, list):
        pass

    def draw_table(self, table, table_num=None):
        # TODO: Can 'full' be controlled from XML, as well as padding?
        style = 'tt full ' + table.attrib['align']
        cellpadding = '3'
        cellspacing = '0'
        htmltable = E.table(cellpadding=cellpadding, cellspacing=cellspacing)
        htmltable.attrib['class'] = style

        # Add caption, if it exists
        if 'title' in table.attrib and table.attrib['title']:
            caption = ''
            if table_num:
                caption = 'Table ' + str(table_num) + ': '
            htmltable.append(E.caption(caption + table.attrib['title']))

        # Draw headers
        header_row = E.tr()
        col_aligns = []
        for header in table.findall('ttcol'):
            th = E.th(header.text)
            th.attrib['class'] = header.attrib['align']
            # Store alignment information
            col_aligns.append(header.attrib['align'])
            header_row.append(th)
        htmltable.append(E.thead(header_row))

        # Draw body
        body = E.tbody()
        tr = E.tr()
        num_columns = len(col_aligns)
        for i, cell in enumerate(table.findall('c')):
            col_num = i % num_columns
            if col_num == 0 and i != 0:
                # New row
                body.append(tr)
                tr = E.tr()
            td = E.td(cell.text)
            # Get alignment from header
            td.attrib['class'] = col_aligns[col_num]
            tr.append(td)
        body.append(tr)  # Add final row
        htmltable.append(body)

        self.body.append(htmltable)

    def insert_anchor(self, text):
        div = E.div(id=text)
        self.body.append(div)

    def expand_refs(self, element):
        """ Returns a <p> element with inline references expanded properly """
        return element.text

    def add_to_toc(self, bullet, title, anchor=None):
        pass

    def pre_processing(self):
        """ Handle any metadata """
        pass

    def post_processing(self):
        # Nothing to do here
        pass

    def write_to_file(self, filename):
        # Write the tree to the file
        file = open(filename, 'w')
        file.write(defaults['doctype'] + '\n')
        file.write(lxml.etree.tostring(self.html, pretty_print=True))
