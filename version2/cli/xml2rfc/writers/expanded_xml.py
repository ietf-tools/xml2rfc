# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import lxml.etree
import xml2rfc


class ExpandedXmlWriter:
    """ Writes a duplicate XML file but with all references expanded """

    # Note -- we don't need to subclass BaseRfcWriter because the behavior
    # is so different and so trivial

    def __init__(self, xmlrfc, quiet=False, verbose=False):
        self.root = xmlrfc.getroot()
        self.quiet = quiet
        self.verbose = verbose

    def write(self, filename):
        """ Public method to write the XML document to a file """
        # Use lxml's built-in serialization
        file = open(filename, 'w')
        # Assemble elements before root node
        pre = []
        element = self.root.getprevious()
        while element is not None:
            pre.append(element)
            element = element.getprevious()
        # Serialize pre-elements in reverse order
        for i in range(len(pre)):
            j = len(pre) - i - 1
            file.write(lxml.etree.tostring(pre[j], pretty_print=True))
        # Serialize main tree
        file.write(lxml.etree.tostring(self.root, pretty_print=True))

        if not self.quiet:
            xml2rfc.log.write('Created file', filename)
