import lxml.etree
import re
import urlparse
import urllib
import os
import sys
import xml2rfc


__all__ = ['XmlRfcParser', 'XmlRfc']


class CachingResolver(lxml.etree.Resolver):
    def __init__(self, verbose=False, quiet=False, write_out=sys.stdout, \
                 write_err=sys.stderr):
        self.verbose = verbose
        self.quiet = quiet
        self.write_out = write_out
        self.write_err = write_err
        if not verbose and not self.quiet:
            self.write_out.write('Loading resources...')
            self.write_out.flush()

    def resolve(self, request_url, public_id, context):
        cache_dir = os.path.expanduser('~/.cache/xml2rfc')
        if not os.path.exists(cache_dir):
            if self.verbose:
                self.write_out.write('Creating cache directory at ' + \
                                     cache_dir + '\r\n')
            os.makedirs(cache_dir)
        template_dir = os.path.join(os.path.dirname(xml2rfc.__file__), \
                                    'templates')
        url = urlparse.urlparse(request_url)
        filename = os.path.basename(url.path)
        if filename.endswith('.dtd'):
            # Found a dtd request, load from templates directory
            resource_path = os.path.join(template_dir, filename)
        elif url.netloc:
            # Network entity, load from cache, or create if necessary
            resource_path = os.path.join(cache_dir, filename)
            if not os.path.exists(resource_path):
                if self.verbose:
                    self.write_out.write('Creating cache for ' + request_url \
                                         + '\r\n')
                urllib.urlretrieve(request_url, resource_path)
        else:
            # Not dtd or network entity, use the absolute path was given
            resource_path = url.path
        if self.verbose:
            self.write_out.write('Loading resource... ' + resource_path +
                                 '\r\n')
        elif not self.quiet:
            self.write_out.write('.')
            self.write_out.flush()
        return self.resolve_filename(resource_path, context)

class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    def __init__(self, filename, verbose=False, quiet=False, \
                 write_out=sys.stdout, write_err=sys.stderr):
        self.verbose = verbose
        self.quiet = quiet
        self.source = filename
        self.write_out = write_out
        self.write_err = write_err

    def parse(self, prepare=True):
        """ Parses the source XML file and returns an XmlRfc instance """

        # Get a parser object
        parser = lxml.etree.XMLParser(dtd_validation=True, \
                                      no_network=False, \
                                      remove_comments=True, \
                                      remove_blank_text=True)

        # Add our custom resolver
        parser.resolvers.add(CachingResolver(verbose=self.verbose, \
                                             quiet=self.quiet, \
                                             write_out=self.write_out, \
                                             write_err=self.write_err))

        # Parse the XML file into a tree and create an rfc instance
        # Bubble up any validation or syntax errors. They will need to be
        # handled in the CLI script or GUI.
        try:
            tree = lxml.etree.parse(self.source, parser)
        except lxml.etree.XMLSyntaxError, error:
            raise error

        if not self.verbose and not self.quiet:
            # Add a newline since the resolver never added one
            self.write_out.write('\r\n')

        xmlrfc = XmlRfc(tree)

        # Finally, do any extra formatting on the RFC before returning
        if prepare:
            xmlrfc.prepare()
        return xmlrfc


class XmlRfc:
    """ Internal representation of an RFC document

        Contains an lxml.etree.ElementTree, with some additional helper
        methods to prepare the tree for output.

        Accessing the rfc tree is done by getting the root node from getroot()
    """

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
                    element.text = re.sub('\n\s*', ' ', element.text.lstrip())
                if element.tail is not None:
                    element.tail = re.sub('\n\s*', ' ', element.tail.rstrip())

        # Set some document-independent defaults
        root.attrib['trad_header'] = 'Network Working Group'
        if 'updates' in root.attrib and root.attrib['updates']:
            root.attrib['updates'] = 'Updates: ' + root.attrib['updates']
        if 'obsoletes' in root.attrib and root.attrib['obsoletes']:
            root.attrib['obsoletes'] = 'Obsoletes: ' + root.attrib['obsoletes']
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

        year = root.find('front/date').attrib.get('year', '')
        root.attrib['copyright'] = 'Copyright (C) The Internet Society (%s).'\
        ' All Rights Reserved.' % year

    def replaceUnicode(self):
        """ Traverses the RFC tree and replaces unicode characters with the
            proper equivalents specified in rfc2629-xhtml.ent.  Writers should
            call this method if the entire RFC document needs to be ascii
            formattable
        """
        root = self.getroot()
        for element in root.iter():
            if element.text:
                try:
                    element.text = str(element.text)
                except UnicodeEncodeError:
                    element.text = xml2rfc.utils.replace_unicode(element.text)
            if element.tail:
                try:
                    element.tail = str(element.tail)
                except UnicodeEncodeError:
                    element.tail = xml2rfc.utils.replace_unicode(element.tail)
