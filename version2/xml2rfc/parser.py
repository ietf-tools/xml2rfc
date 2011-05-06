import lxml.etree
import re

class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    
    def parse(self, source):
        # Get a parser object
        parser = lxml.etree.XMLParser(dtd_validation=True, \
                                      no_network=False, \
                                      remove_comments=True, \
                                      remove_blank_text=True)
        
        # Parse the XML file into a tree and create an rfc instance
        tree = lxml.etree.parse(source, parser)
        xmlrfc = XmlRfc(tree)

        # Finally, do any extra formatting on the RFC before returning
        xmlrfc.prepare()
        return xmlrfc


class XmlRfc:
    """ Internal representation of an RFC document
        
        Contains an lxml.etree.ElementTree, with some additional helper
        methods to prepare the tree for output.
        
        Accessing the rfc tree is done by getting the root node from getroot()
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

        # Traverse the tree and strip any newlines contained in element data
        for element in root.iter():
            if element.tag != 'artwork':
                if element.text is not None:
                    element.text = re.sub('\n\s*', ' ', element.text)
                if element.tail is not None:
                    element.tail = re.sub('\n\s*', ' ', element.tail)

        root.attrib['trad_header'] = 'Network Working Group'
        if 'updates' in root.attrib:
            if root.attrib['updates'] != '':
                root.attrib['updates'] = 'Updates: ' + \
                                                root.attrib['updates']
        if 'obsoletes' in root.attrib:
            if root.attrib['obsoletes'] != '':
                root.attrib['obsoletes'] = 'Obsoletes: ' + \
                                                root.attrib['obsoletes']
        if 'category' in root.attrib:
            if root.attrib['category'] == 'std':
                root.attrib['category'] = 'Standards-Track'
                root.attrib['status'] = \
        'This document specifies an Internet standards track protocol for ' \
        'the Internet community, and requests discussion and suggestions ' \
        'for improvements.  Please refer to the current edition of the ' \
        '"Internet Official Protocol Standards" (STD 1) for the ' \
        'standardization state and status of this protocol.  Distribution ' \
        'of this memo is unlimited.'

            elif root.attrib['category'] == 'bcp':
                root.attrib['category'] = 'Best Current Practices'
                root.attrib['status'] = \
        'This document specifies an Internet Best Current Practices for ' \
        'the Internet Community, and requests discussion and suggestions ' \
        'for improvements. Distribution of this memo is unlimited.'

            elif root.attrib['category'] == 'exp':
                root.attrib['category'] = 'Experimental Protocol'
                root.attrib['status'] = \
        'This memo defines an Experimental Protocol for the Internet ' \
        'community.  This memo does not specify an Internet standard of ' \
        'any kind.  Discussion and suggestions for improvement are ' \
        'requested. Distribution of this memo is unlimited.'

            elif root.attrib['category'] == 'historic':
                root.attrib['category'] = 'Historic'
                root.attrib['status'] = 'NONE'

            elif root.attrib['category'] == 'info':
                root.attrib['category'] = 'Informational'
                root.attrib['status'] = \
        'This memo provides information for the Internet community. This ' \
        'memo does not specify an Internet standard of any kind. ' \
        'Distribution of this memo is unlimited.'

        root.attrib['copyright'] = 'Copyright (C) The Internet Society (%s).'\
        ' All Rights Reserved.' % root.find('front/date').attrib['year']


class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    xmlrfc = None
    curr_node = None
    stack = None

    def __init__(self, xmlrfc):
        self.xmlrfc = xmlrfc
        self.curr_node = self.xmlrfc
        self.stack = []

    def start(self, element):
        # Make a new node and push on top
        self.stack.append(self.curr_node)
        self.curr_node = self.curr_node.insert(element.tag, Node())
        # Add text/attrib if available
        if element.text:
            self.curr_node.text = element.text.strip().replace('\n', '')
        if element.tail:
            self.curr_node.tail = element.tail.strip().replace('\n', '')
        if element.attrib:
            self.curr_node.attribs = element.attrib

    def end(self):
        # Pop node stack
        if len(self.stack) > 0:
            self.curr_node = self.stack.pop()

    def parse(self, source):
        # Construct an iterator
        # context = iter(xml.etree.ElementTree.iterparse(source, \
        #                                           events=['start', 'end']))
        context = iter(lxml.etree.iterparse(source, events=['start', 'end']))

        # Get root from xml and set any attributes from <rfc> node
        event, root = context.next()
        if root.attrib:
            # Make shallow copy since we will delete this node.
            for key,val in root.attrib.items():
                self.xmlrfc.attribs[key] = val

        # Step through xml file
        for event, element in context:
            if event == "start":
                self.start(element)
            if event == "end":
                self.end()
                root.clear()  # Free memory

        # Finally, do any extra formatting on the RFC rfc
        self.xmlrfc.prepare()
>>>>>>> migrated to lxml parser (libxml2) instead of expat.  modified root.attrib.copy to be a manual shallow copy
