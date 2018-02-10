# Copyright The IETF Trust 2017, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import copy
import datetime
import lxml.etree
import os
import re
import six
import sys
import unicodedata

from codecs import open

try:
    import debug
    debug.debug = True
except ImportError:
    pass

if six.PY2:
    from urlparse import urlsplit, urlunsplit
    from urllib import urlopen
elif six.PY3:
    from urllib.parse import urlsplit, urlunsplit
    from urllib.request import urlopen

from collections import OrderedDict
from lxml import etree


from xml2rfc import log
from xml2rfc.boilerplate_rfc_7841 import boilerplate_status_of_memo
from xml2rfc.boilerplate_tlp import boilerplate_tlp
from xml2rfc.utils import build_dataurl
from xml2rfc.writers.base import default_options
from xml2rfc.writers.v2v3 import slugify
from xml2rfc.scripts import get_scripts

ns={
    'x':'http://relaxng.org/ns/structure/1.0',
    'a':'http://relaxng.org/ns/compatibility/annotations/1.0',
}

refname_mapping = {}

def normalize_month(month):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for i, m in enumerate(months):
        if m.lower().startswith(month.lower()):
            month = '%02d' % (i+1)
    assert month.isdigit()
    return month

# This is used to enforce global uniqueness on slugs:
seen_slugs = set([])

def slugify_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub('[^\w\s/-]', '', name).strip().lower()
    slug = re.sub('[-\s/]+', '-', slug)
    # limit slug length
    n = 32
    m = 2
    while slug[:n] in seen_slugs and n < len(slug) and n<40:
        n += 1
    while slug[:n]+'-%s'%m in seen_slugs and m < 99:
        m += 1
    if m == 99 and slug[:n]+'-%s'%m in seen_slugs:
        raise RuntimeError("Too many overlapping <name> content instances; cannot create a sensible slugifiedName attribute")
    if slug[:n] in seen_slugs:
        slug = slug[:n]+'-%s'%m
    else:
        slug = slug[:n]
    seen_slugs.add(slug)
    return slug

class PrepToolWriter:
    """ Writes an XML file where the input has been modified according to RFC 7998"""

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today(), liberal=None):
        if not quiet is None:
            options.quiet = quiet
        self.xmlrfc = xmlrfc
        self.root = xmlrfc.getroot()
        self.tree = self.root.getroottree()
        self.options = options
        self.when = 'before'                    # used for validation output messages
        self.errors = []
        self.ol_counts = {}
        self.v3_rng_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'v3.rng')
        self.schema = etree.ElementTree(file=self.v3_rng_file)
        self.attribute_defaults = {}
        # 
        self.boilerplate_section_number = 0
        self.note_number = 0
        self.middle_section_number = [0, ]
        self.table_number = 0
        self.figure_number = 0
        self.references_number = [0, ]
        self.back_section_number = [0, ]
        self.paragraph_number = [0, ]
        self.iref_number = 0
        #
        self.prev_section_level = 0
        self.prev_paragraph_section = None
        #
        self.liberal = liberal if liberal != None else options.liberal

    def get_attribute_defaults(self, tag):
        if not tag in self.attribute_defaults:
            attr = self.schema.xpath("/x:grammar/x:define/x:element[@name='%s']//x:attribute" % tag, namespaces=ns)
            defaults = dict( (a.get('name'), a.get("{%s}defaultValue"%ns['a'], None)) for a in attr )
            keys = list(defaults.keys())
            keys.sort()
            self.attribute_defaults[tag] = OrderedDict( (k, defaults[k]) for k in keys if defaults[k] )
        return self.attribute_defaults[tag]

    def element(self, tag, **kwargs):
        attrib = self.get_attribute_defaults(tag)
        attrib.update(kwargs)
        return etree.Element(tag, **attrib)

    def note(self, e, text):
        lnum = getattr(e, 'sourceline', 0)
        msg = "%s(%s): Note: %s" % (self.xmlrfc.source, lnum+1, text)
        log.write(msg)

    def warn(self, e, text):
        lnum = getattr(e, 'sourceline', 0)
        msg = "%s(%s): Warning: %s" % (self.xmlrfc.source, lnum+1, text)
        log.write(msg)

    def err(self, e, text, trace=False):
        lnum = getattr(e, 'sourceline', 0)
        msg = "%s(%s): Error: %s" % (self.xmlrfc.source, lnum+1, text)
        if trace or self.options.debug:
            raise RuntimeError(msg)
        else:
            log.write(msg)
        self.errors.append(msg)

    def die(self, e, text, trace=False):
        self.err(e, text, trace)
        log.write("Cannot continue, quitting now")
        sys.exit(1)

    def validate(self, when):

        
        v3_rng = lxml.etree.RelaxNG(file=self.v3_rng_file)

        # Our schema doesn't permit xi:include elements, so we must expand
        # before validation
        try:
            v3_rng.assertValid(self.tree)
            log.note("The document validates according to the RFC7991 schema %s running preptool" % (when, ))
            return True
        except Exception as e:
            # These warnings are occasionally incorrect -- disable this
            # output for now:
            self.warn(e, 'Invalid document %s running preptool: %s' % (when, e,))
            return False

    def write(self, filename):
        """ Public method to write the XML document to a file """

        self.prep()
        if self.errors:
            log.write("Not creating output file due to errors (see above)")
            return

        # Use lxml's built-in serialization
        file = open(filename, 'w', encoding='utf-8')

        text = lxml.etree.tostring(self.root.getroottree(), 
                                        xml_declaration=True, 
                                        encoding='utf-8',
                                        pretty_print=True)
        file.write(text.decode('utf-8'))

        if not self.options.quiet:
            log.write('Created file', filename)

    def prep(self):
        global refname_mapping

        ## Selector notation: Some selectors below have a handler annotation,
        ## with the selector and the annotation separated by a semicolon (;).
        ## Everything from the semicolon to the end of the string is stripped
        ## before the selector is used.
        selectors = [
                                                # 5.1.1.  XInclude Processing
                                                # 5.1.2.  DTD Removal
            '//processing-instruction()',       # 5.1.3.  Processing Instruction Removal
            '.;validate_before()',              # 5.1.4.  Validity Check
            './/*[@anchor]',                    # 5.1.5.  Check "anchor"
            '.;insert_version()',               # 5.2.1.  "version" Insertion
            './front;insert_series_info()',     # 5.2.2.  "seriesInfo" Insertion
            # mon
            './front;insert_date())',           # 5.2.3.  <date> Insertion
            '.;insert_preptime()',              # 5.2.4.  "prepTime" Insertion
            './/ol[@group]',                    # 5.2.5.  <ol> Group "start" Insertion
            '//*;insert_attribute_defaults()',  # 5.2.6.  Attribute Default Value Insertion
            './/section',                       # 5.2.7.  Section "toc" attribute
            './/note[@removeInRFC="true"]',     # 5.2.8.  "removeInRFC" Warning Paragraph
            './/section[@removeInRFC="true"]',     
            '//*[@*="yes" or @*="no"]',         #         convert old attribute false/true
            './front/date',                     # 5.3.1.  "month" Attribute
            './/*[@ascii]',                     # 5.3.2.  ASCII Attribute Processing
            './front/author',
            # tue
            './/*[@title]',                     # 5.3.3.  "title" Conversion
            '.;fill_in_expires_date()',         # 5.4.1.  "expiresDate" Insertion
            './front;insert_boilerplate()',     # 5.4.2.  <boilerplate> Insertion
            '.;check_series_and_submission_type()', # 5.4.2.1.  Compare <rfc> "submissionType" and <seriesInfo> "stream"
            # wed (+ investigating verification runtime)
            './/boilerplate;insert_status_of_memo()',  # 5.4.2.2.  "Status of this Memo" Insertion
            # thu
            './/boilerplate;insert_copyright_notice()', # 5.4.2.3.  "Copyright Notice" Insertion
            './/boilerplate//section',          # 5.2.7.  Section "toc" attribute
            # sun
            './/reference;insert_target()',     # 5.4.3.  <reference> "target" Insertion
            './/name;insert_slugified_name()',  # 5.4.4.  <name> Slugification
            './/references;sort()',             # 5.4.5.  <reference> Sorting
                                                # 5.4.6.  "pn" Numbering
            './/boilerplate//section;add_number()',
            './front//abstract;add_number()',
            './/front//note;add_number()',
            './/middle//section;add_number()',
            './/table;add_number()',
            './/figure;add_number()',
            './/references;add_number()',
            './/back//section;add_number()',
            '.;paragraph_add_number()',
            './/iref;add_number()',             # 5.4.7.  <iref> Numbering
            # mon
            './/xref',                          # 5.4.8.  <xref> Processing
            './/relref',                        # 5.4.9.  <relref> Processing
            './/artwork',                       # 5.5.1.  <artwork> Processing
            # tue
            './/sourcecode',                    # 5.5.2.  <sourcecode> Processing
            './/*[@removeInRFC="true"]',        # 5.6.1.  <note> Removal
            './/cref;removal()',                # 5.6.2.  <cref> Removal
                                                # 5.6.3.  <link> Processing
            './/link[@rel="alternate"];removal()',
            '.;check_links_required()',
            './/comment();removal()',           # 5.6.4.  XML Comment Removal
            '.;attribute_removal()',            # 5.6.5.  "xml:base" and "originalSrc" Removal
            '.;validate_after()',               # 5.6.6.  Compliance Check
            '.;insert_scripts()',               # 5.7.1.  "scripts" Insertion
            '.;pretty_print_prep()',            # 5.7.2.  Pretty-Format
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

        self.tree.xinclude()

        # Set up reference mapping for later use.
        refname_mapping = dict( (e.get('anchor'), e.get('anchor')) for e in self.root.xpath('.//reference') )
        refname_mapping.update(dict( (e.get('target'), e.get('to')) for e in self.root.xpath('.//displayreference') ))

        # 
        # 5.1.2.  DTD Removal
        # 
        #    Fully process any Document Type Definitions (DTDs) in the input
        #    document, then remove the DTD.  At a minimum, this entails processing
        #    the entity references and includes for external files.

        ## Entities has been resolved as part of the initial parsing.  Remove
        ## docinfo and PIs outside the <rfc/> element by copying the root
        ## element and creating a new tree.
        root = copy.deepcopy(self.root)
        self.tree = root.getroottree()
        self.root = root

        ## Do remaining processing by xpath selectors (listed above)
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
                if self.options.debug:
                    log.note("Calling %s()" % func_name)
                for e in self.tree.xpath(ss):
                    func(e, e.getparent())
                    selector_visits[s] += 1
            else:
                log.warn("No handler %s() found" % (func_name, ))


        if self.options.debug:
            for s in selectors:
                if selector_visits[s] == 0:
                    log.note("Selector '%s' has not matched" % (s))

    # ----------------------------------------------------------------

    # 5.1.3.  Processing Instruction Removal
    # 
    #    Remove processing instructions.

    def processing_instruction(self, e, p):
        if p != None:
            p.remove(e)

    # 5.1.4.  Validity Check
    # 
    #    Check the input against the RELAX NG (RNG) in [RFC7991].  If the
    #    input is not valid, give an error.

    def validate_before(self, e, p):
        if not self.validate('before'):
            log.note("Schema validation failed for input document")

    # 5.1.5.  Check "anchor"
    # 
    #    Check all elements for "anchor" attributes.  If any "anchor"
    #    attribute begins with "s-", "f-", "t-", or "i-", give an error.
    #
    ## modified to use "section-", "figure-", "table-", "index-"

    def attribute_anchor(self, e, p):
        reserved = ["section-", "figure-", "table-", "index-", ]
        k = 'anchor'
        if k in e.keys():
            v = e.get(k)
            for prefix in reserved:
                if v.startswith(prefix):
                    self.err(e, "Reserved anchor name: %s.  Don't use anchor names beginning with one of %s" % (v, ', '.join(reserved)))

    # 
    # 5.2.  Defaults
    # 
    #    These steps will ensure that all default values have been filled in
    #    to the XML, in case the defaults change at a later date.  Steps in
    #    this section will not overwrite existing values in the input file.
    # 
    # 5.2.1.  "version" Insertion
    # 
    #    If the <rfc> element has a "version" attribute with a value other
    #    than "3", give an error.  If the <rfc> element has no "version"
    #    attribute, add one with the value "3".

    def insert_version(self, e, p):
        version = e.get('version', None)
        if version and version != '3':
            self.err(e, "Expected <rfc version='3'>, found version='%s'" % (version,))
        e.set('version', '3')

    # 5.2.2.  "seriesInfo" Insertion
    # 
    #    If the <front> element of the <rfc> element does not already have a
    #    <seriesInfo> element, add a <seriesInfo> element with the name
    #    attribute based on the mode in which the prep tool is running
    #    ("Internet-Draft" for Draft mode and "RFC" for RFC production mode)
    #    and a value that is the input filename minus any extension for
    #    Internet-Drafts, and is a number specified by the RFC Editor for
    #    RFCs.
    def front_insert_series_info(self, e, p):
        series = e.xpath('seriesInfo')
        if not series:
            title = e.find('title')
            if title != None:
                pos = e.index(title)+1
            else:
                pos = 0
            path, base = os.path.split(self.options.output_filename)
            name, ext  = base.split('.', 1)
            if self.options.rfc:
                if not name.starswith('rfc'):
                    self.die(e, "Expected a filename starting with 'rfc' in --rfc mode, but found '%s'" % (name, ))
                num = name[3:]
                if not num.isdigit():
                    self.die(e, "Expected to find the RFC number in the file name in --rfc mode, but found '%s'" % (num, ))
                e.insert(pos, etree.Element('seriesInfo', name='RFC', value=self.rfcnumber))
            else:
                e.insert(pos, etree.Element('seriesInfo', name='Internet-Draft', value=name))
        else:
            if self.options.rfc:
                rfcinfo = e.find('./seriesInfo[@name="RFC"]')
                if rfcinfo is None:
                    self.die(e, "Expected a <seriesInfo> element giving the RFC number in --rfc mode, but found none")
                self.rfcnumber = rfcinfo.get('value')
                if not self.rfcnumber.isdigit():
                    self.die(rfcinfo, "Expected a numeric RFC number, but found '%s'" % (self.rfcnumber, ))
                    

    # 5.2.3.  <date> Insertion
    # 
    #    If the <front> element in the <rfc> element does not contain a <date>
    #    element, add it and fill in the "day", "month", and "year" attributes
    #    from the current date.  If the <front> element in the <rfc> element
    #    has a <date> element with "day", "month", and "year" attributes, but
    #    the date indicated is more than three days in the past or is in the
    #    future, give a warning.  If the <front> element in the <rfc> element
    #    has a <date> element with some but not all of the "day", "month", and
    #    "year" attributes, give an error.

    def front_insert_date(self, e, p):
        d = e.find('date')
        today = datetime.date.today()
        
        if d != None:
            year  = d.get('year')
            month = d.get('month')
            day   = d.get('day')
            if self.options.rfc and not (year and month and day):
                # XXX: This changes RFC Editor policy on publication dates, and is
                # probably not what was intended
                self.warn(e, "Expected explicit values for year, month, and day, but found %s, %s and %s" % (year, month, day))
                day = "1"
            if month and not month.isdigit():
                if len(month) < 3:
                    self.err("Expected a month name with at least 3 letters, found '%s'" % (month, ))
                month = normalize_month(month)
            if not year:
                year = str(today.year)
            if not month:
                if not year == str(today.year):
                    self.die(e, "Expected <date> to have the current year, when month is missing, but found '%s'" % (d.get('year')))
                month = today.strftime('%m')

            if not day:
                if not (year == str(today.year) and month == today.strftime('%m')):
                    self.warn(e, "Expected <date> to have the current month when day is missing, but found '%s'" % (d.get('month')))
                    day = '01'
                else:
                    day = today.strftime('%d')
            datestr = "%s-%s-%s" %(year, month, day)
            date = datetime.datetime.strptime(datestr, "%Y-%m-%d").date()
            if abs(date - datetime.date.today()) > datetime.timedelta(days=3):
                self.warn(e, "The document date (%s) is more than 3 days away from today's date" % date)
            n = self.element('date', year=year, month=month, day=day)
            e.replace(d, n)
        else:
            preceding = e.xpath('title|seriesInfo|author')
            pos = max(e.index(i) for i in preceding)+1
            date = self.options.date or datetime.date.today()
            year  = str(date.year)
            month = date.strftime('%m')
            day   = date.strftime('%d')
            e.insert(pos, self.element('date', year=year, month=month, day=day))
        self.date = datetime.date(year=int(year), month=int(month), day=int(day))

    # 5.2.4.  "prepTime" Insertion
    # 
    #    If the input document includes a "prepTime" attribute of <rfc>, exit
    #    with an error.
    # 
    #    Fill in the "prepTime" attribute of <rfc> with the current datetime.
    def insert_preptime(self, e, p):
        if 'prepTime' in e.attrib:
            if self.liberal:
                self.note(e, "Scanning alredy prepped source dated %s" % (e.get('prepTime'), ))
            else:
                self.die(e, "Did not expect a prepTime= attribute for <rfc>, but found '%s'" % (e.get('prepTime')))
        else:
            e.set('prepTime', datetime.date.today().strftime('%Y-%m-%d'))

    # 5.2.5.  <ol> Group "start" Insertion
    # 
    #    Add a "start" attribute to every <ol> element containing a group that
    #    does not already have a start.

    def attribute_ol_group(self, e, p):
        group = e.get('group')
        start = e.get('start')
        if not start:
            if group in self.ol_counts:
                self.ol_counts[group] += 1
            else:
                self.ol_counts[group] = 1
            e.set('start', str(self.ol_counts[group]))

    # 5.2.6.  Attribute Default Value Insertion
    # 
    #    Fill in any default values for attributes on elements, except
    #    "keepWithNext" and "keepWithPrevious" of <t>, and "toc" of <section>.
    #    Some default values can be found in the RELAX NG schema, while others
    #    can be found in the prose describing the elements in [RFC7991].
    def insert_attribute_defaults(self, e, p):
        g = p.getparent() if p != None else None
        ptag = p.tag if p != None else None
        gtag = g.tag if g != None else None
        if not (gtag in ['reference', ] or ptag in ['reference', ]):
            defaults = self.get_attribute_defaults(e.tag)
            for k in ['keepWithNext', 'keepWithPrevious', 'toc']:
                if k in defaults:
                    del defaults[k]
            for k in defaults:
                if not k in e.attrib:
                    #debug.say('Setting <%s %s="%s">' % (e.tag, k, defaults[k]))
                    e.set(k, defaults[k])

    # 5.2.7.  Section "toc" attribute
    # 
    #    For each <section>, modify the "toc" attribute to be either "include"
    #    or "exclude":
    # 
    #    o  for sections that have an ancestor of <boilerplate>, use "exclude"
    # 
    #    o  else for sections that have a descendant that has toc="include",
    #       use "include".  If the ancestor section has toc="exclude" in the
    #       input, this is an error.
    # 
    #    o  else for sections that are children of a section with
    #       toc="exclude", use "exclude".
    # 
    #    o  else for sections that are deeper than rfc/@tocDepth, use
    #       "exclude"
    # 
    #    o  else use "include"
    def element_section(self, e, p):
        # we will process .//boilerplate//section elements correctly later,
        # so ignore that condition for now.
        etoc = e.get('toc')
        ptoc = p.get('toc')
        included_descendants = e.xpath('.//section[@toc="include"]')
        edepth = len([ a for a in e.iterancestors() if a.tag == 'section'])+1

        if   etoc == 'include':
            pass
        elif etoc in [ None, 'default' ]:
            if included_descendants:
                e.set('toc', 'include')
            elif ptoc == 'exclude':
                e.set('toc', 'exclude')
            else:
                tocDepth = self.root.get('tocDepth', '3')
                if tocDepth.isdigit():
                    if edepth <= int(tocDepth):
                        e.set('toc', 'include')
                    else:
                        e.set('toc', 'exclude')
                else:
                    self.err(self.root, "Expected tocDepth to be an integer, but found '%s'" % (tocDepth))
        elif etoc == 'exclude':
            if included_descendants:
                self.err(e, 'Expected <section> to have toc="include", to match child section attribute, but found toc="exclude"')
        else:
            self.err(e, "Expected the toc attribute to be one of 'include', 'exclude', or 'default', but found '%s'" % etoc)
            

    # 5.2.8.  "removeInRFC" Warning Paragraph
    # 
    #    In I-D mode, if there is a <note> or <section> element with a
    #    "removeInRFC" attribute that has the value "true", add a paragraph to
    #    the top of the element with the text "This note is to be removed
    #    before publishing as an RFC." or "This section...", unless a
    #    paragraph consisting of that exact text already exists.
    def attribute_note_removeinrfc_true(self, e, p):
        if not self.options.rfc:
            warning_text = "This %s is to be removed before publishing as an RFC." % e.tag
            top_para = e.find('t')
            if top_para.text != warning_text:
                name = e.xpath('name')
                pos = 1 if name != None else 0
                t = self.element('t')
                t.text = warning_text
                e.insert(pos, t)

    def attribute_section_removeinrfc_true(self, e, p):
        self.attribute_note_removeinrfc_true(e, p)
    


    # 5.3.  Normalization
    # 
    #    These steps will ensure that ideas that can be expressed in multiple
    #    different ways in the input document are only found in one way in the
    #    prepared document.

    # The following is not specified or required, but will make life easier
    # later:
    def attribute_yes_no(self, e, p):
        for k,v in e.attrib.items():
            if   v == 'yes':
                e.set(k, 'true')
            elif v == 'no':
                e.set(k, 'false')

    # 5.3.1.  "month" Attribute
    # 
    #    Normalize the values of "month" attributes in all <date> elements in
    #    <front> elements in <rfc> elements to numeric values.
    def element_front_date(self, e, p):
        month = e.get('month')
        if not month.isdigit():
            e.set('month', normalize_month(month))

    # 5.3.2.  ASCII Attribute Processing
    # 
    #    In every <email>, <organization>, <street>, <city>, <region>,
    #    <country>, and <code> element, if there is an "ascii" attribute and
    #    the value of that attribute is the same as the content of the
    #    element, remove the "ascii" element and issue a warning about the
    #    removal.
    def attribute_ascii(self, e, p):
        if e.text.strip() == e.get('ascii').strip():
            del e.attrib['ascii']
            self.warn(e, "Removed a redundant ascii= attribute from <%s>" % (e.tag))

    #    In every <author> element, if there is an "asciiFullname",
    #    "asciiInitials", or "asciiSurname" attribute, check the content of
    #    that element against its matching "fullname", "initials", or
    #    "surname" element (respectively).  If the two are the same, remove
    #    the "ascii*" element and issue a warning about the removal.
    def element_front_author(self, e, p):
        for a in ['fullname', 'initials', 'surname']:
            aa = 'ascii'+a.capitalize()
            keys = e.keys()
            if   aa in keys and not a in keys:
                self.err(e, "Expected a %s= attribute to match the %s= attribute, but found none" % (a, aa))
            elif a in keys and aa in keys:
                if e.get(a).strip() == e.get(aa).strip():
                    del e.attrib[aa]
                    self.warn(e, "Removed a redundant %s= attribute from <%s>" % (aa, e.tag))

    # 5.3.3.  "title" Conversion
    # 
    #    For every <section>, <note>, <figure>, <references>, and <texttable>
    #    element that has a (deprecated) "title" attribute, remove the "title"
    #    attribute and insert a <name> element with the title from the
    #    attribute.
    def attribute_title(self, e, p):
        title = e.get('title')
        del e.attrib['title']
        name = self.element('name')
        name.text = title
        e.insert(0, name)

    # 5.4.  Generation
    # 
    #    These steps will generate new content, overriding existing similar
    #    content in the input document.  Some of these steps are important
    #    enough that they specify a warning to be generated when the content
    #    being overwritten does not match the new content.
    # 
    # 5.4.1.  "expiresDate" Insertion
    # 
    #    If in I-D mode, fill in "expiresDate" attribute of <rfc> based on the
    #    <date> element of the document's <front> element.
    def fill_in_expires_date(self, e, p):
        return
        if not self.options.rfc:
            d = e.find('./front/date')
            date = datetime.date(year=int(d.get('year')), month=int(d.get('month')), day=int(d.get('day')))
            old_exp = e.get('expiresDate')
            new_exp = (date + datetime.timedelta(days=185)).strftime('%Y-%m-%d')
            if old_exp != new_exp:
                e.set('expiresDate', new_exp)
                if old_exp:
                    self.warn(e, "Changed the rfc expiresDate attribute to correspond with the <front><date> element: '%s'" % (new_exp, ))

    # 
    # 5.4.2.  <boilerplate> Insertion
    # 
    #    Create a <boilerplate> element if it does not exist.  If there are
    #    any children of the <boilerplate> element, produce a warning that
    #    says "Existing boilerplate being removed.  Other tools, specifically
    #    the draft submission tool, will treat this condition as an error" and
    #    remove the existing children.
    # 
    def front_insert_boilerplate(self, e, p):
        if self.options.rfc:
            old_bp = e.find('boilerplate')
            new_bp = self.element('boilerplate')
            if old_bp != None:
                if not self.liberal:
                    children = old_bp.getchildren()
                    if len(children):
                        self.warn(old_bp, "Expected no <boilerplate> element, but found one.  Replacing the content with new boilerplate")
                    new_bp = self.element('boilerplate')
                    e.replace(old_bp, new_bp)
            else:
                e.append(new_bp)

    # 5.4.2.1.  Compare <rfc> "submissionType" and <seriesInfo> "stream"
    # 
    #    Verify that <rfc> "submissionType" and <seriesInfo> "stream" are the
    #    same if they are both present.  If either is missing, add it.  Note
    #    that both have a default value of "IETF".
    def check_series_and_submission_type(self, e, p):
        submission_type = e.get('submissionType')
        series_info_list = e.xpath('./front/seriesInfo')
        streams = [ i.get('stream') for i in series_info_list if i.get('stream') ] + [ submission_type ]
        if len(set(streams)) > 1:
            if submission_type:
                self.err(series_info_list[0], "The stream setting of <seriesInfo> is inconsistent with the submissionType of <rfc>.  Found %s" % (', '.join(streams)))
            else:
                self.err(series_info_list[0], "The stream settings of the <seriesInfo> elements are inconsistent.  Found %s" % (', '.join(streams)))
        else:
            stream = list(streams)[0]
            e.set('submissionType', stream)
            for i in series_info_list:
                i.set('stream', stream)

    # 5.4.2.2.  "Status of this Memo" Insertion
    # 
    #    Add the "Status of this Memo" section to the <boilerplate> element
    #    with current values.  The application will use the "submissionType",
    #    and "consensus" attributes of the <rfc> element, the <workgroup>
    #    element, and the "status" and "stream" attributes of the <seriesInfo>
    #    element, to determine which boilerplate from [RFC7841] to include, as
    #    described in Appendix A of [RFC7991].
    def boilerplate_insert_status_of_memo(self, e, p):
        # submissionType: "IETF" | "IAB" | "IRTF" | "independent"
        # consensus: "false" | "true"
        # category: "std" | "bcp" | "exp" | "info" | "historic"
        if self.options.rfc:
            if self.liberal and e.xpath('./section/name[text()="Status of this Memo"]'):
                self.note(e, "Boilerplate 'Status of this Memo' section exists, leaving it in place")
            else:
                stream = self.root.get('submissionType')
                category = self.root.get('category')
                consensus = self.root.get('consensus')
                workgroup = self.root.find('./front/workgroup')
                #
                group = workgroup.text if workgroup != None else None
                format_dict = { 'rfc_number': self.rfcnumber }
                if group:
                    format_dict['group_name'] = group
                #
                if stream == 'IRTF' and workgroup == None:
                    consensus = 'n/a'
                elif stream == 'independent':
                    consensus = 'n/a'
                #
                section = self.element('section', numbered='false')
                name = self.element('name')
                name.text = "Status of this Memo"
                section.append(name)
                try:
                    for para in boilerplate_status_of_memo[stream][category][consensus]:
                        t = self.element('t')
                        t.text = para.format(**format_dict)
                        section.append(t)
                except KeyError as exception:
                    if str(exception) in ["'rfc_number'", "'group_name'"]:
                        # Error in string expansion
                        self.die(p, 'Expected to have a value for %s when expanding the "Status of this Memo" boilerplate, but found none.' % str(exception))
                    else:
                        # Error in boilerplate dictionary indexes
                        self.die(self.root, 'Unexpected attribute combination(%s): <rfc submissionType="%s" category="%s" consensus="%s">' % (exception, stream, category, consensus))
                e.append(section)

    # 5.4.2.3.  "Copyright Notice" Insertion
    # 
    #    Add the "Copyright Notice" section to the <boilerplate> element.  The
    #    application will use the "ipr" and "submissionType" attributes of the
    #    <rfc> element and the <date> element to determine which portions and
    #    which version of the Trust Legal Provisions (TLP) to use, as
    #    described in A.1 of [RFC7991].
    def boilerplate_insert_copyright_notice(self, e, p):
        if self.options.rfc:
            if self.liberal and e.xpath('./section/name[text()="Copyright Notice"]'):
                self.note(e, "Boilerplate 'Copyright Notice' section exists, leaving it in place")
            else:
                tlp_2_start_date = datetime.date(year=2009, month=2, day=15)
                tlp_3_start_date = datetime.date(year=2009, month=9, day=12)
                tlp_4_start_date = datetime.date(year=2009, month=12, day=28)
                ipr = self.root.get('ipr').lower()
                subtype = self.root.get('submissionType')
                if not ipr:
                    self.die(self.root, "Missing ipr attribute on <rfc> element.")
                if not ipr.endswith('trust200902'):
                    self.die(self.root, "Unknown ipr attribute: %s" % (self.root.get('ipr'), ))
                #
                if   self.date < tlp_2_start_date:
                    self.die(e, "Cannot insert copyright statements earlier than TLP2.0, effective %s" % (tlp_2_start_date))
                elif self.date < tlp_3_start_date:
                    tlp = "2.0"
                    stream = "n/a"
                elif self.date < tlp_4_start_date:
                    tlp = "3.0"
                    stream = "n/a"
                else:
                    tlp = "4.0"
                    stream = 'IETF' if subtype == 'IETF' else 'alt'
                section = self.element('section', numbered='false')
                name = self.element('name')
                name.text = "Copyright Notice"
                section.append(name)
                paras = boilerplate_tlp[tlp][stream][:]
                if   ipr.startswith('nomodification'):
                    paras += boilerplate_tlp[tlp]['noModification'][:]
                elif ipr.startswith('noderivatives'):
                    paras += boilerplate_tlp[tlp]['noDerivatives'][:]
                elif ipr.startswith('pre5378'):
                    paras += boilerplate_tlp[tlp]['pre5378'][:]
                for para in paras:
                    t = self.element('t')
                    t.text = para.format(year=self.date.year)
                    section.append(t)
                e.append(section)
        
    # 5.2.7.  Section "toc" attribute
    # 
    #    ...
    #    o  for sections that have an ancestor of <boilerplate>, use "exclude"    

    def element_boilerplate_section(self, e, p):
        e.set('toc', 'exclude')

    # 5.4.3.  <reference> "target" Insertion
    # 
    #    For any <reference> element that does not already have a "target"
    #    attribute, fill the target attribute in if the element has one or
    #    more <seriesinfo> child element(s) and the "name" attribute of the
    #    <seriesinfo> element is "RFC", "Internet-Draft", or "DOI" or other
    #    value for which it is clear what the "target" should be.  The
    #    particular URLs for RFCs, Internet-Drafts, and Digital Object
    #    Identifiers (DOIs) for this step will be specified later by the RFC
    #    Editor and the IESG.  These URLs might also be different before and
    #    after the v3 format is adopted.
    def reference_insert_target(self, e, p):
        target_pattern = {
            "RFC":              "https://rfc-editor/info/rfc{value}",
            "DOI":              "https://doi.org/{value}",
            "Internet-Draft":   "https://tools.ietf.org/html/{value}",
        }
        if not e.get('target'):
            for c in e.xpath('.//seriesInfo'):
                series_name = c.get('name')
                if series_name in ['RFC', 'DOI', 'Internet-Draft']:
                    series_value=c.get('value')
                    if series_value:
                        e.set('target', target_pattern[series_name].format(value=series_value))
                        break
                    else:
                        self.err(c, 'Expected a value= attribute value for <seriesInfo name="%s">, but found none' % (series_name, ))

    # 
    # 5.4.4.  <name> Slugification
    # 
    #    Add a "slugifiedName" attribute to each <name> element that does not
    #    contain one; replace the attribute if it contains a value that begins
    #    with "n-".
    def name_insert_slugified_name(self, e, p):
        text = ' '.join(list(e.itertext()))
        slug = slugify_name('name-'+text)
        e.set('slugifiedName', slug)
        
    # 
    # 5.4.5.  <reference> Sorting
    # 
    #    If the "sortRefs" attribute of the <rfc> element is true, sort the
    #    <reference> and <referencegroup> elements lexically by the value of
    #    the "anchor" attribute, as modified by the "to" attribute of any
    #    <displayreference> element.  The RFC Editor needs to determine what
    #    the rules for lexical sorting are.  The authors of this document
    #    acknowledge that getting consensus on this will be a difficult task.
    def references_sort(self, e, p):
        global refname_mapping
        children = e.xpath('./reference')
        children.sort(key=lambda x: refname_mapping[x.get('anchor')])
        for c in children:
            e.remove(c)
        e[-1].tail = ''
        for c in children:
            e.append(c)

    # 5.4.6.  "pn" Numbering
    # 
    #    Add "pn" attributes for all parts.  Parts are:
    # 
    #    o  <section> in <middle>: pn='s-1.4.2'
    # 
    #    o  <references>: pn='s-12' or pn='s-12.1'
    # 
    #    o  <abstract>: pn='s-abstract'
    # 
    #    o  <note>: pn='s-note-2'
    # 
    #    o  <section> in <boilerplate>: pn='s-boilerplate-1'
    # 
    #    o  <table>: pn='t-3'
    # 
    #    o  <figure>: pn='f-4'
    # 
    #    o  <artwork>, <aside>, <blockquote>, <dt>, <li>, <sourcecode>, <t>:
    #       pn='p-[section]-[counter]'
    def boilerplate_section_add_number(self, e, p):
        self.boilerplate_section_number += 1
        e.set('pn', 'section-boilerplate.%s' % (self.boilerplate_section_number, ))

    def front_abstract_add_number(self, e, p):
        e.set('pn', 'section-abstract')

    def front_note_add_number(self, e, p):
        self.note_number += 1
        e.set('pn', 'section-note.%s' % (self.note_number, ))

    def middle_section_add_number(self, e, p):
        level = len(list(e.iterancestors('section')))
        if level > self.prev_section_level:
            self.middle_section_number.append(0)
        self.middle_section_number[level] += 1
        if level < self.prev_section_level:
            self.middle_section_number = self.middle_section_number[:level+1]
        e.set('pn', 'section-%s' % ('.'.join([ str(n) for n in self.middle_section_number ]), ))
        self.prev_section_level = level

    def table_add_number(self, e, p):
        self.table_number += 1
        e.set('pn', 'table-%s' % (self.table_number, ))

    def figure_add_number(self, e, p):
        self.figure_number += 1
        e.set('pn', 'figure-%s' % (self.figure_number, ))

    def references_add_number(self, e, p):
        self.references_number[0] = self.middle_section_number[0] + 1
        if len(list(p.iterchildren('references'))) > 1:
            if len(self.references_number) == 1:
                self.references_number.append(0)
            self.references_number[1] += 1
        e.set('pn', 'section-%s' % ('.'.join([ str(s) for s in self.references_number ]), ))

    def back_section_add_number(self, e, p):
        level = len(list(e.iterancestors('section')))
        if level > self.prev_section_level:
            self.back_section_number.append(0)
        self.back_section_number[level] += 1
        if level < self.prev_section_level:
            self.back_section_number = self.back_section_number[:level+1]
        section_number = self.back_section_number[:]
        section_number[0] = chr(0x60+section_number[0])
        e.set('pn', 'appendix-%s' % ('.'.join([ str(n) for n in section_number ]), ))
        self.prev_section_level = level

    def paragraph_add_number(self, e, p):
        # In this case, we need to keep track of separate paragraph number
        # sequences as we descend to child levels and return.  Handle this by
        # recursive descent.
        def child(s, prefix=None, num=None):
            para_tags = ['artwork', 'aside', 'blockquote', 'list', 'dl', 'dd', 'ol', 'ul', 'dt', 'li', 'sourcecode', 't']
            sect_tags = ['abstract', 'note', 'section', 'references' ]
            skip_tags = ['reference', ]
            if s.tag in sect_tags:
                prefix = s.get('pn')+'-'
                num = 0
            for c in s:
                if c.tag in para_tags:
                    if prefix is None:
                        debug.show('s.tag')
                        debug.show('s.items()')
                        debug.show('c.tag')
                        debug.show('c.items()')
                    num += 1
                    c.set('pn', prefix+str(num))
                if c.tag in sect_tags:
                    child(c)
                elif c.tag in skip_tags:
                    pass
                else:
                    num = child(c, prefix, num)
            return num
        child(e)

    # 5.4.7.  <iref> Numbering
    # 
    #    In every <iref> element, create a document-unique "pn" attribute.
    #    The value of the "pn" attribute will start with 'i-', and use the
    #    item attribute, the subitem attribute (if it exists), and a counter
    #    to ensure uniqueness.  For example, the first instance of "<iref
    #    item='foo' subitem='bar'>" will have the "irefid" attribute set to
    #    'i-foo-bar-1'.
    def iref_add_number(self, e, p):
        item = e.get('item')
        sub  = e.get('subitem')
        self.iref_number += 1
        if not item:
            self.err(e, "Expected <iref> to have an item= attribute, but found none")
        else:
            if sub:
                e.set('pn', slugify_name('iref-%s-%s-%s' % (item, sub, self.iref_number)))
            else:
                e.set('pn', slugify_name('iref-%s-%s' % (item, self.iref_number)))


    # 5.4.8.  <xref> Processing
    # 
    # 5.4.8.1.  "derivedContent" Insertion (with Content)
    # 
    #    For each <xref> element that has content, fill the "derivedContent"
    #    with the element content, having first trimmed the whitespace from
    #    ends of content text.  Issue a warning if the "derivedContent"
    #    attribute already exists and has a different value from what was
    #    being filled in.
    # 
    # 5.4.8.2.  "derivedContent" Insertion (without Content)
    # 
    #    For each <xref> element that does not have content, fill the
    #    "derivedContent" attribute based on the "format" attribute.
    # 
    #    o  For a value of "counter", the "derivedContent" is set to the
    #       section, figure, table, or ordered list number of the element with
    #       an anchor equal to the <xref> target.
    # 
    #    o  For format='default' and the "target" attribute points to a
    #       <reference> or <referencegroup> element, the "derivedContent" is
    #       the value of the "target" attribute (or the "to" attribute of a
    #       <displayreference> element for the targeted <reference>).
    # 
    #    o  For format='default' and the "target" attribute points to a
    #       <section>, <figure>, or <table>, the "derivedContent" is the name
    #       of the thing pointed to, such as "Section 2.3", "Figure 12", or
    #       "Table 4".
    # 
    #    o  For format='title', if the target is a <reference> element, the
    #       "derivedContent" attribute is the name of the reference, extracted
    #       from the <title> child of the <front> child of the reference.
    # 
    #    o  For format='title', if the target element has a <name> child
    #       element, the "derivedContent" attribute is the text content of
    #       that <name> element concatenated with the text content of each
    #       descendant node of <name> (that is, stripping out all of the XML
    #       markup, leaving only the text).
    # 
    #    o  For format='title', if the target element does not contain a
    #       <name> child element, the "derivedContent" attribute is the value
    #       of the "target" attribute with no other adornment.  Issue a
    #       warning if the "derivedContent" attribute already exists and has a
    #       different value from what was being filled in.
    def element_xref(self, e, p):
        def split_pn(t, pn):
            if pn is None:
                self.die(e, "Expected to find a pn= attribute on <%s anchor='%s'> when processing <xref>, but found none" % (t.tag, t.get('anchor')), trace=True)
            type, num = pn.split('-')[:2]
            return type, num
        #
        if e.text:
            value = e.text.strip()
        else:
            target = e.get('target')
            if not target:
                self.die(e, "Expected <xref> to have a target= attribute, but found none")
            format = e.get('format')
            if not format:
                self.die(e, "<xref> format= value should have been filled in with its default!", trace=True)
            t = self.root.find('.//*[@anchor="%s"]'%(target, ))
            if t is None:
                self.die(e, "Found no element to match the <xref> target attribute '%s'" % (target, ))
            pn = t.get('pn')
            #
            if   format == 'counter':
                if not t.tag in ['section', 'table', 'figure', 'li']:
                    self.die(e, "Using <xref> format='counter' with a <%s> target is not supported" % (t.tag, ))
                if t.tag == 'li':
                    parent = t.getparent()
                    if not parent.tag == 'ol':
                        self.die(e, "Using <xref> format='counter' with a <%s><%s> target is not supported" %(parent.tag, t.tag, ))
                type, num = split_pn(t, pn)
                value = num
            elif format == 'default':
                if t.tag in [ 'reference', 'referencegroup' ]:
                    value = refname_mapping[t.get('anchor')]
                else:
                    type, num = split_pn(t, pn)
                    value = e.text if e.text else "%s %s" % (type.capitalize(), num)
            elif format == 'title':
                if t.tag == 'reference':
                    title = t.find('./front/title')
                    if title is None:
                        self.err(t, "Expected a <title> element when processing <xref> to <%s>, but found none" % (t.tag, ))
                    value = title.text
                elif t.find('./name') != None:
                    name = t.find('./name')
                    value = ' '.join(list(name.itertext()))
                else:
                    value = target
            elif format == 'none':
                value = ''
            else:
                self.err(e, "Expected format to be one of 'default', 'title', 'counter' or 'none', but found '%s'" % (format, ) )
        #
        attr = e.get('derivedContent')
        if attr and attr != value:
            self.err(e, "When processing <xref>, found derivedContent='%s' when trying to set it to '%s'" % (attr, value))
        e.set('derivedContent', value)
        # relative= processing
        if e.get('relative') or e.get('section'):
            self.element_relref(e, p, t)

    # 5.4.9.  <relref> Processing
    # 
    #    If any <relref> element's "target" attribute refers to anything but a
    #    <reference> element, give an error.
    # 
    #    For each <relref> element, fill in the "derivedLink" attribute.
    def element_relref(self, e, p, t=None):
        if t is None:
            target = e.get('target')
            t = self.root.find('.//*[@anchor="%s"]'%(target, ))
        section = e.get('section')
        if section is None:
            self.err("Cannot render an <%s> with a relative= attribute without also having a section= attribute." % (e.tag))
        if t.tag != 'reference':
            self.err(e, "Expected the target of an <%s> with a section= attribute to be a <reference>, found <%s>" % (e.tag, t.tag, ))
        relative = e.get('relative')
        if relative is None:
            for s in t.xpath('.//seriesInfo'):
                if s.get('name') in ['RFC', 'Internet-Draft']:
                    relative = 'section-%s' % section
                    break
            if not relative:
                self.err(e, "Cannot build a href for this <%s> with a section= attribute without also having a relative= attribute." % (e.tag))
        if relative:
            url = t.get('target')
            if url is None:
                self.err(e, "Cannot build a href for <reference anchor='%s'> without having a target= attribute giving the URL." % (target, ))
            link = "%s#%s" % (url, relative)
            e.set('derivedLink', link)

    # 5.5.  Inclusion
    # 
    #    These steps will include external files into the output document.
    # 
    # 5.5.1.  <artwork> Processing
    # 
    def check_src_scheme(self, e, src):
        permitted_schemes = ['file', 'http', 'https', 'data', ]
        e.set('originalSrc', src)
        scheme, netloc, path, query, fragment = urlsplit(src)
        if scheme == '':
            scheme = 'file'
        if not scheme in permitted_schemes:
            self.err(e, "Expected an <%s> src scheme of '%s:', but found '%s:'" % (e.tag, scheme, ":', '".join(permitted_schemes)))
        return (scheme, netloc, path, query, fragment)

    def check_src_file_path(self, e, scheme, netloc, path, query, fragment):
        shellmeta = re.compile("[><*[`$|;&(#]")
        #
        dir = os.path.abspath(os.path.dirname(self.xmlrfc.source))
        path = os.path.abspath(os.path.join(dir, path))
        if not path.startswith(dir):
            self.err(e, "Expected an <%s> src= file located beside or below the .xml source (in %s), but found a reference to %s" % (e.tag, dir, path))
            return None
        src = urlunsplit((scheme, '', path, '', ''))
        if shellmeta.search(src):
            self.err(e, "Found disallowed shell meta-characters in the src='file:...' attribute")
            return None
        if not os.path.exists(path):
            self.err(e, "Expected an <%s> src= file at '%s', but no such file exists" % (e.tag, path, ))
            return None
        #
        e.set('src', src)
        return src

    def element_artwork(self, e, p):

    #    1.  If an <artwork> element has a "src" attribute where no scheme is
    #        specified, copy the "src" attribute value to the "originalSrc"
    #        attribute, and replace the "src" value with a URI that uses the
    #        "file:" scheme in a path relative to the file being processed.
    #        See Section 7 for warnings about this step.  This will likely be
    #        one of the most common authoring approaches.
            
        src = e.get('src','').strip()
        if src:
            scheme, netloc, path, query, fragment = self.check_src_scheme(e, src)

    #    2.  If an <artwork> element has a "src" attribute with a "file:"
    #        scheme, and if processing the URL would cause the processor to
    #        retrieve a file that is not in the same directory, or a
    #        subdirectory, as the file being processed, give an error.  If the
    #        "src" has any shellmeta strings (such as "`", "$USER", and so on)
    #        that would be processed, give an error.  Replace the "src"
    #        attribute with a URI that uses the "file:" scheme in a path
    #        relative to the file being processed.  This rule attempts to
    #        prevent <artwork src='file:///etc/passwd'> and similar security
    #        issues.  See Section 7 for warnings about this step.
            if scheme == 'file':
                src = self.check_src_file_path(e, scheme, netloc, path, query, fragment)

    #    3.  If an <artwork> element has a "src" attribute, and the element
    #        has content, give an error.

        ## This is nonsense, since the element content is specified for use
        ## as a fallback if the rendering medium cannot handle the "src"
        ## format.  See https://tools.ietf.org/html/rfc7991#section-2.5

    #    4.  If an <artwork> element has type='svg' and there is an "src"
    #        attribute, the data needs to be moved into the content of the
    #        <artwork> element.

            if src:                             # Test again, after check_src_file_path()
                awtype = e.get('type')
                if awtype == 'svg':

    #        *  If the "src" URI scheme is "data:", fill the content of the
    #           <artwork> element with that data and remove the "src"
    #           attribute.

        ## This conflicts with https://tools.ietf.org/html/rfc7991#section-2.5
        ## and destroys content.  Will turn external src content into a data:
        ## url if there is text content in <artwork>.

                    awtext = (' '.join(list(e.itertext()))).strip()
                    svg = None
                    if awtext:
                        # keep svg in src attribute
                        if scheme in ['file', 'http', 'https']:
                            f = urlopen(src)
                            data = f.read()
                            if six.PY2:
                                mediatype = f.info().gettype()
                            else:
                                mediatype = f.info().get_content_type()
                            f.close()
                            src = build_dataurl(mediatype, data)
                            e.set('src', src)

    #        *  If the "src" URI scheme is "file:", "http:", or "https:", fill
    #           the content of the <artwork> element with the resolved XML
    #           from the URI in the "src" attribute.  If there is no
    #           "originalSrc" attribute, add an "originalSrc" attribute with
    #           the value of the URI and remove the "src" attribute.
                    else:
                        f = urlopen(src)
                        data = f.read()
                        f.close()
                        svg = etree.fromstring(data)
                        e.append(svg)
                        del e.attrib['src']

    #        *  If the <artwork> element has an "alt" attribute, and the SVG
    #           does not have a <desc> element, add the <desc> element with
    #           the contents of the "alt" attribute.
                    alt = e.get('alt')
                    if alt and svg != None:
                        if not svg.xpath('.//desc'):
                            desc = self.element('desc')
                            desc.text = alt
                            svg.append(desc)

    #    5.  If an <artwork> element has type='binary-art', the data needs to
    #        be in an "src" attribute with a URI scheme of "data:".  If the
    #        "src" URI scheme is "file:", "http:", or "https:", resolve the
    #        URL.  Replace the "src" attribute with a "data:" URI, and add an
    #        "originalSrc" attribute with the value of the URI.  For the
    #        "http:" and "https:" URI schemes, the mediatype of the "data:"
    #        URI will be the Content-Type of the HTTP response.  For the
    #        "file:" URI scheme, the mediatype of the "data:" URI needs to be
    #        guessed with heuristics (this is possibly a bad idea).  This also
    #        fails for content that includes binary images but uses a type
    #        other than "binary-art".  Note: since this feature can't be used
    #        for RFCs at the moment, this entire feature might be
                elif awtype == 'binary-art':
                    # keep svg in src attribute
                    if scheme in ['http', 'https']:
                        with urlopen(src) as f:
                            data = f.read()
                            if six.PY2:
                                mediatype = f.info().gettype()
                            else:
                                mediatype = f.info().get_content_type()
                        src = build_dataurl(mediatype, data)
                        e.set('src', src)
                    elif scheme == 'file':
                        self.err(e, "Won't guess media-type of file '%s', please use the data: scheme instead." % (src, ))

    #    6.  If an <artwork> element does not have type='svg' or
    #        type='binary-art' and there is an "src" attribute, the data needs
    #        to be moved into the content of the <artwork> element.  Note that
    #        this step assumes that all of the preferred types other than
    #        "binary-art" are text, which is possibly wrong.
    # 
    #        *  If the "src" URI scheme is "data:", fill the content of the
    #           <artwork> element with the correctly escaped form of that data
    #           and remove the "src" attribute.
    # 
    #        *  If the "src" URI scheme is "file:", "http:", or "https:", fill
    #           the content of the <artwork> element with the correctly
    #           escaped form of the resolved text from the URI in the "src"
    #           attribute.  If there is no "originalSrc" attribute, add an
    #           "originalSrc" attribute with the value of the URI and remove
    #           the "src" attribute.
                else:
                    with urlopen(src) as f:
                        data = f.read()
                    debug.type('data')
                    e.text = data
                    del e.attrib['src']

    # 5.5.2.  <sourcecode> Processing

    def element_sourcecode(self, e, p):
    #    1.  If a <sourcecode> element has a "src" attribute where no scheme
    #        is specified, copy the "src" attribute value to the "originalSrc"
    #        attribute and replace the "src" value with a URI that uses the
    #        "file:" scheme in a path relative to the file being processed.
    #        See Section 7 for warnings about this step.  This will likely be
    #        one of the most common authoring approaches.
        src = e.get('src','').strip()
        if src:
            scheme, netloc, path, query, fragment = self.check_src_scheme(e, src)


    #    2.  If a <sourcecode> element has a "src" attribute with a "file:"
    #        scheme, and if processing the URL would cause the processor to
    #        retrieve a file that is not in the same directory, or a
    #        subdirectory, as the file being processed, give an error.  If the
    #        "src" has any shellmeta strings (such as "`", "$USER", and so on)
    #        that would be processed, give an error.  Replace the "src"
    #        attribute with a URI that uses the "file:" scheme in a path
    #        relative to the file being processed.  This rule attempts to
    #        prevent <sourcecode src='file:///etc/passwd'> and similar
    #        security issues.  See Section 7 for warnings about this step.
            if scheme == 'file':
                src = self.check_src_file_path(e, scheme, netloc, path, query, fragment)

    #    3.  If a <sourcecode> element has a "src" attribute, and the element
    #        has content, give an error.
            srctext = (' '.join(list(e.itertext()))).strip()
            if srctext:
                self.err(e, "Expected either external src= content, or element content for <%s>, but found both" % (e.tag, ))

    #    4.  If a <sourcecode> element has a "src" attribute, the data needs
    #        to be moved into the content of the <sourcecode> element.
    # 
    #        *  If the "src" URI scheme is "data:", fill the content of the
    #           <sourcecode> element with that data and remove the "src"
    #           attribute.
    # 
    #        *  If the "src" URI scheme is "file:", "http:", or "https:", fill
    #           the content of the <sourcecode> element with the resolved XML
    #           from the URI in the "src" attribute.  If there is no
    #           "originalSrc" attribute, add an "originalSrc" attribute with
    #           the value of the URI and remove the "src" attribute.

            if src:                             # Test again, after check_src_file_path()
                with urlopen(src) as f:
                    data = f.read()
                e.text = data
                del e.attrib['src']

    # 5.6.  RFC Production Mode Cleanup
    # 
    #    These steps provide extra cleanup of the output document in RFC
    #    production mode.
    # 
    # 5.6.1.  <note> Removal
    # 
    #    In RFC production mode, if there is a <note> or <section> element
    #    with a "removeInRFC" attribute that has the value "true", remove the
    #    element.
    def attribute_removeinrfc_true(self, e, p):
        if self.options.rfc:
            p.remove(e)

    # 5.6.2.  <cref> Removal
    # 
    #    If in RFC production mode, remove all <cref> elements.
    def cref_removal(self, e, p):
        if self.options.rfc:
            p.remove(e)

    # 5.6.3.  <link> Processing
    def attribute_link_rel_alternate_removal(self, e, p):
        if self.options.rfc:
    #    1.  If in RFC production mode, remove all <link> elements whose "rel"
    #        attribute has the value "alternate".
            if e.get('rel') == 'alternate':
                p.remove(e)
                return

    #    2.  If in RFC production mode, check if there is a <link> element
    #        with the current ISSN for the RFC series (2070-1721); if not, add
    #        <link rel="item" href="urn:issn:2070-1721">.
    def check_links_required(self, e, p):
        if self.options.rfc:
            item_href = "urn:issn:2070-1721"
            urnlink = e.find('.//link[@rel="item"][@href="%s"]' % (item_href, ))
            if urnlink is None :
                e.insert(0, self.element('link', rel='item', href=item_href))
    #    3.  If in RFC production mode, check if there is a <link> element
    #        with a DOI for this RFC; if not, add one of the form <link
    #        rel="describedBy" href="https://dx.doi.org/10.17487/rfcdd"> where
    #        "dd" is the number of the RFC, such as
    #        "https://dx.doi.org/10.17487/rfc2109".  The URI is described in
    #        [RFC7669].  If there was already a <link> element with a DOI for
    #        this RFC, check that the "href" value has the right format.  The
    #        content of the href attribute is expected to change in the
    #        future.
            doi_href = "https://dx.doi.org/10.17487/rfc%s" % self.rfcnumber
            doilink = e.find('.//link[@rel="describedBy"]')
            if doilink is None:
                e.insert(0, self.element('link', rel='describedBy', href=doi_href))

    # 
    #    4.  If in RFC production mode, check if there is a <link> element
    #        with the file name of the Internet-Draft that became this RFC the
    #        form <link rel="convertedFrom"
    #        href="https://datatracker.ietf.org/doc/draft-tttttttttt/">.  If
    #        one does not exist, give an error.
            converted_from = e.find('.//link[@rel="convertedFrom"]')
            if converted_from is None:
                self.warn(e, "Expected a <link> with rel='convertedFrom' providing the datatracker url for the origin draft.")
            else:
                converted_from_href = converted_from.get('href', '')
                if not converted_from_href.startswith("https://datatracker.ietf.org/doc/draft-"):
                    self.err(converted_from, "Expected the <link rel='convertedFrom'> href= to have the form 'https://datatracker.ietf.org/doc/draft-...', but found '%s'" % (converted_from_href, ))

    # 5.6.4.  XML Comment Removal
    # 
    #    If in RFC production mode, remove XML comments.
    def comment_removal(self, e, p):
        if self.options.rfc:
            p.remove(e)

    # 5.6.5.  "xml:base" and "originalSrc" Removal
    # 
    #    If in RFC production mode, remove all "xml:base" or "originalSrc"
    #    attributes from all elements.
    def attribute_removal(self, e, p):
        if self.options.rfc:
            for c in e.iterfind('.//*[@xml:base]', namespaces={'xml':'http://www.w3.org/XML/1998/namespace', }):
                del c.attrib['{http://www.w3.org/XML/1998/namespace}base']
            for c in e.iterfind('.//*[@originalSrc]'):
                del c.attrib['originalSrc']

    # 5.6.6.  Compliance Check
    # 
    #    If in RFC production mode, ensure that the result is in full
    #    compliance to the v3 schema, without any deprecated elements or
    #    attributes and give an error if any issues are found.
    def validate_after(self, e, p):
        # XXX: There is an issue with exponential increase in validation time
        # as a function of the number of attributes on the root element.  See
        # https://bugzilla.gnome.org/show_bug.cgi?id=133736 .  In our schema,
        # there is no dependency in the underlying schema on the root element
        # attributes, on the order of minutes for the full set of possble
        # attribute values.  In order to avoid very long validation times, we
        # strip the root attributes before validation, and put them back
        # afterwards.  
        for k in e.keys():
            if not e.get(k):
                del e.attrib[k]
        attrib = copy.deepcopy(e.attrib) 
        for k in attrib.keys():
            del e.attrib[k]
        if not self.validate('after'):
            log.note("Schema validation failed for input document")
        keys = list(attrib.keys())
        keys.sort()
        for k in keys:
            e.set(k, attrib[k])

    # 5.7.  Finalization
    # 
    #    These steps provide the finishing touches on the output document.

    # 5.7.1.  "scripts" Insertion
    # 
    #    Determine all the characters used in the document and fill in the
    #    "scripts" attribute for <rfc>.
    def insert_scripts(self, e, p):
        text = ' '.join(e.itertext())
        scripts = ','.join(sorted(list(get_scripts(text))))
        e.set('scripts', scripts)

    # 5.7.2.  Pretty-Format
    # 
    #    Pretty-format the XML output.  (Note: there are many tools that do an
    #    adequate job.)
    def pretty_print_prep(self, e, p):
        # apply this to elements that can't appear with text, i.e., don't have
        # any of these as parent:
        skip_parents = set([
            "annotation", "blockquote", "preamble", "postamble", "name", "refcontent", "c", "t",
            "cref", "dd", "dt", "li", "td", "th", "tt", "em", "strong", "sub", "sup", ])
        for c in e.iter():
            p = c.getparent()
            if p != None and p.tag in skip_parents:
                continue
            if c.tail != None:
                if c.tail.strip() == '':
                    c.tail = None        
        ## The actual pretty-printing is done in self.write()
