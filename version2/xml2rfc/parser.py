import xml.etree.ElementTree


class Node:
    """ Single node that optionally contains text, attributes, or child nodes.

        To access child nodes, use like a dictionary, e.g. node[child] instead
        of node.children[child].

        Add child nodes by using .insert instead of [] or __setitem__,
        if a child element already exists it will convert to a list instead of
        overwriting.

    """
    text = None
    attribs = None
    children = None

    def __init__(self):
        self.text = None
        self.attribs = {}
        self.children = {}

    def __getitem__(self, key):
        return self.children[key]

    def __repr__(self):
        str = " "
        if self.text:
            str += "text=" + self.text + ", "
        if self.attribs:
            str += "attribs=" + repr(self.attribs) + ", "
        if self.children:
            str += "children=" + repr(self.children)
        return str

    def insert(self, key, node):
        if key in self.children:
            # Recurring element.  Convert to list or append to existing list.
            if isinstance(self.children[key], list):
                self.children[key].append(node)
            else:
                self.children[key] = [self.children[key], node]
            return node
        else:
            # Unique element.
            self.children[key] = node
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
        event, root = context.next()

        # Step through xml file
        for event, element in context:
            if event == "start":
                self.start(element)
            if event == "end":
                self.end()
                root.clear()  # Free memory
