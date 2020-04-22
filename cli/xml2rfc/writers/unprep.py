# Copyright The IETF Trust 2017, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import copy
import datetime
import inspect

from codecs import open

try:
    from xml2rfc import debug
    debug.debug = True
except ImportError:
    pass

from lxml import etree


from xml2rfc import log
from xml2rfc.utils import namespaces, sdict
from xml2rfc.writers.base import default_options, BaseV3Writer, RfcWriterError
from xml2rfc.writers.v2v3 import slugify


class UnPrepWriter(BaseV3Writer):
    """ Writes an XML file where many of the preptool additions have been removed"""

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today(), liberal=None, keep_pis=['v3xml2rfc']):
        super(UnPrepWriter, self).__init__(xmlrfc, quiet=quiet, options=options, date=date)
        if not quiet is None:
            options.quiet = quiet
        self.rfcnumber = self.root.get('number')
        self.liberal = liberal if liberal != None else options.accept_prepped
        self.keep_pis = keep_pis
        #
        self.v3_rng = etree.RelaxNG(file=self.rng_file)
        #
        self.ol_counts = {}
        self.attribute_defaults = {}
        # 
        self.boilerplate_section_number = 0
        self.toc_section_number = 0
        self.note_number = 0
        self.middle_section_number = [0, ]
        self.table_number = 0
        self.figure_number = 0
        self.unicode_number = 0
        self.references_number = [0, ]
        self.back_section_number = [0, ]
        self.paragraph_number = [0, ]
        self.iref_number = 0
        #
        self.prev_section_level = 0
        self.prev_references_level = 0
        self.prev_paragraph_section = None
        #
        self.prepped = self.root.get('prepTime')
        #
        self.index_entries = []
        #
        self.spacer = '\u00a0\u00a0'
        #
        self.boilerplate_https_date = datetime.date(year=2017, month=8, day=21)

    def get_attribute_names(self, tag):
        attr = self.schema.xpath("/x:grammar/x:define/x:element[@name='%s']//x:attribute" % tag, namespaces=namespaces)
        names = [ a.get('name') for a in attr ]
        return names
        
    def get_attribute_defaults(self, tag):
        if not tag in self.attribute_defaults:
            ignored_attributes = set(['keepWithNext', 'keepWithPrevious', 'toc', 'pageno', ])
            attr = self.schema.xpath("/x:grammar/x:define/x:element[@name='%s']//x:attribute" % tag, namespaces=namespaces)
            defaults = dict( (a.get('name'), a.get("{%s}defaultValue"%namespaces['a'], None)) for a in attr )
            keys = set(defaults.keys()) - ignored_attributes
            self.attribute_defaults[tag] = sdict(dict( (k, defaults[k]) for k in keys if defaults[k] ))
        return copy.copy(self.attribute_defaults[tag])

    def validate(self, when, warn=False):
        return super(UnPrepWriter, self).validate(when='%s running unprep'%when, warn=warn)

    def write(self, filename):
        """ Public method to write the XML document to a file """

        if not self.options.quiet:
            self.log(' Unprepping %s' % self.xmlrfc.source)
        self.unprep()
        if self.errors:
            raise RfcWriterError("Not creating output file due to errors (see above)")

        # Use lxml's built-in serialization
        file = open(filename, 'w', encoding='utf-8')

        text = etree.tostring(self.root.getroottree(), 
                                        xml_declaration=True, 
                                        encoding='utf-8',
                                        pretty_print=True)
        file.write(text.decode('utf-8'))

        if not self.options.quiet:
            self.log(' Created file %s' % filename)

    def unprep(self):

        ## Selector notation: Some selectors below have a handler annotation,
        ## with the selector and the annotation separated by a semicolon (;).
        ## Everything from the semicolon to the end of the string is stripped
        ## before the selector is used.

        selectors = [
            '.;validate_before()',
            '/rfc[@prepTime]',
            './/ol[@group]',
            './front/boilerplate',
            './front/toc',
            './/name[@slugifiedName]',
            './/*;remove_attribute_defaults()',
            './/*[@pn]',
            './/xref',
            './back/section/t[@anchor="rfc.index.index"]',
            './back/section[@anchor="authors-addresses"]',
            './/section[@toc]',
            './/*[@removeInRFC="true"]',
#            '.;validate_after()',
            '.;pretty_print_prep()',
        ]
        # Setup
        selector_visits = dict( (s, 0) for s in selectors)

        ## From RFC7998:
        ##
        # 5.1.1.  XInclude Processing
        # 
        #    Process all <x:include> elements.  Note: XML <x:include> elements may
        #    include more <x:include> elements (with relative references resolved
        #    against the base URI potentially modified by a previously inserted
        #    xml:base attribute).  The tool may be configurable with a limit on
        #    the depth of recursion.
        try:
            self.tree.xinclude()
        except etree.XIncludeError as e:
            self.die(None, "XInclude processing failed: %s" % e)

        # Set up reference mapping for later use.  Done here, and not earlier,
        # to capture any references pulled in by the XInclude we just did.
        self.refname_mapping = self.get_refname_mapping()

        # Check for duplicate <displayreference> 'to' values:
        seen = {}
        for e in self.root.xpath('.//displayreference'):
            to = e.get('to')
            if to in set(seen.keys()):
                self.die(e, 'Found duplicate displayreference value: "%s" has already been used in %s' % (to, etree.tostring(seen[to]).strip()))
            else:
                seen[to] = e
        del seen

        ## Do remaining processing by xpath selectors (listed above)
        funcs = set([])
        for s in selectors:
            slug = slugify(s.replace('self::', '').replace(' or ','_').replace(';','_'))
            if '@' in s:
                func_name = 'attribute_%s' % slug
            elif "()" in s:
                func_name = slug
            else:
                if not slug:
                    slug = 'rfc'
                func_name = 'element_%s' % slug
            # get rid of selector annotation
            ss = s.split(';')[0]
            func = getattr(self, func_name, None)
            if func:
                for e in self.tree.xpath(ss):
                    func(e, e.getparent())
                    selector_visits[s] += 1
                funcs.add(func_name)
            else:
                self.warn(None, "No handler %s() found" % (func_name, ))
                selector_visits[s] = None

        if self.options.debug:
            for s in selectors:
                if selector_visits[s] == 0:
                    self.note(None, "Selector '%s' has not matched" % (s))

            methods = inspect.getmembers(self, predicate=inspect.ismethod)
            ignored = set([ '__init__', 'get_attribute_names', 'get_attribute_defaults', 'validate', 'write',
                            'unprep', 'remove_element', ])
            ignored |= set( n for (n, m) in inspect.getmembers(BaseV3Writer, predicate=inspect.ismethod) )
            methods = [ (n, m) for (n, m) in methods if not n in ignored ]
            for (n, m) in methods:
                if not n in funcs:
                    self.warn(None, "Method '%s()' has not been used" % n)

        log.note(" Completed unprep run")

        if self.errors:
            raise RfcWriterError("Not creating output file due to errors (see above)")

        return self.tree

    def validate_before(self, e, p):
        version = self.root.get('version', '3')
        if version not in ['3', ]:
            self.die(self.root, 'Expected <rfc> version="3", but found "%s"' % version)
        if not self.validate('before'):
            self.note(None, "Schema validation failed for input document")

    def attribute_rfc_preptime(self, e, p):
        del e.attrib['prepTime']

    def attribute_ol_group(self, e, p):
        group = e.get('group')
        start = e.get('start')
        if not group in self.ol_counts:
            self.ol_counts[group] = 1
        if start and int(start) == int(self.ol_counts[group]):
            del e.attrib['start']
        self.ol_counts[group] += len(list(e.iterchildren('li')))

    def attribute_removeinrfc_true(self, e, p):
        warning_text = "This %s is to be removed before publishing as an RFC." % e.tag
        top_para = e.find('t')
        if top_para!=None and top_para.text != warning_text:
            e.remove(top_para)

    def remove_element(self, e, p):
        self.remove(p, e)

    element_front_boilerplate = remove_element
    element_front_toc = remove_element
    attribute_back_section_anchor_authors_addresses = remove_element
    attribute_back_section_t_anchor_rfcindexindex = remove_element

    def attribute_name_slugifiedname(self, e, p):
        del e.attrib['slugifiedName']

    def remove_attribute_defaults(self, e, p):
        g = p.getparent() if p != None else None
        ptag = p.tag if p != None else None
        gtag = g.tag if g != None else None
        if not (gtag in ['reference', ] or ptag in ['reference', ]):
            defaults = self.get_attribute_defaults(e.tag)
            for k in defaults:
                if k in e.attrib:
                    if (e.tag, k) in [('rfc', 'consensus')]:
                        continue
                    #debug.say('L%-5s: Setting <%s %s="%s">' % (e.sourceline, e.tag, k, defaults[k]))
                    if ':' in k:
                        ns, tag = k.split(':',1)
                        q = etree.QName(namespaces[ns], tag)
                        if e.get(q) == defaults[k]:
                            del e.attrib[q]
                    else:
                        if e.get(k) == defaults[k]:
                            del e.attrib[k]

    def attribute_pn(self, e, p):
        del e.attrib['pn']

    def attribute_section_toc(self, e, p):
        del e.attrib['toc']

    def element_xref(self, e, p):
        if e.get('derivedContent'):
            del e.attrib['derivedContent']
        if e.get('derivedLink'):
            del e.attrib['derivedLink']

    def validate_after(self, e, p):
        # XXX: There is an issue with exponential increase in validation time
        # as a function of the number of attributes on the root element, on
        # the order of minutes for the full set of possble attribute values.
        # See https://bugzilla.gnome.org/show_bug.cgi?id=133736 .  In our
        # schema, there is no dependency in the underlying schema on the root
        # element attributes.  In order to avoid very long validation times, we
        # strip the root attributes before validation, and put them back
        # afterwards.  
        for k in e.keys():
            if not e.get(k):
                del e.attrib[k]
        attrib = copy.deepcopy(e.attrib) 
        for k in attrib.keys():
            del e.attrib[k]
        #
        if not self.validate('after', warn=True):
            self.note(None, "Schema validation failed for input document")
        else:
            self.root.set('version', '3')
        #
        keys = list(attrib.keys())
        keys.sort()
        for k in keys:
            e.set(k, attrib[k])
