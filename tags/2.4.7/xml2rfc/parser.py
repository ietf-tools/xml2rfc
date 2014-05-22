# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

""" Public XML parser module """

import lxml.etree
import re
import os
import shutil
import xml2rfc.log

try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse, urljoin
try:
    import debug
    assert debug
except ImportError:
    pass

__all__ = ['XmlRfcParser', 'XmlRfc', 'XmlRfcError']


class XmlRfcError(Exception):
    """ Application XML errors with positional information
    
        This class attempts to mirror the API of lxml's error class
    """
    def __init__(self, msg, filename=None, line_no=0):
        self.msg = msg
        # This mirrors lxml error behavior, but we can't capture column
        self.position = (line_no, 0)
        # Also match lxml.etree._LogEntry attributes:
        self.message = msg
        self.filename = filename
        self.line = line_no

class CachingResolver(lxml.etree.Resolver):
    """ Custom ENTITY request handler that uses a local cache """
    def __init__(self, cache_path=None, library_dirs=None, source=None,
                 templates_path='templates', verbose=False, quiet=False,
                 network_locs= [
                     'http://xml2rfc.ietf.org/public/rfc/',
                     'http://xml2rfc.tools.ietf.org/public/rfc/',
                     'http://xml.resource.org/public/rfc/',
                 ],
                 rfc_number=None):
        self.verbose = verbose
        self.quiet = quiet
        self.source = source
        self.library_dirs = library_dirs
        self.templates_path = templates_path
        self.network_locs = network_locs
        self.include = False
        self.rfc_number = rfc_number

        # Get directory of source
        self.source_dir = os.path.abspath(os.path.dirname(self.source))

        # Determine cache directories to read/write to
        self.read_caches = [ os.path.expanduser(path) for path in xml2rfc.CACHES ]
        self.write_cache = None
        if cache_path:
            # Explicit directory given, set as first directory in read_caches
            self.read_caches.insert(0, cache_path)
        # Try to find a valid directory to write to by stepping through
        # Read caches one by one
        for dir in self.read_caches:
            if os.path.exists(dir) and os.access(dir, os.W_OK):
                self.write_cache = dir
                break
            else:
                try:
                    os.makedirs(dir)
                    xml2rfc.log.note('Created cache directory at', dir)
                    self.write_cache = dir
                except OSError:
                    # Can't write to this directory, try the next one
                    pass
        if not self.write_cache:
            xml2rfc.log.warn('Unable to find a suitible cache directory to '
                            'write to, trying the following directories:\n ',
                            '\n  '.join(self.read_caches),
                            '\nTry giving a specific directory with --cache.')
        else:
            # Create the prefix directory if it doesnt exist
            pdir = os.path.join(self.write_cache, xml2rfc.CACHE_PREFIX)
            if not os.path.exists(pdir):
                os.makedirs(pdir)
                
    def delete_cache(self, path=None):
        # Explicit path given?
        caches = path and [path] or self.read_caches
        for dir in caches:
            path = os.path.join(dir, xml2rfc.CACHE_PREFIX)
            if os.access(path, os.W_OK):
                shutil.rmtree(path)
                xml2rfc.log.write('Deleted cache directory at', path)

    def resolve(self, request, public_id, context):
        """ Called internally by lxml """
        if not request:
            # Not sure why but sometimes LXML will ask for an empty request,
            # So lets give it an empty response.
            return None
        # If the source itself is requested, return as-is
        if request == self.source:
            return self.resolve_filename(request, context)
        if request == u"internal:/rfc.number":
            if self.rfc_number:
                return self.resolve_string(self.rfc_number, context)
            return self.resolve_string("XXXX", context)
        if not urlparse(request).netloc:
            # Format the request from the relative path of the source so that 
            # We get the exact same path as in the XML document
            if request.startswith("file:///"):
                request = request[8:]
            try:
                request = os.path.relpath(request, self.source_dir)
            except ValueError:
                pass
        path = self.getReferenceRequest(request)
        return self.resolve_filename(path, context)
    
    def getReferenceRequest(self, request, include=False, line_no=0):
        """ Returns the correct and most efficient path for an external request

            To determine the path, the following algorithm is consulted:

            If REQUEST ends with '.dtd' or '.ent' then
              If REQUEST is an absolute path (local or network) then
                Return REQUEST
            Else
              Try TEMPLATE_DIR + REQUEST, otherwise
              Return SOURCE_DIR + REQUEST
            Else
              If REQUEST doesn't end with '.xml' then append '.xml'
              If REQUEST is an absolute path (local or network) then
                Return REQUEST
              Else
                If REQUEST contains intermediate directories then
                  Try each directory in LOCAL_LIB_DIRS + REQUEST, otherwise
                  Try NETWORK + REQUEST
                Else (REQUEST is simply a filename)
                  [Recursively] Try each directory in LOCAL_LIB_DIRS + REQUEST, otherise
                  Try each explicit (bibxml, bibxml2...) subdirectory in NETWORK + REQUEST

            Finally if the path returned is a network URL, use the cached
            version or create a new cache.
           
            - REQUEST refers to the full string of the file asked for,
            - TEMPLATE_DIR refers to the applications 'templates' directory,
            - SOURCE_DIR refers to the directory of the XML file being parsed
            - LOCAL_LIB_DIRS refers to a list of local directories to consult,
              on the CLI this is set by $XML_LIBRARY, defaulting to 
              ['/usr/share/xml2rfc'].  On the GUI this can be configured
              manually but has the same initial defaults.
            - NETWORK refers to the online citation library.  On the CLI this
              is http://xml.resource.org/public/rfc/.  On the GUI this 
              can be configured manually but has the same initial default.

            The caches in read_dirs are consulted in sequence order to find the
            request.  If not found, the request will be cached at write_dir.

            This method will throw an lxml.etree.XMLSyntaxError to be handled
            by the application if the reference cannot be properly resolved
        """
        self.include = include # include state
        tried_cache = False
        attempts = []  # Store the attempts
        original = request  # Used for the error message only
        result = None  # Our proper path
        if request.endswith('.dtd') or request.endswith('.ent'):
            if os.path.isabs(request) or urlparse(request).netloc:
                # Absolute request, return as-is
                attempts.append(request)
                result = request
            else:
                basename = os.path.basename(request)
                # Look for dtd in templates directory
                attempt = os.path.join(self.templates_path, basename)
                attempts.append(attempt)
                if os.path.exists(attempt):
                    result = attempt
                else:
                    # Default to source directory
                    result = os.path.join(self.source_dir, basename)
                    attempts.append(result)
        else:
            if request.endswith('.xml'):
                paths = [ request ]
            else:
                paths = [ request, request + '.xml' ]
            if os.path.isabs(paths[0]):
                # Absolute path, return as-is
                for path in paths:
                    attempts.append(path)
                    result = path
                    if os.path.exists(path):
                        break
            elif urlparse(paths[0]).netloc:
                # URL requested, cache it
                origloc = urlparse(paths[0]).netloc
                if True in [ urlparse(loc).netloc == urlparse(paths[0]).netloc for loc in self.network_locs ]:
                    for loc in self.network_locs:
                        newloc = urlparse(loc).netloc
                        for path in paths:
                            path = path.replace(origloc, newloc)
                            attempts.append(path)
                            result = self.cache(path)
                            if result:
                                break
                        if result:
                            break
                else:
                    for path in paths:
                        attempts.append(path)
                        result = self.cache(path)
                        if result:
                            break
                tried_cache = True
            else:
                if os.path.dirname(paths[0]):
                    # Intermediate directories, only do flat searches
                    for dir in self.library_dirs:
                        # Try local library directories
                        for path in paths:
                            attempt = os.path.join(dir, path)
                            attempts.append(attempt)
                            if os.path.exists(attempt):
                                result = attempt
                                break
                    if not result:
                        # Try network location
                        for loc in self.network_locs:
                            for path in paths:
                                url = urljoin(loc, path)
                                attempts.append(url)
                                result = self.cache(url)
                                if result:
                                    break
                            if result:
                                break
                        tried_cache = True
                        # if not result:
                        #     # Document didn't exist, default to source dir
                        #     result = os.path.join(self.source_dir, request)
                        #     attempts.append(result)
                else:
                    # Hanging filename
                    for dir in self.library_dirs:
                        # NOTE: Recursion can be implemented here
                        # Try local library directories
                        for path in paths:
                            attempt = os.path.join(dir, path)
                            attempts.append(attempt)
                            if os.path.exists(attempt):
                                result = attempt
                                break
                    if not result:
                        # Try network subdirs
                        for subdir in xml2rfc.NET_SUBDIRS:
                            for loc in self.network_locs:
                                for path in paths:
                                    url = urljoin(loc, subdir + '/' + path)
                                    attempts.append(url)
                                    result = self.cache(url)
                                    if result:
                                        break
                                if result:
                                    break
                            tried_cache = True
                            if result:
                                break
                    # if not result:
                    #     # Default to source dir
                    #     result = os.path.join(self.source_dir, request)
                    #     attempts.append(result)

        # Verify the result -- either raise exception or return it
        if not os.path.exists(result) and not urlparse(result).netloc:
            if os.path.isabs(original):
                xml2rfc.log.warn('A reference was requested with an absolute path, but not found '
                    'in that location.  Removing the path component will cause xml2rfc to look for'
                    'the file automatically in standard locations.')
            # Couldn't resolve.  Throw an exception
            error = XmlRfcError('Unable to resolve external request: '
                                      + '"' + original + '"', line_no=line_no, filename=self.source)
            if self.verbose and len(attempts) > 1:
                # Reveal attemps
                error.msg += ', trying the following location(s):\n    ' + \
                             '\n    '.join(attempts)
            raise error
        else:
            if not tried_cache:
                # Haven't printed a verbose messsage yet
                typename = self.include and 'include' or 'entity'
                xml2rfc.log.note('Resolving ' + typename + '...', result)
            return result

    def cache(self, url):
        """ Return the path to a cached URL

            Checks for the existence of the cache and creates it if necessary.
        """
        basename = os.path.basename(urlparse(url).path)
        typename = self.include and 'include' or 'entity'
        # Try to load the URL from each cache in `read_cache`
        for dir in self.read_caches:
            cached_path = os.path.join(dir, xml2rfc.CACHE_PREFIX, basename)
            if os.path.exists(cached_path):
                xml2rfc.log.note('Resolving ' + typename + '...', url)
                xml2rfc.log.note('Loaded from cache', cached_path)
                return cached_path
        # Not found, save to `write_cache`
        if self.write_cache:
            write_path = os.path.join(self.write_cache, 
                                      xml2rfc.CACHE_PREFIX, basename)
            try:
                xml2rfc.log.note('Resolving ' + typename + '...', url)
                xml2rfc.utils.StrictUrlOpener().retrieve(url, write_path)
                xml2rfc.log.note('Created cache at', write_path)
                return write_path
            except IOError as e:
                # Invalid URL -- Error will be displayed in getReferenceRequest
                xml2rfc.log.note("I/O Error: %s" % e)
                return ''
        # No write cache available, test existance of URL and return
        else:
            try:
                xml2rfc.log.write('Resolving ' + typename + '...', url)
                xml2rfc.utils.StrictUrlOpener().open(url)
                return url
            except IOError as e:
                # Invalid URL
                xml2rfc.log.note("I/O Error: %s" % e)
                return ''

class XmlRfcParser:

    """ XML parser container with callbacks to construct an RFC tree """
    def __init__(self, source, verbose=False, quiet=False,
                 cache_path=None, templates_path=None, library_dirs=None,
                 network_locs=[
                     'http://xml2rfc.ietf.org/public/rfc/',
                     'http://xml2rfc.tools.ietf.org/public/rfc/',
                     'http://xml.resource.org/public/rfc/',
                 ]
                 ):
        self.verbose = verbose
        self.quiet = quiet
        self.source = source
        self.cache_path = cache_path
        self.network_locs = network_locs

        # Initialize templates directory
        self.templates_path = templates_path or \
                              os.path.join(os.path.dirname(xml2rfc.__file__),
                                           'templates')
        self.default_dtd_path = os.path.join(self.templates_path, 'rfc2629.dtd')

        # If library dirs werent explicitly set, like from the gui, then try:
        #   1. $XML_LIBRARY environment variable as a delimited list
        #   2. Default to /usr/share/xml2rfc
        # Split on colon or semi-colon delimiters
        if not library_dirs:
            library_dirs = os.environ.get('XML_LIBRARY', '/usr/share/xml2rfc:')
        self.library_dirs = []
        for raw_dir in re.split(':|;', library_dirs):
            # Convert empty directory to source dir
            if raw_dir == '': 
                raw_dir = os.path.abspath(os.path.dirname(self.source))
            else:
                raw_dir = os.path.normpath(os.path.expanduser(raw_dir))
            # Add dir if its unique
            if raw_dir not in self.library_dirs:
                self.library_dirs.append(raw_dir)

        # Initialize the caching system.  We'll replace this later if parsing.
        self.cachingResolver = CachingResolver(cache_path=self.cache_path,
                                        library_dirs=self.library_dirs,
                                        templates_path=self.templates_path,
                                        source=self.source,
                                        network_locs=self.network_locs,
                                        verbose=self.verbose,
                                        quiet=self.quiet,
                                    )

    def delete_cache(self, path=None):
        self.cachingResolver.delete_cache(path=path)

    def parse(self, remove_comments=True, remove_pis=False, quiet=False, strip_cdata=True):
        """ Parses the source XML file and returns an XmlRfc instance """
        if not (self.quiet or quiet):
            xml2rfc.log.write('Parsing file', self.source)

        # Get an iterating parser object
        context = lxml.etree.iterparse(self.source,
                                      dtd_validation=False,
                                      load_dtd=True,
                                      attribute_defaults=True,
                                      no_network=False,
                                      remove_comments=remove_comments,
                                      remove_pis=remove_pis,
                                      remove_blank_text=True,
                                      resolve_entities=False,
                                      strip_cdata=strip_cdata,
                                      events=("start",),
                                      tag="rfc",
                                  )
        # resolver without knowledge of rfc_number:
        caching_resolver = CachingResolver(cache_path=self.cache_path,
                                        library_dirs=self.library_dirs,
                                        templates_path=self.templates_path,
                                        source=self.source,
                                        network_locs=self.network_locs,
                                        verbose=self.verbose,
                                        quiet=self.quiet,
                                    )
        context.resolvers.add(caching_resolver)

        # Get hold of the rfc number (if any) in the rfc element, so we can
        # later resolve the "&rfc.number;" entity.
        try:
            for action, element in context:
                if element.tag == "rfc":
                    self.rfc_number = element.attrib.get("number", None)
        except lxml.etree.XMLSyntaxError as e:
            xml2rfc.log.warn("Parsing Error: %s" % e)
            self.rfc_number = None

        # now get a regular parser, and parse again, this time resolving entities
        parser = lxml.etree.XMLParser(dtd_validation=False,
                                      load_dtd=True,
                                      attribute_defaults=True,
                                      no_network=False,
                                      remove_comments=remove_comments,
                                      remove_pis=remove_pis,
                                      remove_blank_text=True,
                                      resolve_entities=True,
                                      strip_cdata=strip_cdata)

        # Initialize the caching system
        self.cachingResolver = CachingResolver(cache_path=self.cache_path,
                                        library_dirs=self.library_dirs,
                                        templates_path=self.templates_path,
                                        source=self.source,
                                        network_locs=self.network_locs,
                                        verbose=self.verbose,
                                        quiet=self.quiet,
                                        rfc_number = self.rfc_number,
                                    )

        # Add our custom resolver
        parser.resolvers.add(self.cachingResolver)

        # Parse the XML file into a tree and create an rfc instance
        tree = lxml.etree.parse(self.source, parser)
        xmlrfc = XmlRfc(tree, self.default_dtd_path)
        
        # Evaluate processing instructions behind root element
        xmlrfc._eval_pre_pi()
        
        # Expand 'include' instructions
        for element in xmlrfc.getroot().iter():
            if element.tag is lxml.etree.PI:
                pidict = xmlrfc.parse_pi(element)
                if 'include' in pidict and pidict['include']:
                    request = pidict['include']
                    path = self.cachingResolver.getReferenceRequest(request,
                           # Pass the line number in XML for error bubbling
                           include=True, line_no=getattr(element, 'sourceline', 0))
                    try:
                        # Parse the xml and attach it to the tree here
                        parser = lxml.etree.XMLParser(load_dtd=False,
                                                      no_network=False,
                                                      remove_comments=remove_comments,
                                                      remove_pis=remove_pis,
                                                      remove_blank_text=True,
                                                      resolve_entities=True,
                                                      strip_cdata=strip_cdata)
                        # parser.resolvers.add(self.cachingResolver) --- should this be done?
                        ref_root = lxml.etree.parse(path, parser).getroot()
                        parent = element.getparent()
                        parent.replace(element, ref_root)
                    except (lxml.etree.XMLSyntaxError, IOError) as e:
                        if e is lxml.etree.XMLSyntaxError:
                            xml2rfc.log.warn('The include file at', path,
                                             'contained an XML error and was '\
                                             'not expanded:', e.msg)
                        else:
                            xml2rfc.log.warn('Unable to load the include file at',
                                              path)

        # Finally, do any extra formatting on the RFC before returning
        xmlrfc._format_whitespace()

        return xmlrfc

class XmlRfc:
    """ Internal representation of an RFC document

        Contains an lxml.etree.ElementTree, with some additional helper
        methods to prepare the tree for output.

        Accessing the rfc tree is done by getting the root node from getroot()
    """

    def __init__(self, tree, default_dtd_path):
        self.default_dtd_path = default_dtd_path
        self.tree = tree
        # Pi default values
        self.pis = {
            "artworkdelimiter":	None,
            "artworklines":	0 ,
            "authorship":	"yes",
            "autobreaks":	"yes",
            "background":	"" ,
            "colonspace":	"no" ,
            "comments":		"no" ,
            "docmapping":	"no",
            "editing":		"no",
            "emoticonic":	"no",
            #"footer":		Unset
            "figurecount":      "no",
            #"header":		Unset
            "inline":		"no",
            "iprnotified":	"no",
            "linkmailto":	"yes",
            #"linefile":	Unset
            #"needLines":       Unset
            "multiple-initials":"no",
            "notedraftinprogress": "yes",
            "private":		"",
            "refparent":	"References",
            "rfcedstyle":	"no",
            "rfcprocack":	"no",
            "sectionorphan":    4,
            "slides":		"no",
            "sortrefs":		"no",
            "strict":		"no",
            "symrefs":		"yes",
            "tablecount":       "no",
            "text-list-symbols": "o*+-",
            "toc":		"no",
            "tocappendix":	"yes",
            "tocdepth":		3,
            "tocindent":	"yes",
            "tocnarrow":	"yes",
            "tocompact":	"yes",
            "topblock":		"yes",
            #"typeout":		Unset
            "useobject":	"no" ,
        }
        # Special cases:
        self.pis["compact"] = self.pis["rfcedstyle"]
        self.pis["subcompact"] = self.pis["compact"]

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
                except lxml.etree.DTDParseError as e:
                    # The DTD itself has errors
                    xml2rfc.log.error('Could not parse the dtd file:',
                                      dtd_path + '\n  ', e.message)
                    return False, []
            else:
                # Invalid path given
                xml2rfc.log.error('DTD file does not exist:', dtd_path)
                return False, []
            
        # Otherwise, use document's DTD declaration
        else:
            dtd = self.tree.docinfo.externalDTD
            
        if not dtd:
            # No explicit DTD filename OR declaration in document!
            xml2rfc.log.warn('No DTD given, defaulting to', self.default_dtd_path)
            return self.validate(dtd_path=self.default_dtd_path)

        if dtd.validate(self.getroot()):
            # The document was valid
            return True, []
        else:
            if len(dtd.error_log) == 0:
                return True, []
            else:
                # The document was not valid
                return False, dtd.error_log
    
    def parse_pi(self, pi):
        """ Add a processing instruction to the current state 
            
            Will also return the dictionary containing the added instructions
            for use in things like ?include instructions
        """
        if pi.text:
            # Split text in the format 'key="val"'
            chunks = re.split(r'=[\'"]([^\'"]*)[\'"]', pi.text)
            # Create pairs from this flat list, discard last element if odd
            tmp_dict = dict(zip(chunks[::2], chunks[1::2]))
            for key, val in tmp_dict.items():
                # Update main PI state
                self.pis[key] = val
            # Return the new values added
            return tmp_dict
        return {}

    def _eval_pre_pi(self):
        """ Evaluate pre-document processing instructions
        
            This will look at all processing instructions before the root node
            for initial document settings.
        """
        # Grab processing instructions from xml tree
        element = self.tree.getroot().getprevious()
        while element is not None:
            if element.tag is lxml.etree.PI:
                self.parse_pi(element)
            element = element.getprevious()

    def _format_whitespace(self):
        xml2rfc.utils.formatXmlWhitespace(self.getroot())
