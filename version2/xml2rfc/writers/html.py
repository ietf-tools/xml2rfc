# External libs
import lxml.builder
import lxml.etree

# Local libs
from raw_txt import RawTextRfcWriter


class HtmlRfcWriter(RawTextRfcWriter):
    """ Writes to an HTML with embedded CSS """

    def __init__(self, xmlrfc, width=72):
        RawTextRfcWriter.__init__(self, xmlrfc)
        self.html = lxml.builder.E.html()
        
    def build_tree(self):
        """ Builds an lxml HTML Element Tree from the RFC tree instance """
    
    def write(self, filename):
        # Consruct the HTML tree with lxml
        self.build_tree()
        
        # Write the tree to the file
        file = open(filename, 'w')
        file.write(lxml.etree.tostring(self.html, pretty_print=True))
