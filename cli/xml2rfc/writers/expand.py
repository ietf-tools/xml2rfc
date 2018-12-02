# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from io import open
from lxml import etree

from xml2rfc.writers.base import BaseV3Writer
from xml2rfc import log

class ExpandV3XmlWriter(BaseV3Writer):
    """ Writes a duplicate XML file but with all includes expanded """

    # Note -- we don't need to subclass BaseRfcWriter because the behavior
    # is so different and so trivial

    def write(self, filename):
        """ Public method to write the XML document to a file """

        version = self.root.get('version', '3')
        if version not in ['3', ]:
            self.die(self.root, 'Expected <rfc> version="3", but found "%s"' % version)

        try:
            self.tree.xinclude()
        except etree.XIncludeError as e:
            self.die(None, "XInclude processing failed: %s" % e)

        self.pretty_print_prep(self.root, None)

        # Use lxml's built-in serialization
        # Use lxml's built-in serialization
        file = open(filename, 'w', encoding='utf-8')

        text = etree.tostring(self.tree,
                                xml_declaration=True, 
                                encoding='utf-8',
                                pretty_print=True)
        file.write(text.decode('utf-8'))

        if not self.options.quiet:
            log.write('Created file', filename)

            
