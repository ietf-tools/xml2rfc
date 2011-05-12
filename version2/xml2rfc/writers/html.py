# External libs
from lxml.builder import E
import lxml.etree

# Local libs
from raw_txt import RawTextRfcWriter

# HTML Specific Defaults that are not provided in XML document
# TODO: This could possibly go in parser.py, as a few defaults already do.
defaults =  {'doctype': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">',
             'style_title':  'Xml2Rfc (sans serif)',
            }

class HtmlRfcWriter(RawTextRfcWriter):
    """ Writes to an HTML with embedded CSS """

    def __init__(self, xmlrfc, css_document='templates/rfc.css',
                 expanded_css=True, lang='en'):
        RawTextRfcWriter.__init__(self, xmlrfc)
        self.html = E.html(lang=lang)
        self.css_document = css_document
        self.expanded_css = expanded_css
        
    def build_stylesheet(self):
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
    
    def build_head(self):
        """ Returns the constructed <head> element """
        head = E.head()
        head.append(self.build_stylesheet())
        return head
    
    def build_header(self):
        """ Returns the header table """
        table = E.table()
        table.attrib['class'] = 'header'
        tbody = E.tbody()
        # Use RawTextWriter methods to construct header
        header_left = self.prepare_top_left()
        header_right = self.prepare_top_right()
        for i in range(max(len(header_left), len(header_right))):
            if i < len(header_left):
                left_string = header_left[i]
            else:
                left_string = ''
            if i < len(header_right):
                right_string = header_right[i]
            else:
                right_string = ''
            td_left = E.td(left_string)
            td_left.attrib['class'] = 'left'
            td_right = E.td(right_string)
            td_right.attrib['class'] = 'right'
            tbody.append(E.tr(td_left, td_right))
        table.append(tbody)
        return table

    def build_t_tree(self, t):
        """ Returns an HTML element tree from an XML <t> node """
        p = E.p(t.text)
        return p
    
    def build_body(self):
        """ Returns the constructed <body> element """
        body = E.body()
        
        # Header
        body.append(self.build_header())
        
        # Title
        title = E.p(self.r.find('front/title').text)
        title.attrib['class'] = 'title'
        title.append(E.br())
        if 'docName' in self.r.attrib:
            filename = E.span(self.r.attrib['docName'])
            filename.attrib['class'] = 'filename'
            title.append(filename)
        body.append(title)
        
        # Abstract
        abstract = self.r.find('front/abstract')
        if abstract is not None:
            body.append(E.h1(E.a('Abstract', href='#rfc.abstract'), \
                             id='rfc.abstract'))
            for t in abstract.findall('t'):
                body.append(self.build_t_tree(t))

        # Status
        body.append(E.h1(E.a('Status of this Memo', href='#rfc.status'), \
                         id='rfc.status'))
        body.append(E.p(self.r.attrib['status']))

        # Copyright
        body.append(E.h1(E.a('Copyright Notice', href='#rfc.copyrightnotice'), \
                         id='rfc.copyrightnotice'))
        body.append(E.p(self.r.attrib['copyright']))
        
        # Finished
        return body

    def build_tree(self):
        """ Builds an lxml HTML Element Tree from the RFC tree instance """
        self.html.append(self.build_head())
        self.html.append(self.build_body())
    
    def write(self, filename):
        # Consruct the HTML tree with lxml
        self.build_tree()
        
        # Write the tree to the file
        file = open(filename, 'w')
        file.write(defaults['doctype'] + '\n')
        file.write(lxml.etree.tostring(self.html, pretty_print=True))
