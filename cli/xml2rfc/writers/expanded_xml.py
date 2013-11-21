# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import sys
import lxml.etree
import xml2rfc
import datetime

class ExpandedXmlWriter:
    """ Writes a duplicate XML file but with all references expanded """

    # Note -- we don't need to subclass BaseRfcWriter because the behavior
    # is so different and so trivial

    def __init__(self, xmlrfc, quiet=False, verbose=False, date=datetime.date.today()):
        self.root = xmlrfc.getroot()
        self.quiet = quiet
        self.verbose = verbose

    def write(self, filename):
        """ Public method to write the XML document to a file """
        # clean out entity definitions first

        element = self.root
        lines = []
        while element is not None:
            lines.append(lxml.etree.tostring(element, pretty_print=True))
            element = element.getprevious()
        lines.append("<!DOCTYPE rfc SYSTEM \"rfc2629.dtd\">\n")
        lines.append("<?xml version=\"1.0\" encoding='utf-8'?>\n")
        lines.reverse()
       
        # Use lxml's built-in serialization
        file = open(filename, 'w')
        if sys.version > '3':
            file.write(lxml.etree.tostring(self.root.getroottree(), 
                                       xml_declaration=True, 
                                       encoding='utf-8', 
                                       pretty_print=True).decode())
        else:
            foo = ''
            file.write(foo.join(lines))

        if not self.quiet:
            xml2rfc.log.write('Created file', filename)
