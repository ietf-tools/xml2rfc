# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# External libs
from lxml.html import builder as E
import lxml
import os.path
import string

# Local libs
import xml2rfc
from xml2rfc.writers.base import BaseRfcWriter


class HtmlRfcWriter(BaseRfcWriter):
    """ Writes to an HTML file.
    
        If *css_document* is specified, an alternate css file is used.
        
        If *external_css* is set, the html file will contain a link to
        the css file, instead of inlining the file, which is the default
        behavior.
        
        *lang* controls the lang attribute of the html document
    """
    # HTML Specific Defaults that are not provided in XML document
    defaults = {'doctype': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">',
                'style_title': 'Xml2Rfc (sans serif)',
                'references_url': 'http://tools.ietf.org/html/'
                }

    def __init__(self, xmlrfc, css_document=None, external_css=False, \
                 lang='en', quiet=False, verbose=False):
        BaseRfcWriter.__init__(self, xmlrfc, quiet=quiet, verbose=verbose)
        self.list_counters = {}
        self.iref_index = []
        self.html = E.HTML(lang=lang)
        self.css_document = os.path.join(os.path.dirname(xml2rfc.__file__), \
                                         'templates/rfc.css')
        if css_document:
            if os.path.exists(css_document):
                self.css_document = css_document
            else:
                xml2rfc.log.warn('The default css document was used because ' \
                                 'the supplied file does not exist:', \
                                 css_document)
        self.external_css = external_css

        # Create head element -- only pre_processing() will insert here
        self.head = E.HEAD()
        self.html.append(self.head)

        # Create body element -- everything will be added to this
        self.body = E.BODY()
        self.html.append(self.body)

        # Create table of contents element
        self.toc_header = E.H1('Table of Contents', id='rfc.toc')
        self.toc_header.attrib['class'] = 'np'
        self.toc_list = E.UL()
        self.toc_list.attrib['class'] = 'toc'

    def _build_stylesheet(self):
        """ Returns either a <link> or <style> element for css data.

            The element returned is dependent on the value of expanded_css
        """
        if self.external_css:
            element = E.LINK(rel='stylesheet', href=self.css_document)
        else:
            file = open(self.css_document, 'r')
            element = E.STYLE(file.read(), \
                              title=HtmlRfcWriter.defaults['style_title'])
        element.attrib['type'] = 'text/css'
        return element

    def _write_list(self, list, parent):
        style = list.attrib.get('style', 'empty')
        if style == 'hanging':
            list_elem = E.DL()
            hangIndent = list.attrib.get('hangIndent', '8')
            style = 'margin-left: ' + hangIndent
            for t in list.findall('t'):
                hangText = t.attrib.get('hangText', '')
                dt = E.DT(hangText)
                dd = E.DD(style=style)
                list_elem.append(dt)
                list_elem.append(dd)
                self.write_t_rec(t, parent=dd)
        elif style.startswith('format'):
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
            list_elem = E.DL()
            for t in list.findall('t'):
                self.list_counters[counter_index] += 1
                count = self.list_counters[counter_index]
                if '%d' in format_str:
                    bullet = format_str.replace(r'%d', str(count) + ' ')
                elif '%c' in format_str:
                    bullet = format_str.replace(r'%c', \
                                                str(string.ascii_lowercase\
                                                    [count % 26]) + ' ')
                else: 
                    bullet = format_str
                dt = E.DT(bullet)
                dd = E.DD()
                list_elem.append(dt)
                list_elem.append(dd)
                self.write_t_rec(t, parent=dd)
        else:
            if style == 'symbols':
                list_elem = E.UL()
            elif style == 'numbers':
                list_elem = E.OL()
            elif style == 'letters':
                list_elem = E.OL(style="list-style-type: lower-alpha")
            else:  # style == empty
                list_elem = E.UL()
                list_elem.attrib['class'] = 'empty'
            for t in list.findall('t'):
                li = E.LI()
                list_elem.append(li)
                self.write_t_rec(t, parent=li)
        parent.append(list_elem)

    # -----------------------------------------
    # Base writer overrides
    # -----------------------------------------

    def insert_toc(self):
        # Insert the table of contents element whereever we are in the body
        hr = E.HR()
        hr.attrib['class'] = 'noprint'
        self.body.append(hr)
        self.body.append(self.toc_header)
        self.body.append(self.toc_list)

    def write_raw(self, text, align='left'):
        pre = E.PRE(text)
        self.body.append(pre)

    def write_label(self, text, type='figure', align='center'):
        # Ignore labels for table, they are handled in draw_table
        if type == 'figure':
            p = E.P(text)
            p.attrib['class'] = 'figure'
            self.body.append(p)

    def write_title(self, title, docName=None):
        p = E.P(title)
        p.attrib['class'] = 'title'
        if docName:
            p.append(E.BR())
            span = E.SPAN(docName)
            span.attrib['class'] = 'filename'
            p.append(span)
        self.body.append(p)

    def write_heading(self, text, bullet=None, idstring=None, anchor=None, \
                      level=1):
        if level > 1:
            h = E.H2()
        else:
            h = E.H1()
        if idstring:
            h.attrib['id'] = idstring
        if bullet:
            # Use separate elements for bullet and text
            a_bullet = E.A(bullet)
            a_bullet.tail = ' '
            if idstring:
                a_bullet.attrib['href'] = '#' + idstring
            h.append(a_bullet)
            if anchor:
                # Use an anchor link for heading
                a_text = E.A(text, href='#' + anchor)
                h.append(a_text)
            else:
                # Plain text
                a_bullet.tail += text
        else:
            # Only use one <a> pointing to idstring
            a = E.A(text)
            if idstring:
                a.attrib['href'] = '#' + idstring
            h.append(a)
        self.body.append(h)

    def write_paragraph(self, text, align='left', idstring=None):
        if text:
            p = E.P(text)
            if idstring:
                p.attrib['id'] = idstring
            self.body.append(p)

    def write_t_rec(self, t, idstring=None, align='left', parent=None):
        """ Recursively writes a <t> element

            If no parent is specified, <body> will be treated as the parent,
            and any text will go in a <p> element.  Otherwise text and
            child elements will be insert directly into the parent -- meaning
            we are in a list
        """
        if parent is None:
            parent = self.body
            current = E.P()
            parent.append(current)
        else:
            current = parent
        if t.text:
            current.text = t.text
            if idstring:
                current.attrib['id'] = idstring
        for child in t:
            if child.tag == 'xref' or child.tag == 'eref':
                target = child.attrib.get('target', '')
                if child.text:
                    a = E.A(child.text, href='#' + target)
                    a.tail = ' '
                    current.append(a)
                # TODO: Grab proper title from reference
                cite = E.CITE('[' + target + ']', title='NONE')
                if child.tail:
                    cite.tail = child.tail
                current.append(cite)
            elif child.tag == 'iref':
                # Add anchor to index
                item = child.attrib.get('item', '')
                subitem = child.attrib.get('subitem', '')
                index_elem = (item, subitem)
                self.iref_index.append(index_elem)
                # Create anchor element
                a = E.A()
                current.append(a)
                if subitem:
                    a.attrib['name'] ='.'.join(index_elem)
                else:
                    a.attrib['name'] = item
                if child.tail:
                    a.tail = child.tail
            elif child.tag == 'spanx':
                style = child.attrib.get('style', 'emph')
                text = ''
                if child.text: 
                    text = child.text
                elem = None
                if style == 'strong':
                    elem = E.STRONG(text)
                elif style == 'verb':
                    elem = E.SAMP(text)
                else:
                    # Default to style=emph
                    elem = E.EM(text)
                current.append(elem)
                if child.tail:
                    elem.tail = child.tail
            elif child.tag == 'vspace':
                br = E.BR()
                current.append(br)
                blankLines = int(child.attrib.get('blankLines'), 0)
                for i in range(blankLines):
                    br = E.BR()
                    current.append(br)
                if child.tail:
                    br.tail = child.tail
            elif child.tag == 'list':
                self._write_list(child, parent)
                if child.tail:
                    parent.append(E.P(child.tail))
            elif child.tag == 'figure':
                # Callback to base writer method
                self._write_figure(child)
            elif child.tag == 'texttable':
                # Callback to base writer method
                self._write_table(child)

    def write_top(self, left_header, right_header):
        """ Adds the header table """
        table = E.TABLE()
        table.attrib['class'] = 'header'
        tbody = E.TBODY()
        for i in range(max(len(left_header), len(right_header))):
            if i < len(left_header):
                left_string = left_header[i]
            else:
                left_string = ''
            if i < len(right_header):
                right_string = right_header[i]
            else:
                right_string = ''
            td_left = E.TD(left_string)
            td_left.attrib['class'] = 'left'
            td_right = E.TD(right_string)
            td_right.attrib['class'] = 'right'
            tbody.append(E.TR(td_left, td_right))
        table.append(tbody)
        self.body.append(table)

    def write_address_card(self, author):
        div = E.DIV()
        div.attrib['class'] = 'avoidbreak'
        address_elem = E.ADDRESS()
        address_elem.attrib['class'] = 'vcard'

        # Name section
        vcardline = E.SPAN()
        vcardline.attrib['class'] = 'vcardline'
        fullname = author.attrib.get('fullname')
        role = author.attrib.get('role')
        fn = E.SPAN(fullname)
        fn.attrib['class'] = 'fn'
        if role:
            fn.tail = ' (' + role + ')'
        vcardline.append(fn)
        address_elem.append(vcardline)

        # Organization section
        organization = author.find('organization')
        if organization is not None and organization.text:
            org_vcardline = E.SPAN(organization.text)
            org_vcardline.attrib['class'] = 'org vcardline'
            address_elem.append(org_vcardline)

        # Address section
        address = author.find('address')
        if address is not None:
            adr_span = E.SPAN()
            adr_span.attrib['class'] = 'adr'
            postal = address.find('postal')
            if postal is not None:
                for street in postal.findall('street'):
                    if street.text:
                        # TODO -- Does street need a css class?
                        adr_span.append(E.SPAN(street.text))
                city_span = E.SPAN()
                city_span.attrib['class'] = 'vcardline'
                city = postal.find('city')
                if city is not None and city.text:
                    span = E.SPAN(city.text)
                    span.attrib['class'] = 'locality'
                    city_span.append(span)
                region = postal.find('region')
                if region is not None and region.text:
                    span = E.SPAN(region.text)
                    span.attrib['class'] = 'region'
                    city_span.append(span)
                code = postal.find('code')
                if code is not None and code.text:
                    span = E.SPAN(code.text)
                    span.attrib['class'] = 'code'
                    city_span.append(span)
                adr_span.append(city_span)
                country = postal.find('country')
                if country is not None and country.text:
                    span = E.SPAN(country.text)
                    span.attrib['class'] = 'country-name vcardline'
                    adr_span.append(span)
            address_elem.append(adr_span)
            phone = address.find('phone')
            if phone is not None and phone.text:
                span = E.SPAN('Phone: ' + phone.text)
                span.attrib['class'] = 'vcardline'
                address_elem.append(span)
            fascimile = address.find('fascimile')
            if fascimile is not None and fascimile.text:
                span = E.SPAN('Fax: ' + fascimile.text)
                span.attrib['class'] = 'vcardline'
                address_elem.append(span)
            email = address.find('email')
            if email is not None and email.text:
                span = E.SPAN('EMail: ')
                span.attrib['class'] = 'vcardline'
                span.append(E.A(email.text, href='mailto:' + email.text))
                address_elem.append(span)
            uri = address.find('uri')
            if uri is not None and uri.text:
                span = E.SPAN('URI: ')
                span.attrib['class'] = 'vcardline'
                span.append(E.A(uri.text, href=uri.text))
                address_elem.append(span)

        # Done, add to body
        div.append(address_elem)
        self.body.append(div)

    def write_reference_list(self, list):
        tbody = E.TBODY()
        for i, reference in enumerate(list.findall('reference')):
            tr = E.TR()
            # Use anchor attribute for bullet, otherwise i
            bullet = reference.attrib.get('anchor', str(i))
            bullet_td = E.TD(E.B('[' + bullet + ']', id=bullet))
            bullet_td.attrib['class'] = 'reference'
            ref_td = E.TD()
            ref_td.attrib['class'] = 'top'
            last = ref_td
            authors = reference.findall('front/author')
            for j, author in enumerate(authors):
                organization = author.find('organization')
                email = author.find('address/email')
                surname = author.attrib.get('surname')
                initials = author.attrib.get('initials', '')
                if surname is not None:
                    name_string = surname
                    if initials:
                        name_string += ', ' + initials
                    a = E.A(name_string)
                    if email is not None and email.text:
                        a.attrib['href'] = 'mailto:' + email.text
                    if organization is not None and organization.text:
                        a.attrib['title'] = organization.text
                    ref_td.append(a)
                    last = a
                    if j == len(authors) - 2:
                        # Second to last, add an "and"
                        a.tail = (' and ')
                    else:
                        a.tail = ', '
                elif organization is not None and organization.text:
                    # Use organization instead of name
                    a = E.A(organization.text)
                    ref_td.append(a)
                    last = a
            last.tail = ', "'
            title = reference.find('front/title')
            if title is not None and title.text:
                title_string = title.text
            else:
                xml2rfc.log.warn('No title specifide in reference:', \
                                 reference.get.attrib('anchor', ''))
                title_string = ''
            title_a = E.A(title_string)
            title_a.tail = '", '
            ref_td.append(title_a)
            for seriesInfo in reference.findall('seriesInfo'):
                # Create title's link to document from seriesInfo
                if seriesInfo.attrib.get('name', '') == 'RFC':
                    title_a.attrib['href'] = \
                        HtmlRfcWriter.defaults['references_url'] + \
                        'rfc' + seriesInfo.attrib.get('value', '')
                elif seriesInfo.attrib.get('name', '') == 'Internet-Draft':
                    title_a.attrib['href'] = \
                        HtmlRfcWriter.defaults['references_url'] + \
                        seriesInfo.attrib.get('value', '')
                title_a.tail += seriesInfo.attrib.get('name', '') + ' ' + \
                             seriesInfo.attrib.get('value', '') + ', '
            date = reference.find('front/date')
            month = date.attrib.get('month', '')
            if month:
                month += ' '
            year = date.attrib.get('year', '')
            title_a.tail += month + year + '.'
            tr.append(bullet_td)
            tr.append(ref_td)
            tbody.append(tr)
        self.body.append(E.TABLE(tbody))

    def draw_table(self, table, table_num=None):
        # TODO: Can 'full' be controlled from XML, as well as padding?
        style = 'tt full ' + table.attrib['align']
        cellpadding = '3'
        cellspacing = '0'
        htmltable = E.TABLE(cellpadding=cellpadding, cellspacing=cellspacing)
        htmltable.attrib['class'] = style

        # Add caption, if it exists
        if 'title' in table.attrib and table.attrib['title']:
            caption = ''
            if table_num:
                caption = 'Table ' + str(table_num) + ': '
            htmltable.append(E.CAPTION(caption + table.attrib['title']))

        # Draw headers
        header_row = E.TR()
        col_aligns = []
        for header in table.findall('ttcol'):
            th = E.TH()
            if header.text:
                th.text = header.text
            th.attrib['class'] = header.attrib['align']
            # Store alignment information
            col_aligns.append(header.attrib['align'])
            header_row.append(th)
        htmltable.append(E.THEAD(header_row))

        # Draw body
        body = E.TBODY()
        tr = E.TR()
        num_columns = len(col_aligns)
        for i, cell in enumerate(table.findall('c')):
            col_num = i % num_columns
            if col_num == 0 and i != 0:
                # New row
                body.append(tr)
                tr = E.TR()
            td = E.TD()
            if cell.text:
                td.text = cell.text
            # Get alignment from header
            td.attrib['class'] = col_aligns[col_num]
            tr.append(td)
        body.append(tr)  # Add final row
        htmltable.append(body)

        self.body.append(htmltable)

    def insert_anchor(self, text):
        div = E.DIV(id=text)
        self.body.append(div)
        
    def write_iref_index(self):
        # Omit this element if the index is empty
        if len(self.iref_index) > 0:
            self.write_heading('Index', idstring='index')
            self.add_to_toc('', 'Index', link='index')
            dl = E.DL()
            for iref in self.iref_index:
                if iref[1]:
                    dl.append(E.DT(iref[0]))
                    dl.append(E.DD(E.A(iref[1], href='#' + '.'.join(iref))))
                else:
                    dl.append(E.DD(E.A(iref[0], href='#' + iref[0])))
            self.body.append(dl)

    def add_to_toc(self, bullet, title, link=None):
        li = E.LI('')
        if bullet:
            li.text += bullet + '.   '
        if link:
            li.append(E.A(title, href='#' + link))
        else:
            li.text += title
        self.toc_list.append(li)

    def pre_processing(self):
        """ Insert all metadata into head """
        # Document title
        title = self.r.find('front/title')
        if title is not None and title.text:
            self.head.append(E.TITLE(title.text))
        
        # Stylesheet
        self.head.append(self._build_stylesheet())
        
        # Description (from abstract first t element)
        abs_t = self.r.find('front/abstract/t')
        if abs_t is not None and abs_t.text:
            self.head.append(E.META(name='description', content=abs_t.text))
        
        # Keywords
        keywords = self.r.findall('front/keyword')
        keyword_strings = []
        for keyword in keywords:
            if keyword.text:
                keyword_strings.append(keyword.text)
            else:
                xml2rfc.log.warn('<keyword> element was ignored because it '\
                                'had empty text.')
        if len(keyword_strings) > 0:
            self.head.append(E.META(name='keywords', \
                                    content=', '.join(keyword_strings)))

    def post_processing(self):
        # Nothing to do here
        pass

    def write_to_file(self, filename):
        # Write the tree to the file
        file = open(filename, 'w')
        file.write(HtmlRfcWriter.defaults['doctype'] + '\n')
        file.write(lxml.html.tostring(self.html, pretty_print=True))
