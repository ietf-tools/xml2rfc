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
template_dir = os.path.join(os.path.dirname(xml2rfc.__file__), 'templates')
default_dtd_path = os.path.join(template_dir, 'rfc2629.dtd')


def getCacheRequest(read_caches, write_cache, request_url, verbose=False,
                    source_dir='.'):
    """ Returns the local path to a cached citation from URL
    
        Unless URL is a local path, in which case it will consult $XML_LIBRARY
    
        The caches in read_dirs are consulted in sequence order to find the
        request.  If not found, the request will be cached at write_dir.
    """
    urlobj = urlparse.urlparse(request_url)
    filename = os.path.basename(urlobj.path)
    if filename.endswith('.dtd'):
        # Found a dtd request, load from templates directory
        cached_path = os.path.join(template_dir, filename)
    elif urlobj.netloc:
        # Network entity, try to load from each cache, finally downloading
        # and caching to `write_cache` if its not found.
        found = False
        for dir in read_caches:
            cached_path = os.path.join(dir, filename)
            if os.path.exists(cached_path):
                found = True
                break
        if not found:
            cached_path = os.path.join(write_cache, filename)
            xml2rfc.utils.StrictUrlOpener().retrieve(request_url, 
                                                     cached_path)
            if verbose:
                xml2rfc.log.write('Created cache for', request_url)
    else:
        # Not dtd or network entity, try `basename` in XML_LIBRARY variable, 
        # default to path of the source file
        basename = os.path.basename(urlobj.path)
        include_dir = os.path.expanduser(os.environ.get('XML_LIBRARY', 
                                         os.path.dirname(urlobj.path)))
        cached_path = os.path.join(include_dir, basename)
        if not os.path.exists(cached_path):
            cached_path = os.path.join(source_dir, filename)
    return cached_path
        

class CachingResolver(lxml.etree.Resolver):
    """ Custom ENTITY request handler that uses a local cache """
    def __init__(self, read_caches, write_cache, verbose=False, quiet=False,
                 source_dir='.'):
        self.verbose = verbose
        self.quiet = quiet
        self.source_dir = source_dir
        self.read_caches = read_caches
        self.write_cache = write_cache

    def resolve(self, request, public_id, context):
        if not request:
            # Not sure why but sometimes LXML will ask for an empty request,
            # So lets give it an empty response.
            return None
        # Get or create the cached URL request
        try:
#            # Try to append .xml if not in the filename
#            if not request.endswith('.xml'):
#                request += '.xml'
            path = getCacheRequest(self.read_caches, self.write_cache,
                                   request, verbose=self.verbose)
        except IOError, e:
            xml2rfc.log.error('Failed to load resource (' + str(e) + '):', 
                              request)
            return
        if self.verbose:
            xml2rfc.log.write('Loading resource... ', path)
        return self.resolve_filename(path, context)
            

class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    def __init__(self, filename, verbose=False, quiet=False, cache_dir=None):
        self.verbose = verbose
        self.quiet = quiet
        self.source = filename
        if not self.quiet:
            xml2rfc.log.write('Parsing file', self.source)

        # Determine cache directories to read/write to
        self.read_caches = map(os.path.expanduser, xml2rfc.CACHES)
        self.write_cache = None
        if cache_dir:
            # Explicit directory given, set it as the write directory, as well
            # as the first directory to check for reading
            self.read_caches.insert(0, cache_dir)
            self.write_cache = cache_dir
        else:
            # Try to find a valid directory to write to
            found = False
            for dir in self.read_caches:
                if os.path.exists(dir) and os.access(dir, os.W_OK):
                    self.write_cache = dir
                    break
                else:
                    try:
                        os.makedirs(dir)
                        if self.verbose:
                            xml2rfc.log.write('Created cache directory at', dir)
                        self.write_cache = dir
                    except OSError:
                        # Can't write to this directory, try the next one
                        pass
            if not self.write_cache:
                xml2rfc.log.error('Unable to find a suitible cache directory to'
                                ' write to.  Try giving a specific directory.')
                
            
                 

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
        parser.resolvers.add(CachingResolver(self.read_caches,
                                        self.write_cache,
                                        source_dir=os.path.dirname(self.source),
                                        verbose=self.verbose,
                                        quiet=self.quiet))

        # Parse the XML file into a tree and create an rfc instance
        tree = lxml.etree.parse(self.source, parser)
        xmlrfc = XmlRfc(tree)
        
        # Evaluate processing instructions behind root element
        xmlrfc._eval_pre_pi()
        
        # Expand 'include' instructions
        for element in xmlrfc.getroot().iter():
            if element.tag is lxml.etree.PI and element.text:
                pidict = dict(xml2rfc.utils.parse_pi(element.text))
                if 'include' in pidict and pidict['include']:
                    request = pidict['include']
                    # Try to append .xml if not in the filename
                    if not request.endswith('.xml'):
                        request += '.xml'
                    # Get or create the cached file request
                    try:
                        path = getCacheRequest(self.read_caches,
                                        self.write_cache, request, 
                                        verbose=self.verbose,
                                        source_dir=os.path.dirname(self.source))
                    except IOError, e:
                        xml2rfc.log.warn('Failed to load include file '
                                         '(' + str(e) + '):', request)
                        break
                    if os.path.exists(path):
                        if self.verbose:
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
    
    def validate(self, dtd_path=None):
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
            
        if not dtd:
            # No explicit DTD filename OR declaration in document!
            xml2rfc.log.warn('No DTD given, defaulting to', default_dtd_path)
            return self.validate(dtd_path=default_dtd_path)

        if dtd.validate(self.getroot()):
            # The document was valid
            return True, []
        else:
            # The document was not valid
            return False, dtd.error_log

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
