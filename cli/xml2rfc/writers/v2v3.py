# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import os
import re
import lxml.etree
import datetime
import traceback as tb
from io import open
from xml2rfc import log
from xml2rfc.writers.base import default_options
from lxml.etree import Element, Comment, CDATA, _Comment

try:
    import debug
    assert debug
except ImportError:
    pass

def slugify(s):
    s = s.strip().lower()
    s = re.sub(r'[^\w\s/|@=-]', '', s)
    s = re.sub(r'[-_\s/|@=]+', '_', s)
    s = s.strip('_')
    return s

def idref(s):
    s = re.sub(r'^[^A-Za-z_]', '_', s)
    s = re.sub(r'[^-._A-Za-z0-9]', '-', s)
    return s

def stripattr(e, attrs):
    for a in attrs:
        if a in e.keys():
            del e.attrib[a]

def copyattr(a, b):
    for k in a.keys():
        v = a.get(k)
        b.set(k, v)

def isempty(e):
    return not ((len(e) and any([ not isinstance(c, _Comment) for c in e.iterchildren() ]))
                or (e.text and e.text.strip()) or (e.tail and e.tail.strip()))

def isblock(e):
    return e.tag in [ 'artwork', 'dl', 'figure', 'ol', 'sourcecode', 't', 'ul', ]

def iscomment(e):
    return isinstance(e, _Comment)

def hastext(e):
    head = [ e.text ] if e.text and e.text.strip() else []
    items = head + [ c for c in e.iterchildren() if not (isblock(c) or iscomment(c))] + [ c.tail for c in e.iterchildren() if c.tail and c.tail.strip() ]
    return items

class V2v3XmlWriter:
    """ Writes an XML file with v2 constructs converted to v3"""

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today()):
        if not quiet is None:
            options.quiet = quiet
        self.xmlrfc = xmlrfc
        self.root = xmlrfc.getroot()
        self.options = options

    def validate(self):
        v3_rng_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'v3.rng')
        v3_rng = lxml.etree.RelaxNG(file=v3_rng_file)
        try:
            v3_rng.assertValid(self.root)
            log.note("The document validates according to the RFC7991 schema")
        except Exception as e:
            # These warnings are occasionally incorrect -- disable this
            # output for now:
            #log.warn('\nInvalid document: %s' % (e,))
            e = e

    def add_xinclude(self):
        for e in self.root.xpath('.//back//reference'):
            p = e.getparent()
            for si in e.xpath('.//seriesInfo'):
                if si.get('name') == 'RFC':
                    num = si.get('value', '')
                    if num and num.isdigit():
                        xi = self.element('{http://www.w3.org/2001/XInclude}include',
                                    nsmap=self.xmlrfc.nsmap,
                                    href="https://xml2rfc.tools.ietf.org/public/rfc/bibxml/reference.RFC.%s.xml"%num)
                        i = p.index(e)
                        p.remove(e)
                        p.insert(i, xi)
                    else:
                        self.warn('Invalid value in %s' % lxml.etree.tostring(e))
                elif si.get('name') == 'Internet-Draft':
                    name = si.get('value', '')
                    if name:
                        tag = name[len('draft-'):] if name.startswith('draft-') else name
                        xi = self.element('{http://www.w3.org/2001/XInclude}include',
                                    nsmap=self.xmlrfc.nsmap,
                                    href="https://xml2rfc.tools.ietf.org/publicrfc/bibxml3/reference.I-D.%s.xml"%tag)
                        i = p.index(e)
                        p.remove(e)
                        p.insert(i, xi)
                    else:
                        self.warn('Invalid value in %s' % lxml.etree.tostring(e))
        lxml.etree.cleanup_namespaces(self.root, top_nsmap=self.xmlrfc.nsmap)


    def post_process_lines(self, lines):
        output = [ line.replace(u'\u00A0', ' ') for line in lines ]
        return output

    def write(self, filename):
        """ Public method to write the XML document to a file """

        self.convert2to3()
        self.validate()
        if self.options.add_xinclude:
            self.add_xinclude()

        # Use lxml's built-in serialization
        file = open(filename, 'w', encoding='utf-8')
        text = lxml.etree.tostring(self.root.getroottree(), 
                                       xml_declaration=True, 
                                       encoding='utf-8',
                                       pretty_print=True)
        file.write(text.decode('utf-8'))

        if not self.options.quiet:
            log.write('Created file', filename)

    # --- Element Operations -------------------------------------------

    def element(self, tag, *args, **kwargs):
        e = Element(tag, **kwargs)
        if self.options.debug:
            filename, lineno, caller, code = tb.extract_stack()[-2]
            e.set('line', str(lineno))
        if args:
            assert len(args) == 1
            text = args[0]
            e.text = text
        return e

    def copy(self, e, tag):
        n = self.element(tag)
        n.text = e.text
        n.tail = e.tail
        copyattr(e, n)
        for c in e.iterchildren():
            n.append(c)                 # moves c from e to n
        return n

    def replace(self, a, b, comments=None):
        if isinstance(b, type('')):
            b = self.element(b)
        if comments is None:
            if b is None:
                comments = ['Removed deprecated tag <%s/>' % (a.tag, ) ]
            else:
                comments = ['Replaced <%s/> with <%s/>' % (a.tag, b.tag) ]
        if not isinstance(comments, list):
            comments = [comments]
        p = a.getparent()
        i = p.index(a)
        c = None
        if self.options.verbose:
            for comment in comments:
                c = Comment(" v2v3: %s " % comment.strip())
                p.insert(i, c)
                i += 1
        if not b is None:
            if a.text and a.text.strip():
                b.text = a.text
            if a.tail and a.tail.strip():
                b.tail = a.tail
            copyattr(a, b)
            for child in a.iterchildren():
                b.append(child)         # moves child from a to b
            p.replace(a, b)
        else:
            if a.tail:
                if c is None:
                    p.text = p.text + ' ' + a.tail if p.text else a.tail
                else:
                    c.tail = a.tail
            p.remove(a)
        return b

    def move_after(self, a, b, comments=None):
        if comments is None:
            comments = ["Moved <%s/> to a new position"]
        if not isinstance(comments, list):
            comments = [comments]
        pa = a.getparent()
        pb = b.getparent()
        sa = a.getprevious()
        if a.tail:
            if sa != None:
                if sa.tail:
                    sa.tail += ' ' + a.tail
                else:
                    sa.tail = a.tail
            else:
                if pa.text and pa.text.strip():
                    pa.text += ' ' + a.tail
                else:
                    if a.tail and a.tail.strip():
                        pa.text = a.tail
            a.tail = None
        i = pb.index(b)+1
        pb.insert(i, a)
        if self.options.verbose:
            for comment in comments:
                c = Comment(" v2v3: %s " % comment.strip())
                pb.insert(i, c)

    def promote(self, e, t):
        assert t.tag == 't'
        pp = t.getparent()
        i = pp.index(t)+1
        t2 = self.element('t')
        t2.text = e.tail
        e.tail = None
        for s in e.itersiblings():
            t2.append(s)                # removes s from t
        if not isempty(t2):
            pp.insert(i, t2)
        pp.insert(i, e)                 # removes e from t
        if self.options.verbose:
            pp.insert(i, Comment(" v2v3: <%s/> promoted to be child of <%s/>, and the enclosing <t/> split. " % (e.tag, pp.tag)))
        if isempty(t):
            pp.remove(t)

    def wrap_content(self, e, t=None):
        if t is None:
            t = self.element('t')
        t.text = e.text
        e.text = None
        for c in e.iterchildren():
            t.append(c)
        e.append(t)
        return t

    # ------------------------------------------------------------------

    def convert2to3(self):
        selectors = [
            # we need to process list before block elements that might get
            # promoted out of their surrounding <t/>, as <list/> uses one <t/>
            # per list item, and if we promote block elements earlier, they
            # will not be picked up as part of the list items
            './/list',                      # 3.4.  <list>
            #
            './/artwork',                   # 2.5.  <artwork>
                                            # 2.5.4.  "height" Attribute
                                            # 2.5.8.  "width" Attribute
                                            # 2.5.9.  "xml:space" Attribute
            './/figure',                    # 2.25.  <figure>
                                            # 2.25.1.  "align" Attribute
                                            # 2.25.2.  "alt" Attribute
                                            # 2.25.4.  "height" Attribute
                                            # 2.25.5.  "src" Attribute
                                            # 2.25.6.  "suppress-title" Attribute
                                            # 2.25.8.  "width" Attribute
            './/reference',                 #        <reference>
            '.',                            # 2.45.  <rfc>
                                            # 2.45.1.  "category" Attribute
                                            # 2.45.2.  "consensus" Attribute
                                            # 2.45.3.  "docName" Attribute
                                            # 2.45.7.  "number" Attribute
                                            # 2.45.10.  "seriesNo" Attribute
            './/seriesInfo',                # 2.47.  <seriesInfo>
            './/t',                         # 2.53.  <t>
                                            # 2.53.2.  "hangText" Attribute
            './/xref',                      # 2.66.  <xref>
                                            # 2.66.1.  "format" Attribute
                                            # 2.66.2.  "pageno" Attribute
            './/facsimile',                 # 3.2.  <facsimile>
            './/format',                    # 3.3.  <format>
            './/postamble',                 # 3.5.  <postamble>
            './/preamble',                  # 3.6.  <preamble>
            './/spanx',                     # 3.7.  <spanx>
            './/texttable',                 # 3.8.  <texttable>
            './/vspace',                    # 3.10.  <vspace>
            # attribute selectors
            './/*[@title]',
                                            # 2.25.7.  "title" Attribute
                                            # 2.33.2.  "title" Attribute
                                            # 2.42.2.  "title" Attribute
                                            # 2.46.4.  "title" Attribute
            './/*[@anchor]',
            './/xref[@target]',
            './/processing-instruction()',  # 1.3.2
            # handle mixed block/non-block content surrounding all block nodes
            './/*[self::artwork or self::dl or self::figure or self::ol or self::sourcecode or self::t or self::ul]',
            './/*[@*="yes" or @*="no"]',      # convert old attribute false/true
            '.;pretty_print_prep()',
        ]

        # replace the vocabulary v2 dtd, but keep some entity definitions.
        tree = self.root.getroottree()
        tree.docinfo.system_url = "rfc2629-xhtml.ent"

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
                for e in self.root.xpath(ss):
                    func(e, e.getparent())
            else:
                log.warn("No handler for function %s, slug %s" % (func_name, slug, ))

    # ----------------------------------------------------------------------

    # 1.3.2.  New Attributes for Existing Elements
    # 
    #    o  Add "sortRefs", "symRefs", "tocDepth", and "tocInclude" attributes
    #       to <rfc> to cover Processing Instructions (PIs) that were in v2
    #       that are still needed in the grammar.  ...
    def processing_instruction(self, e, p):
        rfc_element = self.root.find('.')
        pi_name = {
            'sortrefs': 'sortRefs',
            'symrefs':  'symRefs',
            'docdepth': 'tocDepth',
            'toc':      'tocInclude',
        }
        for k, a in pi_name.items():
            if k in e.attrib:
                v = e.get(k)
                if v == 'yes':
                    v = 'true'
                rfc_element.set(a, v)
                self.replace(e, None, 'Moved %s PI to <rfc %s="%s"' % (k, a, v))

    # 1.3.4.  Additional Changes from v2
    # 
    #    o  Make <seriesInfo> a child of <front>, and deprecated it as a child
    #       of <reference>.  This also deprecates some of the attributes from
    #       <rfc> and moves them into <seriesInfo>.
    def element_seriesinfo(self, e, p):
        if   p.tag == 'front':
            pass
        elif p.tag == 'reference':
            title = p.find('./front/title')
            self.move_after(e, title, "Moved <seriesInfo/> inside <front/> element")

    # 1.3.4.  Additional Changes from v2
    #
    #    o  <t> now only contains non-block elements, so it no longer contains
    #       <figure> elements.
    def element_artwork_dl_figure_ol_sourcecode_t_ul(self, e, p):
        # check if we have any text or non-block-elements next to the
        # element.  If so, embed in <t/> and then promote the element.
        nixmix_tags = [ 'blockquote', 'li', 'dd', 'td', 'th']
        if p.tag in nixmix_tags and hastext(p):
            #debug.say('Wrap %s content ...'%(p.tag))
            self.wrap_content(p)
        p = e.getparent()
        #pp = p.getparent()
        if p.tag == 't':
            #debug.say('Promote %s (parent %s, grandparent %s) ...'%(e.tag, p.tag, pp.tag))
            self.promote(e, p)

    # 2.5.  <artwork>
    # 
    # 2.5.4.  "height" Attribute
    # 
    #    Deprecated.
    # 
    # 2.5.8.  "width" Attribute
    # 
    #    Deprecated.
    # 
    # 2.5.9.  "xml:space" Attribute
    # 
    #    Deprecated.
    def element_artwork(self, e, p):
        e.text = CDATA(e.text)          # prevent text from being mucked up by other processors
        stripattr(e, ['height', '{http://www.w3.org/XML/1998/namespace}space', 'width', ])
        if re.search(r'^\s*<CODE BEGINS>', e.text):
            # We have source code.  Permitted attributes: anchor, name,
            # source, type.
            e = self.replace(e, 'sourcecode')
            match = re.search(r'(?s)^\s*<CODE BEGINS>(\s+file\s+"([^"]*)")?(.*?)(<CODE ENDS>(.*))?$', e.text)
            file = match.group(1)
            name = match.group(2)
            body = match.group(3)
            ends = match.group(4)
            tail = match.group(5)
            if file and name:
                e.set('name', name)
            e.text = CDATA(body)
            if not ends:
                self.warn("Found <CODE BEGINS> without matching <CODE ENDS>")
            if ends and tail.strip() != "":
                self.warn("Found non-whitespace content after <CODE ENDS>")
                e.tail = tail
            stripattr(e, ['align', 'alt', 'height', 'suppress-title', 'width', ])


    # 2.25.  <figure>
    # 
    # 2.25.1.  "align" Attribute
    # 
    #    Deprecated.
    # 
    # 2.25.2.  "alt" Attribute
    # 
    #    Deprecated.  If the goal is to provide a single URI for a reference,
    #    use the "target" attribute in <reference> instead.
    # 
    # 2.25.4.  "height" Attribute
    # 
    #    Deprecated.
    # 
    # 2.25.5.  "src" Attribute
    # 
    #    Deprecated.
    # 
    # 2.25.6.  "suppress-title" Attribute
    # 
    #    Deprecated.
    # 
    #    Allowed values:
    # 
    #    o  "true"
    # 
    #    o  "false" (default)
    # 
    # 2.25.7.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.25.8.  "width" Attribute
    # 
    #    Deprecated.
    # 
    def element_figure(self, e, p):
        comments = []
        artwork = e.find('./artwork')
        if not artwork is None:
            for attr in ['alt', 'src', ]:
                if attr in e.attrib:
                    fattr = e.get(attr)
                    if attr in artwork.attrib:
                        aattr = artwork.get(attr)
                        if fattr != aattr:
                            comments.append('Warning: The "%s" attribute on artwork differs from the one on figure.  Using only "%s" on artwork.' % (attr, attr))
                    else:
                        artwork.set(attr, fattr)
        stripattr(e, ['align', 'alt', 'height', 'src', 'suppress-title', 'width', ])

    # 2.25.7.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.33.2.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.42.2.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 2.46.4.  "title" Attribute
    # 
    #    Deprecated.  Use <name> instead.
    # 
    # 3.8.5.  "title" Attribute
    # 
    #    Deprecated.
    def attribute_title(self, e, p):
        n = self.element('name')
        n.text = e.get('title').strip()
        if n.text:
            e.insert(0, n)
            if self.options.verbose:
                c = Comment(" v2v3: Moved attribute title to <name/> ")
                e.insert(0, c)
        stripattr(e, ['title', ])

    def element_reference(self, e, p):
        if 'quote-title' in e.attrib:
            v = 'true' if e.get('quote-title') in ['true', 'yes'] else 'false'
            if v != 'true':             # no need to set default value
                e.set('quoteTitle', v)
        stripattr(e, ['quote-title'])

    # 2.45.  <rfc>
    # 
    # 2.45.1.  "category" Attribute
    # 
    #    Deprecated; instead, use the "name" attribute in <seriesInfo>.
    # 
    # 2.45.2.  "consensus" Attribute
    # 
    #    Affects the generated boilerplate.  Note that the values of "no" and
    #    "yes" are deprecated and are replaced by "false" (the default) and
    #    "true".
    # 
    # 2.45.3.  "docName" Attribute
    # 
    #    Deprecated; instead, use the "value" attribute in <seriesInfo>.
    # 
    # 2.45.7.  "number" Attribute
    # 
    #    Deprecated; instead, use the "value" attribute in <seriesInfo>.
    # 
    # 2.45.10.  "seriesNo" Attribute
    # 
    #    Deprecated; instead, use the "value" attribute in <seriesInfo>.
    def element_rfc(self, e, p):
#         category_strings = {
#             "std": "Standards Track",
#             "bcp": "Best Current Practice",
#             "exp": "Experimental",
#             "historic": "Historic",
#             "info": "Informational",
#         }
        front = e.find('./front')
        title = e.find('./front/title')
        i = front.index(title) + 1
        if 'category' in e.attrib and 'seriesNo' in e.attrib:
            attr = {
                'name': e.get('category'),
                'value': e.get('seriesNo')
            }
            front.insert(i, self.element('seriesInfo', **attr))
            stripattr(e, ['seriesNo', ]) # keep 'category' for use in preptool
        if 'number' in e.attrib:
            front.insert(i, self.element('seriesInfo', name="RFC", value=e.get('number')))
            if 'docName' in e.attrib:
                e.insert(0, self.element('link', rel='convertedFrom', href="https://datatracker.ietf.org/doc/%s"%(e.get('docName'), )))
        elif 'docName' in e.attrib:
            front.insert(i, self.element('seriesInfo', name="Internet-Draft", value=e.get('docName')))
        stripattr(e, ['docName', 'number', 'xi'])

    # 2.47.  <seriesInfo>
    # 
    #    ...
    #    
    #    This element appears as a child element of <front> (Section 2.26) and
    #    <reference> (Section 2.40; deprecated in this context).
    # 
    # 
    # 2.53.  <t>
    # 
    # 2.53.2.  "hangText" Attribute
    # 
    #    Deprecated.  Instead, use <dd> inside of a definition list (<dl>).
    def element_t(self, e, p):
        if p.tag != 'list':
            stripattr(e, ['hangText', ])
            
    # 
    # 
    # 2.66.  <xref>
    # 
    # 2.66.1.  "format" Attribute
    # 
    #    "none"
    # 
    #       Deprecated.
    # 
    # 1.3.3.  Elements and Attributes Deprecated from v2
    # 
    #    o  Deprecate the "pageno" attribute in <xref> because it was unused
    #       in v2.  Deprecate the "none" values for the "format" attribute in
    #       <xref> because it makes no sense semantically.
    #
    def element_xref(self, e, p):
        if 'format' in e.attrib and e.get('format') == 'none':
            stripattr(e, ['format'])
        stripattr(e, ['pageno'])

    # 2.66.2.  "pageno" Attribute
    # 
    #    Deprecated.
    # 
    # 
    # 3.  Elements from v2 That Have Been Deprecated
    # 
    #    This section lists the elements from v2 that have been deprecated.
    #    Note that some elements in v3 have attributes from v2 that are
    #    deprecated; those are not listed here.
    # 
    # 
    # 3.1.  <c>
    # 
    #    Deprecated.  Instead, use <tr>, <td>, and <th>.
    # 
    #    This element appears as a child element of <texttable> (Section 3.8).
    # 
    # 
    # 3.2.  <facsimile>
    # 
    #    Deprecated.  The <email> element is a much more useful way to get in
    #    touch with authors.
    # 
    #    This element appears as a child element of <address> (Section 2.2).
    def element_facsimile(self, e, p):
            self.replace(e, None)

    # 3.3.  <format>
    # 
    #    Deprecated.  If the goal is to provide a single URI for a reference,
    #    use the "target" attribute in <reference> instead.
    # 
    #    This element appears as a child element of <reference>
    #    (Section 2.40).
    def element_format(self, e, p):
        ptarget = p.get('target')
        ftarget = e.get('target')
        if ptarget:
            if ftarget == ptarget:
                self.replace(e, None, "<format/> element with duplicate target (%s) removed" % ftarget)
            else:
                self.replace(e, None, "Warning: <format/> element with alternative target (%s) removed" % ftarget)
        else:
            p.set('target', ftarget)
            self.replace(e, None, "<format/> element removed, target value (%s) moved to parent" % ftarget)

    # 3.3.1.  "octets" Attribute
    # 
    #    Deprecated.
    # 
    # 3.3.2.  "target" Attribute
    # 
    #    Deprecated.
    # 
    # 3.3.3.  "type" Attribute (Mandatory)
    # 
    #    Deprecated.
    # 
    # 
    # 3.4.  <list>
    # 
    #    Deprecated.  Instead, use <dl> for list/@style "hanging"; <ul> for
    #    list/@style "empty" or "symbols"; and <ol> for list/@style "letters",
    #    "numbers", "counter", or "format".
    # 
    #    This element appears as a child element of <t> (Section 2.53).
    def element_list(self, e, p):
        # convert to dl, ul, or ol
        nstyle = None
        style = e.get('style', '').strip()
        attribs = {}
        comments = []
        if not style:
            # otherwise look for the nearest list parent with a style and use it
            for parent in e.iterancestors():
                if parent.tag == 'list':
                    style = parent.get('style')
                elif parent.tag == 'dl':
                    style = 'hanging'
                elif parent.tag == 'ul':
                    style = 'symbols'
                elif parent.tag == 'ol':
                    nstyle = parent.get('style')
                    if nstyle in ['a', 'A']:
                        style = 'letters'
                    elif nstyle == '1':
                        style = 'numbers'
                if style:
                    break
        if not style:
            style = 'empty'
        #
        if   style == 'empty':
            tag = 'ul'
        elif style == 'symbols':
            tag = 'ul'
        elif style == 'hanging':
            tag = 'dl'
        elif style == 'numbers':
            tag = 'ol'
            attribs['type'] = nstyle if nstyle else '1'
        elif style == 'letters':
            tag = 'ol'
            attribs['type'] = nstyle if nstyle else 'a'
        elif style.startswith('format'):
            tag = 'ol'
            attribs['type'] = style[len('format '):]
        else:
            tag = 'ul'
            comments.append("Warning: unknown list style: '%s'" % style)
        #
        comments.append('Replaced <list style="%s"/> with <%s/>' % (style, tag))
        if 'counter' in e.keys():
            attribs['group'] = e.get('counter')
            comments.append("Converting <list counter=...> to <%s group=...> " % tag)
        #
        attribs['spacing'] = 'compact' if hasattr(e, 'pis') and e.pis['compact'] in ['yes', 'true'] else 'normal'
        #
        stripattr(e, ['counter', 'style', ])
        l = self.element(tag, **attribs)
        self.replace(e, l, comments)
        stripattr(l, ['hangIndent'])
        if tag in ['ol', 'ul']:
            for t in l.findall('./t'):
                self.replace(t, 'li')
        elif tag == 'dl':
            for t in l.findall('./t'):
                dt = self.element('dt')
                dt.text = t.get('hangText')
                if not dt.text is None:
                    del t.attrib['hangText']
                i = l.index(t)
                l.insert(i, dt)
                self.replace(t, 'dd')
        else:
            self.error("Unexpected tag when processing <list/>: '%s'" % tag)

    # 3.4.1.  "counter" Attribute
    # 
    #    Deprecated.  The functionality of this attribute has been replaced
    #    with <ol>/@start.
    # 
    # 3.4.2.  "hangIndent" Attribute
    # 
    #    Deprecated.  Use <dl> instead.
    # 
    # 3.4.3.  "style" Attribute
    # 
    #    Deprecated.
    # 
    # 
    # 3.5.  <postamble>
    # 
    #    Deprecated.  Instead, use a regular paragraph after the figure or
    #    table.
    # 
    #    This element appears as a child element of <figure> (Section 2.25)
    #    and <texttable> (Section 3.8).
    def element_postamble(self, e, p):
        e = self.replace(e, 't')
        self.move_after(e, p)

    # 3.6.  <preamble>
    # 
    #    Deprecated.  Instead, use a regular paragraph before the figure or
    #    table.
    # 
    #    This element appears as a child element of <figure> (Section 2.25)
    #    and <texttable> (Section 3.8).
    def element_preamble(self, e, p):
        e = self.replace(e, 't')
        s = p.getprevious()
        if not s is None:
            self.move_after(e, s)
        else:
            pp = p.getparent()
            i = pp.index(p)
            pp.insert(i, e)             # this relies on there being no surrounding text

    # 1.3.3.  Elements and Attributes Deprecated from v2
    #
    #    o  Deprecate <spanx>; replace it with <strong>, <em>, and <tt>.
    #
    # 3.7.  <spanx>
    # 
    #    Deprecated.
    # 
    #    This element appears as a child element of <annotation>
    #    (Section 2.3), <c> (Section 3.1), <postamble> (Section 3.5),
    #    <preamble> (Section 3.6), and <t> (Section 2.53).
    # 
    # 3.7.1.  "style" Attribute
    # 
    #    Deprecated.  Instead of <spanx style="emph">, use <em>; instead of
    #    <spanx style="strong">, use <strong>; instead of <spanx
    #    style="verb">, use <tt>.
    # 
    # 3.7.2.  "xml:space" Attribute
    # 
    #    Deprecated.
    # 
    #    Allowed values:
    # 
    #    o  "default"
    # 
    #    o  "preserve" (default)
    # 
    def element_spanx(self, e, p):
        style = e.get('style', 'emph')
        tags = {
            'emph':     'em',
            'strong':   'strong',
            'verb':     'tt',
        }
        if style in tags:
            tag = tags[style]
        else:
            self.error("Unexpected style in <spanx/>: '%s'" % style)
        stripattr(e, ['style', '{http://www.w3.org/XML/1998/namespace}space', ])
        self.replace(e, tag, 'Replaced <spanx style="%s"/> with <%s/>' % (style, tag))

    # 1.3.3.  Elements and Attributes Deprecated from v2
    # 
    #    o  Deprecate <texttable>, <ttcol>, and <c>; replace them with the new
    #       table elements (<table> and the elements that can be contained
    #       within it).
    # 
    # 3.8.  <texttable>
    # 
    #    Deprecated.  Use <table> instead.
    # 
    #    This element appears as a child element of <aside> (Section 2.6) and
    #    <section> (Section 2.46).
    #
    # 3.8.1.  "align" Attribute
    # 
    #    Deprecated.
    # 
    # 3.8.2.  "anchor" Attribute
    # 
    #    Deprecated.
    # 
    # 3.8.3.  "style" Attribute
    # 
    #    Deprecated.
    # 
    # 3.8.4.  "suppress-title" Attribute
    # 
    #    Deprecated.
    def element_texttable(self, e, p):
        # The tree has been verified to follow the schema on parsing, so we
        # assume that elements occur in the right order here:
        colcount = 0
        cellcount = 0
        thead = None
        tbody = None
        tr = None
        align = []
        table = self.element('table')
        copyattr(e, table)
        for x in e.iterchildren():
            if   x.tag == 'preamble':
                # will be handled separately
                pass
            elif x.tag == 'ttcol':
                if colcount == 0:
                    thead = self.element('thead')
                    table.append(thead)
                    tr = self.element('tr')
                    thead.append(tr)
                align.append(x.get('align', None))
                th = self.copy(x, 'th')
                stripattr(th, ['width'])
                tr.append(th)
                colcount += 1
            elif x.tag == 'c':
                col = cellcount % colcount
                if cellcount == 0:
                    tbody = self.element('tbody')
                    table.append(tbody)
                if col == 0:
                    tr = self.element('tr')
                    tbody.append(tr)
                td = self.copy(x, 'td')
                if align[col]:
                    td.set('align', align[col])
                tr.append(td)
                stripattr(td, ['width'])
                cellcount += 1
            elif x.tag == 'postamble':
                # will be handled separately
                pass
        stripattr(table, ['align', 'style', 'suppress-title',])
        p.replace(e, table)


    # 
    # 
    # 
    # 3.9.  <ttcol>
    # 
    #    Deprecated.  Instead, use <tr>, <td>, and <th>.
    # 
    #    This element appears as a child element of <texttable> (Section 3.8).
    # 
    # 3.9.1.  "align" Attribute
    # 
    #    Deprecated.
    # 
    #    Allowed values:
    # 
    #    o  "left" (default)
    # 
    #    o  "center"
    # 
    #    o  "right"
    # 
    # 3.9.2.  "width" Attribute
    # 
    #    Deprecated.
    def element_ttcol(self, e, p):
        # handled in element_texttable()
        pass


    # 3.10.  <vspace>
    # 
    #    Deprecated.  In earlier versions of this format, <vspace> was often
    #    used to get an extra blank line in a list element; in the v3
    #    vocabulary, that can be done instead by using multiple <t> elements
    #    inside the <li> element.  Other uses have no direct replacement.
    # 
    #    This element appears as a child element of <t> (Section 2.53).
    # 
    #    Content model: this element does not have any contents.
    def element_vspace(self, e, p):
        t = p
        if t.tag != 't':
            #bare text inside other element -- wrap in t first
            t = self.wrap_content(t)
        l = t.getparent()
        if l.tag in ['dd', 'li', ]:
            i = l.index(t) + 1
            t2 = self.element('t')
            if e.tail and e.tail.strip():
                t2.text = e.tail
            for s in e.itersiblings():
                t2.append(s)
            t.remove(e)
            l.insert(i, t2)
            if self.options.verbose:
                c = Comment(" v2v3: <vspace/> inside list converted to sequence of <t/> ")
                t.insert(i, c)
            if isempty(t):
                l.remove(t)
        else:
            self.replace(e, None, "<vspace/> deprecated and removed")

    # 3.10.1.  "blankLines" Attribute
    # 
    #    Deprecated.
    # 
    # 
    # A.3.  The "consensus" Attribute
    # 
    #    The consensus attribute can be used to supply this information.  The
    #    acceptable values are "true" (the default) and "false"; "yes" and
    #    "no" from v2 are deprecated.
    # 

    # v3 is stricter than v2 on where only IDREF is permitted.  Fix this
    def attribute_anchor(self, e, p):
        k = 'anchor'
        if k in e.keys():
            v = e.get(k)
            id = idref(v.strip())
            if id != v:
                e.set(k, id)
                

    def attribute_xref_target(self, e, p):
        k = 'target'
        if k in e.keys():
            v = e.get(k)
            id = idref(v.strip())
            if id != v:
                e.set(k, id)

    def attribute_yes_no(self, e, p):
        for k,v in e.attrib.items():
            if   v == 'yes':
                e.set(k, 'true')
            elif v == 'no':
                e.set(k, 'false')
