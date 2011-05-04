import lxml.etree
import re


class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    
    def parse(self, source):
        # Get a parser object
        parser = lxml.etree.XMLParser(dtd_validation=True, no_network=False, \
                                      remove_comments=True)
        
        # Parse the XML file into a tree and create an rfc instance
        tree = lxml.etree.parse(source, parser)
        rfc = XmlRfc(tree)

        # Finally, do any extra formatting on the RFC before returning
        rfc.prepare()
        return rfc

class XmlRfc:
    """ Internal representation of an RFC document
        
        Contains an lxml.etree.ElementTree, with some additional helper
        methods to prepare the tree for output
    """
    tree = None
    
    def __init__(self, tree):
        self.tree = tree
    
    def getroot(self):
        """ Wrapper method """
        return self.tree.getroot()
    
    def prepare(self):
        """ Prepare the RFC document for output.

            This method is automatically invoked after the xml file is
            finished being read.  It may do any of the following things:

            -- Set any necessary default values.
            -- Pre-format some elements to the proper text output.

            We can perform any operations here that will be common to all
            ouput formats.  Any further formatting is handled in the
            xml2rfc.writer modules.
        """
        root = self.getroot()
        
        root.attrib['trad_header'] = 'Network Working Group'
        if 'updates' in root.attrib:
            self.attribs['updates'] = 'Updates: ' + \
                                            root.attrib['updates']
        if 'obsoletes' in self.attribs:
            self.attribs['obsoletes'] = 'Obsoletes: ' + \
                                            self.attribs['obsoletes']
        if 'category' in self.attribs:
            if self.attribs['category'] == 'std':
                self.attribs['category'] = 'Standards-Track'
                self.attribs['status'] = \
        'This document specifies an Internet standards track protocol for ' \
        'the Internet community, and requests discussion and suggestions ' \
        'for improvements.  Please refer to the current edition of the ' \
        '"Internet Official Protocol Standards" (STD 1) for the ' \
        'standardization state and status of this protocol.  Distribution ' \
        'of this memo is unlimited.'

            elif self.attribs['category'] == 'bcp':
                self.attribs['category'] = 'Best Current Practices'
                self.attribs['status'] = \
        'This document specifies an Internet Best Current Practices for ' \
        'the Internet Community, and requests discussion and suggestions ' \
        'for improvements. Distribution of this memo is unlimited.'

            elif self.attribs['category'] == 'exp':
                self.attribs['category'] = 'Experimental Protocol'
                self.attribs['status'] = \
        'This memo defines an Experimental Protocol for the Internet ' \
        'community.  This memo does not specify an Internet standard of ' \
        'any kind.  Discussion and suggestions for improvement are ' \
        'requested. Distribution of this memo is unlimited.'

            elif self.attribs['category'] == 'historic':
                self.attribs['category'] = 'Historic'
                self.attribs['status'] = 'NONE'

            elif self.attribs['category'] == 'info':
                self.attribs['category'] = 'Informational'
                self.attribs['status'] = \
        'This memo provides information for the Internet community. This ' \
        'memo does not specify an Internet standard of any kind. ' \
        'Distribution of this memo is unlimited.'

        self.attribs['copyright'] = 'Copyright (C) The Internet Society (%s).'\
        ' All Rights Reserved.' % self['front']['date'].attribs['year']
