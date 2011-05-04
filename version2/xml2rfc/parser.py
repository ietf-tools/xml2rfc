import lxml.etree

# Defines names for all RFC elements that may appear more than once, so that
# we may store them as lists.
multi_elements = ['author',
                 'street',
                 'area',
                 'workgroup',
                 'keyword',
                 'note',
                 'section',
                 't',
                 'ttcol',
                 'c',
                 'figure',
                 'list',
                 'references',
                 'reference',
                 'seriesInfo',
                 'format',
                 'annotation'
                 ]


class Node:
    """ Single node that optionally contains text, attributes, or child nodes.

        Children can be single nodes, or lists of nodes.

        To access child nodes, use like a dictionary, e.g. node[child] instead
        of node._children[child].

        Add child nodes by using .insert instead of [] or __setitem__,
        if a child element already exists it will convert to a list instead of
        overwriting.
    """
    text = None
    tail = None
    attribs = None
    _children = None

    def __init__(self, text=None, tail=None):
        self.text = text
        self.tail = tail
        self.attribs = {}
        self._children = {}

    def __getitem__(self, key):
        if key not in self._children:
            if key in multi_elements:
                # Return an empty list instead of error
                self._children[key] = []
            else:
                raise KeyError("Key doesn't exist: " + str(key))
        return self._children[key]

    def __contains__(self, key):
        return key in self._children

    def __setitem__(self, key, val):
        self._children[key] = val

    def __repr__(self):
        str = " "
        if self.text:
            str += "text=" + self.text + ", "
        if self.attribs:
            str += "attribs=" + repr(self.attribs) + ", "
        if self._children:
            str += "_children=" + repr(self._children)
        return str

    def insert(self, key, node):
        # Check if the element is a single or multiple type
        if key in multi_elements:
            if key in self._children:
                self._children[key].append(node)
            else:
                self._children[key] = [node]
        else:
            if key in self._children:
                raise Exception("Element " + key + " is already defined!")
            else:
                self._children[key] = node
        return node


class XmlRfc(Node):
    """ Internal representation of an RFC document constructed from XML """
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
        self.attribs['trad_header'] = 'Network Working Group'
        if 'updates' in self.attribs:
            self.attribs['updates'] = 'Updates: ' + \
                                            self.attribs['updates']
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


class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    xmlrfc = None
    curr_node = None
    stack = None
    tail_switch = None

    def __init__(self, xmlrfc):
        self.xmlrfc = xmlrfc
        self.curr_node = self.xmlrfc
        self.stack = []
        self.tail_switch = False

    def parse(self, source):
        # Get a parser object
        parser = lxml.etree.XMLParser(dtd_validation=True, no_network=False, \
                                      target=self)
        
        # Parse the XML file -- RFC tree is constructed through callbacks
        lxml.etree.parse(source, parser)

        # Finally, do any extra formatting on the RFC tree
        self.xmlrfc.prepare()

    def start(self, tag, attrib):
        # Start of an element -- flip switch so any data goes in node.text
        self.tail_switch = False
        if tag == 'rfc':
            # Root node -- don't push to stack, this way we avoid using ['rfc']
            self.curr_node = self.xmlrfc
        else:
            # Make a new node and push previous to stack
            self.stack.append(self.curr_node)
            self.curr_node = self.curr_node.insert(tag, Node())
        # Add attribs, if any
        if attrib:
            self.curr_node.attribs = attrib
    
    def end(self, tag):
        # End of an element -- flip switch so any data goes in node.tail
        self.tail_switch = True
        # Pop node stack
        if len(self.stack) > 0:
            self.curr_node = self.stack.pop()
    
    def data(self, data):
        # Set data depending on if we're in the head or tail section
        if self.tail_switch:
            self.curr_node.tail = data
        else:
            self.curr_node.text = data
    
    def comment(self, comment):
        pass # No need to handle comments
    
    def close(self):
        return "XML file closed"
