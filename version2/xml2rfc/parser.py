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


class CachingResolver(lxml.etree.Resolver):
    def __init__(self, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet

    def resolve(self, request_url, public_id, context):
        cache_dir = os.path.expanduser('~/.cache/xml2rfc')
        if not os.path.exists(cache_dir):
            if self.verbose:
                xml2rfc.log.write('Creating cache directory at', cache_dir)
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
                    xml2rfc.log.write('Creating cache for', request_url)
                urllib.urlretrieve(request_url, resource_path)
        else:
            # Not dtd or network entity, use the absolute path was given
            resource_path = url.path
        if self.verbose:
            xml2rfc.log.write('Loading resource... ', resource_path)
        return self.resolve_filename(resource_path, context)


class XmlRfcParser:
    """ XML parser with callbacks to construct an RFC tree """
    def __init__(self, filename, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet
        self.source = filename
        if not self.quiet:
            xml2rfc.log.write('Parsing file', self.source)

    def parse(self, prepare=True):
        """ Parses the source XML file and returns an XmlRfc instance """

        # Get a parser object
        parser = lxml.etree.XMLParser(dtd_validation=True, \
                                      no_network=False, \
                                      remove_comments=True, \
                                      remove_pis=False, \
                                      remove_blank_text=True)

        # Add our custom resolver
        parser.resolvers.add(CachingResolver(verbose=self.verbose, \
                                             quiet=self.quiet))

        # Parse the XML file into a tree and create an rfc instance
        # Bubble up any validation or syntax errors. They will need to be
        # handled in the CLI script or GUI.
        try:
            tree = lxml.etree.parse(self.source, parser)
        except lxml.etree.XMLSyntaxError, error:
            raise error

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

        # Grab processing instructions from xml tree
        element = tree.getroot().getprevious()
        self.pis = {}
        while element is not None:
            if element.tag is lxml.etree.PI:
                key, sep, val = str(element.text).partition('=')
                self.pis[key] = val.strip('"\' ')
            element = element.getprevious()

    def getroot(self):
        """ Wrapper method to get the root of the XML tree"""
        return self.tree.getroot()

    def getpis(self):
        """ Returns a list of the XML processing instructions """
        return self.pis

    def prepare(self):
        """ Prepare the RFC document for output.

            This method is automatically invoked after the xml file is
            finished being read, unless ``prepare=False`` was set.  It
            may do any of the following things:

            * Set any necessary default values.
            * Pre-format some elements to the proper text output.

            We can perform any operations here that will be common to all
            ouput formats.  Any further formatting is handled in the
            xml2rfc.writer modules.
        """
        root = self.getroot()

        # Traverse the tree and strip any newlines contained in element data,
        # Except for artwork, which needs to preserve whitespace.
        # If we strip a newline after a period, ensure that there are 
        # two spaces after the period.
        for element in root.iter():
            if element.tag != 'artwork':
                if element.text is not None:
                    element.text = re.sub('\s*\n\s*', ' ', \
                                   re.sub('\.\s*\n\s*', '.  ', \
                                   element.text.lstrip()))
                    
                if element.tail is not None:
                    element.tail = re.sub('\s*\n\s*', ' ', \
                                   re.sub('\.\s*\n\s*', '.  ', \
                                   element.tail))

        # Set some document-independent defaults
        workgroup = root.find('front/workgroup')
        if workgroup is None or not workgroup.text:
           root.attrib['workgroup'] = 'Network Working Group'
        else:
            root.attrib['workgroup'] = workgroup.text
        if 'updates' in root.attrib and root.attrib['updates']:
            root.attrib['updates'] = 'Updates: ' + root.attrib['updates']
        if 'obsoletes' in root.attrib and root.attrib['obsoletes']:
            root.attrib['obsoletes'] = 'Obsoletes: ' + root.attrib['obsoletes']
        if 'category' not in root.attrib:
            xml2rfc.log.warn('No category specified for document.')

        # Fix date
        today = datetime.date.today()
        date = root.find('front/date')
        year = date.attrib.get('year', '')
        month = date.attrib.get('month', '')
        day = date.attrib.get('day', '')
        if not year or (year == str(today.year) and not month) or \
                       (year == str(today.year) and month == str(today.month)):
            date.attrib['year'] = today.strftime('%Y')
            date.attrib['month'] = today.strftime('%B')
            date.attrib['day'] = today.strftime('%d')
        yearstring = date.attrib['year']
        root.attrib['copyright'] = 'Copyright (c) %s IETF Trust and the ' \
        'persons identified as the document authors.  All rights reserved.' % \
        yearstring

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
