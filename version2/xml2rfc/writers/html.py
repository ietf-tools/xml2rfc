# Local libs
from base import XmlRfcWriter


class HtmlRfcWriter(XmlRfcWriter):
    """ Writes to an HTML with embedded CSS """

    def __init__(self, xmlrfc, width=72):
        XmlRfcWriter.__init__(self, xmlrfc)
    
    
    def write(self, filename):
        pass