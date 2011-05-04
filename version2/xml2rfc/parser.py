import xml.etree.ElementTree

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
                 'figure',
                 'list',
                 'reference',
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
    attribs = None
    _children = None

    def __init__(self):
        self.text = None
        self.attribs = {}
        self._children = {}

    def __getitem__(self, key):
        return self._children[key]

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
            # Unique element.
        else:
            if key in self._children:
                raise Exception("Element " + key + " is already defined!")
            else:
                self._children[key] = node
        return node


class XmlRfcTree(Node):
    """ Internal representation of an RFC document constructed from XML """


class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    tree = None
    curr_node = None
    stack = None

    def __init__(self, xmlrfc_tree):
        self.tree = xmlrfc_tree
        self.curr_node = self.tree
        self.stack = []

    def start(self, element):
        # Make a new node and push on top
        self.stack.append(self.curr_node)
        self.curr_node = self.curr_node.insert(element.tag, Node())
        # Add text/attrib if available
        if element.text:
            self.curr_node.text = element.text.strip()
        if element.attrib:
            self.curr_node.attribs = element.attrib

    def end(self):
        # Pop node stack
        if len(self.stack) > 0:
            self.curr_node = self.stack.pop()

    def parse(self, source):
        # Construct an iterator
        context = iter(xml.etree.ElementTree.iterparse(source, \
                                                    events=['start', 'end']))
        
        # Get root from xml and set any attributes from <rfc> node
        event, root = context.next()
        if root.attrib:
            self.tree.attribs = root.attrib

        # Step through xml file
        for event, element in context:
            if event == "start":
                self.start(element)
            if event == "end":
                self.end()
                root.clear()  # Free memory
