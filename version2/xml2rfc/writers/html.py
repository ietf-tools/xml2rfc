# External libs
import lxml.builder
import lxml.etree

# Local libs
from raw_txt import RawTextRfcWriter

# HTML Specific Defaults that are not provided in XML document
# TODO: This could possibly go in parser.py, as a few defaults already do.
defaults =  {'style_title':  'Xml2Rfc (sans serif)',
            }

class HtmlRfcWriter(RawTextRfcWriter):
    """ Writes to an HTML with embedded CSS """

    def __init__(self, xmlrfc, css_document='templates/rfc.css',
                 expanded_css=True, lang='en'):
        RawTextRfcWriter.__init__(self, xmlrfc)
        self.html = lxml.builder.E.html()
        self.html.attrib['lang'] = lang
        self.css_document = css_document
        self.expanded_css = expanded_css
        
    def build_stylesheet(self):
        """ Returns either a <link> or <style> element for css data.
        
            The element returned is dependent on the value of expanded_css
        """
        if self.expanded_css:
            file = open(self.css_document, 'r')
            element = lxml.builder.E.style(file.read())
            element.attrib['title'] = defaults['style_title']
        else:
            element = lxml.builder.E.link()
            element.attrib['rel'] = 'stylesheet'
            element.attrib['href'] = self.css_document
        element.attrib['type'] = 'text/css'
        return element
        
    def build_tree(self):
        """ Builds an lxml HTML Element Tree from the RFC tree instance """
        # Build head
        head = lxml.builder.E.head()
        head.append(self.build_stylesheet())
        self.html.append(head)
    
    def write(self, filename):
        # Consruct the HTML tree with lxml
        self.build_tree()
        
        # Write the tree to the file
        file = open(filename, 'w')
        file.write(lxml.etree.tostring(self.html, pretty_print=True))
