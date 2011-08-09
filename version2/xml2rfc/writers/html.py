# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# External libs
from lxml.html import builder as E
import lxml
import os.path
import string
import sys

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
    # HTML Specific Defaults that are not provided in templates or XML
    defaults = {'references_url': 'http://tools.ietf.org/html/',
               }

    def __init__(self, xmlrfc, quiet=False, verbose=False, templates_dir=None):
        BaseRfcWriter.__init__(self, xmlrfc, quiet=quiet, verbose=verbose)
        self.list_counters = {}
        self.iref_index = []
        
        # Initialize templates directory
        self.templates_dir = templates_dir or \
                             os.path.join(os.path.dirname(xml2rfc.__file__),
                                          'templates')

        # Open template files and read into string.template objects
        self.templates = {}
        for filename in ['base.html',
                         'address_card.html']:
            file = open(os.path.join(os.path.dirname(xml2rfc.__file__), 
                                     self.templates_dir, filename), 'r')
            self.templates[filename] = string.Template(file.read())

        # Buffers to aggregate various elements before processing template
        self.buffers = {'front': [],
                        'body': [],
                        'header_rows': [],
                        'toc_head_links': [],
                        'toc_rows': []}
        
        # Use an active buffer pointer
        self.active_buffer = self.buffers['front']
        
        # String holding the final document to write
        self.output = ''
        
        # Temporary div for recursive functions
        self.temp_div = E.DIV()

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
                                str(string.ascii_lowercase[count % 26]) + ' ')
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

    def _create_toc(self):
        # Add link for toc itself
        link = E.LINK(rel='Contents', href='#rfc.toc')
        self.buffers['toc_head_links'].append(self._serialize(link))
        for item in self._getTocIndex():
            # Create link for head
            link = E.LINK(href='#' + item.autoAnchor)
            link.attrib['rel'] = 'copyright' in item.autoAnchor and \
                                 'Copyright' or 'Chapter'
            if item.title and item.counter:
                link.attrib['title'] = item.counter + ' ' + item.title
            self.buffers['toc_head_links'].append(self._serialize(link))
            # Create actual toc list item
            a = E.A(item.title, href='#' + item.autoAnchor)
            counter_text = item.counter and item.counter + '.   ' or ''
            li = E.LI(counter_text)
            li.append(a)
            self.buffers['toc_rows'].append(self._serialize(li))

    def _serialize(self, element):
        return lxml.html.tostring(element, pretty_print=True)
    
    def _flush_temp_div(self):
        lines = []
        for child in self.temp_div:
            lines.append(self._serialize(child))
            child.drop_tree()
        return '\n'.join(lines)
    
    def _expand_ref(self, element):
        """ Return a list of HTML elements that represent the reference """   
        if element.tag == 'xref':
            target = element.attrib.get('target', '')
            if element.text:
                cite = E.CITE('[' + target + ']', title='NONE')
                a = E.A(element.text, href='#' + target)
                a.tail = ' '
                if element.tail:
                    cite.tail = element.tail
                return [a, cite]
            else:
                # Create xref from index lookup
                format = element.attrib.get('format', 'default')
                a = E.A(href='#' + target)
                item = self._getItemByAnchor(target)
                if not item or format == 'none':
                    text = '[' + target + ']'
                elif format == 'counter':
                    text = item.counter
                elif format == 'title':
                    text = item.title
                else:
                    # Default
                    text = item.autoName
                a.text = text
                if element.tail:
                    a.tail = element.tail
                return [a]
        elif element.tag == 'eref':
            target = element.attrib.get('target', '')
            text = element.text or target
            if text:
                a = E.A(text, href=target)
                a.tail = element.tail
#                cite = E.CITE('[' + target + ']', title='NONE')
#                current.append(cite)
                return [a]
        elif element.tag == 'iref':
            # Add anchor to index
            item = element.attrib.get('item', '')
            subitem = element.attrib.get('subitem', '')
            index_elem = (item, subitem)
            self.iref_index.append(index_elem)
            # Create anchor element
            a = E.A()
            if subitem:
                a.attrib['name'] = '.'.join(index_elem)
            else:
                a.attrib['name'] = item
            if element.tail:
                a.tail = element.tail
            return [a]
        elif element.tag == 'spanx':
            style = element.attrib.get('style', 'emph')
            text = ''
            if element.text:
                text = element.text
            elem = None
            if style == 'strong':
                elem = E.STRONG(text)
            elif style == 'verb':
                elem = E.SAMP(text)
            else:
                # Default to style=emph
                elem = E.EM(text)
            if element.tail:
                elem.tail = element.tail
            return [elem]

    # -----------------------------------------
    # Base writer overrides
    # -----------------------------------------

    def insert_toc(self):
        # We don't actually insert the toc here, but we swap the active buffer
        # So that the template replacement is correct
        self.active_buffer = self.buffers['body']

    def write_raw(self, text, align='left', blanklines=0, delimiter=None):
        # Add padding with delimiter/blanklines, if specified
        edge = delimiter and [delimiter] or ['']
        edge.extend([''] * blanklines)
        fill = '\n'.join(edge)
        fill += text
        edge.reverse()
        fill += '\n'.join(edge)

        # Run through template, add to body buffer
        pre = E.PRE(fill)
        self.active_buffer.append(self._serialize(pre))

    def write_label(self, text, type='figure', align='center'):
        # Ignore labels for table, they are handled in draw_table
        if type == 'figure':
            p = E.P(text)
            p.attrib['class'] = 'figure'
            # Add to body buffer
            self.active_buffer.append(self._serialize(p))

    def write_heading(self, text, bullet=None, autoAnchor=None, anchor=None,
                      level=1):
        # Use a hierarchy of header tags if docmapping set
        h = E.H1()
        if self.pis.get('docmapping', 'no') == 'yes':
            if level > 1:
                h = E.H2()
            elif level > 2:
                h = E.H3()
        if autoAnchor:
            h.attrib['id'] = autoAnchor
        if bullet:
            # Use separate elements for bullet and text
            a_bullet = E.A(bullet)
            a_bullet.tail = ' '
            if autoAnchor:
                a_bullet.attrib['href'] = '#' + autoAnchor
            h.append(a_bullet)
            if anchor:
                # Use an anchor link for heading
                a_text = E.A(text, href='#' + anchor, id=anchor)
                h.append(a_text)
            else:
                # Plain text
                a_bullet.tail += text
        else:
            # Only use one <a> pointing to autoAnchor
            a = E.A(text)
            if autoAnchor:
                a.attrib['href'] = '#' + autoAnchor
            h.append(a)
        
        # Add to body buffer
        self.active_buffer.append(self._serialize(h))

    def write_paragraph(self, text, align='left', autoAnchor=None):
        if text:
            p = E.P(text)
            if autoAnchor:
                p.attrib['id'] = autoAnchor        
            # Add to body buffer
            self.active_buffer.append(self._serialize(p))

    def write_t_rec(self, t, autoAnchor=None, align='left', parent=None):
        """ Recursively writes a <t> element

            If no parent is specified, a dummy div will be treated as the parent
            and any text will go in a <p> element.  Otherwise text and
            child elements will be insert directly into the parent -- meaning
            we are in a list
        """
        if parent is None:
            parent = self.temp_div # Dummy div
            current = E.P()
            parent.append(current)
        else:
            current = parent
        if t.text:
            current.text = t.text
            if autoAnchor:
                current.attrib['id'] = autoAnchor
        for child in t:
            if child.tag in ['xref', 'eref', 'iref', 'spanx']:
                for element in self._expand_ref(child):
                    current.append(element)
            elif child.tag == 'vspace':
                br = E.BR()
                current.append(br)
                blankLines = int(child.attrib.get('blankLines', 0))
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
        # If we are back at top level, serialize the whole temporary structure
        # Add to body buffer
        if parent == self.temp_div:
            self.active_buffer.append(self._flush_temp_div())

    def write_top(self, left_header, right_header):
        """ Buffers the header table """
        for i in range(max(len(left_header), len(right_header))):
            if i < len(left_header):
                left = left_header[i]
            else:
                left = ''
            if i < len(right_header):
                right = right_header[i]
            else:
                right = ''
                
            # Add row to header_rows buffer
            left_td = E.TD(left)
            left_td.attrib['class'] = 'left'
            right_td = E.TD(right)
            right_td.attrib['class'] = 'right'
            tr = E.TR(left_td, right_td)
            self.buffers['header_rows'].append(self._serialize(tr))

    def write_address_card(self, author):
        # Create substitution dictionary with empty string values
        vars = ['fullname', 'surname', 'role', 'organization',
                'street_spans', 'locality', 'region', 'code', 
                'locality_sep', 'region_sep', 'country', 'contact_spans']
        subs = dict(zip(vars, [''] * len(vars)))
        
        # Get values with safe defaults
        subs['fullname'] = author.attrib.get('fullname', '')
        subs['surname'] = author.attrib.get('surname', '')
        subs['role'] = author.attrib.get('role', '')
        subs['organization'] = author.find('organization') is not None and \
                               author.find('organization').text or ''
        address = author.find('address')
        
        # Crawl through optional elements
        if address is not None:
            postal = address.find('postal')
            if postal is not None:
                street_spans = []
                for street in postal.findall('street'):
                    if street.text:
                        span = self._serialize(E.SPAN(street.text))
                        street_spans.append(span)
                subs['street_spans'] = ''.join(street_spans)
                city = postal.find('city')
                if city is not None and city.text:
                    subs['locality'] = city.text
                    subs['locality_sep'] = ', '
                region = postal.find('region')
                if region is not None and region.text:
                    subs['region'] = region.text
                    subs['region_sep'] = ' '
                code = postal.find('code')
                if code is not None and code.text:
                    subs['code'] = code.text
                country = postal.find('country')
                if country is not None and country.text:
                    subs['country'] = country.text

            # Use temp div for contact spans
            contact_div = self.temp_div
            phone = address.find('phone')
            if phone is not None and phone.text:
                span = E.SPAN('Phone: ' + phone.text)
                span.attrib['class'] = 'vcardline'
                contact_div.append(span)
            fascimile = address.find('fascimile')
            if fascimile is not None and fascimile.text:
                span = E.SPAN('Fax: ' + fascimile.text)
                span.attrib['class'] = 'vcardline'
                contact_div.append(span)
            email = address.find('email')
            if email is not None and email.text:
                span = E.SPAN('EMail: ')
                span.attrib['class'] = 'vcardline'
                if self.pis.get('linkmailto', 'yes') == 'yes':
                    span.append(E.A(email.text, href='mailto:' + email.text))
                else:
                    span.text += email.text
                contact_div.append(span)
            uri = address.find('uri')
            if uri is not None and uri.text:
                span = E.SPAN('URI: ')
                span.attrib['class'] = 'vcardline'
                span.append(E.A(uri.text, href=uri.text))
                contact_div.append(span)

            # Serialize the temp div
            subs['contact_spans'] = self._flush_temp_div() 

        # Run through template and add to body buffer
        html = self.templates['address_card.html'].substitute(subs)
        self.active_buffer.append(html)

    def write_reference_list(self, list):
        tbody = E.TBODY()
        for i, reference in enumerate(list.findall('reference')):
            tr = E.TR()
            # Use anchor or num depending on PI
            if self.pis.get('symrefs', 'yes') == 'yes':
                bullet = reference.attrib.get('anchor', str(i + 1))
            else:
                bullet = str(i + 1)
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
                    if j == len(authors) - 1 and len(authors) > 1:
                        # Last author, render in reverse
                        last.tail = ' and '
                        name_string = initials + ' ' + surname 
                    else:
                        name_string = surname + ', ' + initials
                    a = E.A(name_string)
                    if email is not None and email.text:
                        if self.pis.get('linkmailto', 'yes') == 'yes':
                            a.attrib['href'] = 'mailto:' + email.text
                    if organization is not None and organization.text:
                        a.attrib['title'] = organization.text
                    ref_td.append(a)
                    last = a
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
                xml2rfc.log.warn('No title specified in reference', \
                                 reference.attrib.get('anchor', ''))
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
            # Render annotation as a separate paragraph
            annotation = reference.find('annotation')
            if annotation is not None and annotation.text:
                ref_td.append(E.P(annotation.text))
                
        # Add to body buffer
        self.active_buffer.append(self._serialize(E.TABLE(tbody)))

    def draw_table(self, table, table_num=None):
        style = 'tt full ' + table.attrib.get('align', 'center')
        cellpadding = '3'
        cellspacing = '0'
        htmltable = E.TABLE(cellpadding=cellpadding, cellspacing=cellspacing)
        htmltable.attrib['class'] = style

        # Add caption, if it exists
        if 'title' in table.attrib and table.attrib['title']:
            caption = ''
            if table_num and self.pis.get('tablecount', 'no') == 'yes':
                caption = 'Table ' + str(table_num) + ': '
            htmltable.append(E.CAPTION(caption + table.attrib['title']))

        # Draw headers
        header_row = E.TR()
        col_aligns = []
        for header in table.findall('ttcol'):
            th = E.TH()
            if header.text:
                th.text = header.text
            header_align = header.attrib.get('align', 'left')
            th.attrib['class'] = header_align
            # Store alignment information
            col_aligns.append(header_align)
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
                # Add text
                td.text = cell.text
            for child in cell:
                # Add any inline elements (references)
                for element in self._expand_ref(child):
                    td.append(element)
            # Get alignment from header
            td.attrib['class'] = col_aligns[col_num]
            tr.append(td)
        body.append(tr)  # Add final row
        htmltable.append(body)

        # Add to body buffer
        self.active_buffer.append(self._serialize(htmltable))

    def insert_anchor(self, text):
        # Add to body buffer
        self.active_buffer.append(self._serialize(E.DIV(id=text)))

    def insert_iref_index(self):
#        # Omit this element if the index is empty
#        if len(self.iref_index) > 0:
#            self.write_heading('Index', autoAnchor='index')
#            # self.add_to_toc('', 'Index', link='index')
#            dl = E.DL()
#            for iref in self.iref_index:
#                if iref[1]:
#                    dl.append(E.DT(iref[0]))
#                    dl.append(E.DD(E.A(iref[1], href='#' + '.'.join(iref))))
#                else:
#                    dl.append(E.DD(E.A(iref[0], href='#' + iref[0])))
#            self.body.append(dl)
        pass
    
    def pre_processing(self):
        # Reset buffers
        self.buffers = {'front': [],
                        'body': [],
                        'header_rows': [],
                        'toc_head_links': [],
                        'toc_rows': []}
        self.active_buffer = self.buffers['front']

    def post_processing(self):
        # Create table of contents buffers
        self._create_toc()
        
        # Grab values that haven't been inserted yet
        background_image = self.pis.get('background', '') and \
            "background-image:url('%s');" % self.pis.get('background') or ''
        title = self.r.find('front/title').text
        docName = self.r.attrib.get('docName', '')
        description = ''
        abs_t = self.r.find('front/abstract/t')
        if abs_t is not None and abs_t.text:
            description = abs_t.text
        keywords = self.r.findall('front/keyword')
        keyword_list = [keyword.text for keyword in keywords if keyword.text]
        
        # Run through base template, store in main output string
        subs = { 
                 # Replace flat values 
                 'background':      background_image,
                 'title':           title,
                 'docName':         docName,
                 'description':     description,
                 'keywords':        ', '.join(keyword_list),
                 
                 # Replace buffers
                 'front':           ''.join(self.buffers['front']),
                 'body':            ''.join(self.buffers['body']),
                 'header_rows':     ''.join(self.buffers['header_rows']),
                 'toc_head_links':  ''.join(self.buffers['toc_head_links']),
                 'toc_rows':        ''.join(self.buffers['toc_rows'])
                }
        self.output = self.templates['base.html'].substitute(subs)

    def write_to_file(self, file):
        file.write(self.output)

#-------------------------------------------------------------------------------
# Unused methods
#-------------------------------------------------------------------------------

    def write_title(self, title, docName=None):
        pass
