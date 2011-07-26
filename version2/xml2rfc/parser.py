# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

""" Public XML parser module """

import lxml.etree
import re
import datetime
import urlparse
import urllib
import os
import sys
import xml2rfc.log

__all__ = ['XmlRfcParser', 'XmlRfc']


# Static paths
cache_dir = os.path.expanduser('~/.cache/xml2rfc')
template_dir = os.path.join(os.path.dirname(xml2rfc.__file__), 'templates')


def getCacheRequest(request_url, verbose=False):
    """ Returns the local path to a cached citation from URL
    
        If the path doesnt exist yet, uses urllib to cache the file.
    """
    if not os.path.exists(cache_dir):
        if verbose:
            xml2rfc.log.write('Creating cache directory at', cache_dir)
        os.makedirs(cache_dir)
    urlobj = urlparse.urlparse(request_url)
    filename = os.path.basename(urlobj.path)
    if filename.endswith('.dtd'):
        # Found a dtd request, load from templates directory
        cached_path = os.path.join(template_dir, filename)
    elif urlobj.netloc:
        # Network entity, load from cache, or create if necessary
        cached_path = os.path.join(cache_dir, filename)
        if not os.path.exists(cached_path):
            if verbose:
                xml2rfc.log.write('Creating cache for', request_url)
            urllib.urlretrieve(request_url, cached_path)
    else:
        # Not dtd or network entity, use the absolute path that was given
        cached_path = urlobj.path
    return cached_path
        

class CachingResolver(lxml.etree.Resolver):
    def __init__(self, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet

    def resolve(self, request_url, public_id, context):
        # Get or create the cached URL request
        path = getCacheRequest(request_url, verbose=self.verbose)
        if self.verbose:
            xml2rfc.log.write('Loading resource... ', path)
        return self.resolve_filename(path, context)


class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    def __init__(self, filename, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet
        self.source = filename
        if not self.quiet:
            xml2rfc.log.write('Parsing file', self.source)

    def parse(self):
        """ Parses the source XML file and returns an XmlRfc instance """

        # Get a parser object
        parser = lxml.etree.XMLParser(dtd_validation=False,
                                      load_dtd=True,
                                      attribute_defaults=True,
                                      no_network=False,
                                      remove_comments=True,
                                      remove_pis=False,
                                      remove_blank_text=True)

        # Add our custom resolver
        parser.resolvers.add(CachingResolver(verbose=self.verbose, \
                                             quiet=self.quiet))

        # Parse the XML file into a tree and create an rfc instance
        # Bubble up any syntax errors. They will need to be handled at the
        # application level.
        try:
            tree = lxml.etree.parse(self.source, parser)
        except lxml.etree.XMLSyntaxError, error:
            raise error

        xmlrfc = XmlRfc(tree)
        
        # Evaluate processing instructions behind root element
        xmlrfc._eval_pre_pi()
        
        # Expand 'include' instructions
        # Try XML_LIBRARY variable, default to input source directory
        include_dir = os.path.expanduser(os.environ.get('XML_LIBRARY', 
                                         os.path.dirname(self.source)))
        xmlrfc._expand_includes(include_dir, verbose=self.verbose)

        # Finally, do any extra formatting on the RFC before returning
        xmlrfc._format_whitespace()

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
        """ Wrapper method to get the root of the XML tree"""
        return self.tree.getroot()

    def getpis(self):
        """ Returns a list of the XML processing instructions """
        return self.pis
    
    def validate(self, dtd_path=''):
        """ Validate the document with its default dtd, or an optional one 
        
            Return a success bool along with a list of any errors
        """
        # Load dtd from alternate path, if it was specified
        if dtd_path:
            if os.path.exists(dtd_path):
                try:
                    dtd = lxml.etree.DTD(dtd_path)
                except lxml.etree.DTDParseError, error:
                    # The DTD itself has errors
                    xml2rfc.log.error('Could not parse the dtd file:',
                                      dtd_path + '\n  ', error.message)
                    return False, []
            else:
                # Invalid path given
                xml2rfc.log.error('DTD file does not exist:', dtd_path)
                return False, []
            
        # Otherwise, use documents DTD declaration
        else:
            dtd = self.tree.docinfo.externalDTD

        if dtd is not None:
            if dtd.validate(self.getroot()):
                # The document was valid
                return True, []
            else:
                # The document was not valid
                return False, dtd.error_log
        else:
            # No explicit DTD filename OR declaration in document!
            xml2rfc.log.error('Cannot validate document, no DTD specified')
            return False, []

    def _eval_pre_pi(self):
        """ Evaluate pre-document processing instructions
        
            This will look at all processing instructions before the root node
            for initial document settings.
        """
        # Grab processing instructions from xml tree
        element = self.tree.getroot().getprevious()
        pairs = []
        while element is not None:
            if element.tag is lxml.etree.PI and element.text:
                pairs.extend(xml2rfc.utils.parse_pi(element.text))
            element = element.getprevious()
        # Initialize the PI dictionary with these values
        self.pis = dict(pairs)

    def _expand_includes(self, dir, verbose=False):
        """ Traverse the document tree and expand any 'include' instructions """
        for element in self.getroot().iter():
            if element.tag is lxml.etree.PI and element.text:
                pidict = dict(xml2rfc.utils.parse_pi(element.text))
                if 'include' in pidict and pidict['include']:
                    request = pidict['include']
                    if request.startswith('http://'):
                        # Get or create the cached URL request
                        path = getCacheRequest(request, verbose=verbose)
                    else:
                        # Try to append .xml if not in the filename
                        if not request.endswith('.xml'):
                            request += '.xml'
                        # Get the file from the given directory
                        path = os.path.join(dir, request)
                    if os.path.exists(path):
                        if verbose:
                            xml2rfc.log.write('Parsing include file', path)
                        try:
                            root = lxml.etree.parse(path).getroot()
                            element.addnext(root)
                        except lxml.etree.XMLSyntaxError, error:
                            xml2rfc.log.warn('The include file at', path,
                                             'contained an XML error and was '\
                                             'not expanded:', error.msg)
                    else:
                        xml2rfc.log.warn('Include file not found:', path)

    def _format_whitespace(self):
        """ Traverse the document tree and properly format whitespace
        
            We replace newlines with single spaces, unless it ends with a
            period then we replace the newline with two spaces.
        """
        for element in self.getroot().iter():
            # Preserve formatting on artwork
            if element.tag != 'artwork':
                if element.text is not None:
                    element.text = re.sub('\s*\n\s*', ' ', \
                                   re.sub('\.\s*\n\s*', '.  ', \
                                   element.text.lstrip()))
                    
                if element.tail is not None:
                    element.tail = re.sub('\s*\n\s*', ' ', \
                                   re.sub('\.\s*\n\s*', '.  ', \
                                   element.tail))

    def replaceUnicode(self):
        """ Traverses the RFC tree and replaces unicode characters with the
            proper equivalents specified in rfc2629-xhtml.ent.

            Writers should call this method if the entire RFC document needs to
            be ascii formatted
        """
        root = self.getroot()
        for element in root.iter():
            if element.text:
                try:
                    element.text = element.text.encode('ascii')
                except UnicodeEncodeError:
                    element.text = xml2rfc.utils.replace_unicode(element.text)
            if element.tail:
                try:
                    element.tail = element.tail.encode('ascii')
                except UnicodeEncodeError:
                    element.tail = xml2rfc.utils.replace_unicode(element.tail)
            for key in element.attrib.keys():
                try:
                    element.attrib[key] = element.attrib[key].encode('ascii')
                except UnicodeEncodeError:
                    element.attrib[key] = \
                    xml2rfc.utils.replace_unicode(element.attrib[key])
