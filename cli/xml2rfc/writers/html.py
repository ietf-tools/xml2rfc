# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import datetime
import i18naddress
import lxml
import os
import re
#import sys
import six
import unicodedata
import xml2rfc

from io import open
from lxml.html import html_parser
from lxml.html.builder import ElementMaker

if six.PY2:
    from urllib import urlopen
elif six.PY3:
    from urllib.request import urlopen

try:
    import debug
    debug.debug = True
except ImportError:
    pass

from xml2rfc import log, strings
from xml2rfc.writers.base import default_options, BaseV3Writer
from xml2rfc.uniscripts import is_script
from xml2rfc.util.date import extract_date, format_date, format_date_iso, get_expiry_date
from xml2rfc.util.name import ( full_author_name_expansion, short_author_role,
                                ref_author_name_first, ref_author_name_last, 
                                short_author_name_set, full_author_name_set,
                                short_org_name_set, full_org_name, )
from xml2rfc.util.postal import ( get_normalized_address_info, address_hcard_properties,
                                enhance_address_format, address_field_mapping, )
from xml2rfc.util.unicode import expand_unicode_element
from xml2rfc.utils import namespaces, is_htmlblock, find_duplicate_html_ids, build_dataurl

#from xml2rfc import utils

# ------------------------------------------------------------------------------

seen = set()

def wrap(h, tag, **kwargs):
    w = build(tag, **kwargs)
    w.append(h)
    return w

def slugify(s):
    s = s.strip().lower()
    s = re.sub(r'[^\w\s/|-]', '', s)
    s = re.sub(r'[-_\s/|]+', '-', s)
    s = s.strip('-')
    return s

def maybefloat(f):
    try:
        return float(f)
    except (ValueError, TypeError):
        return None

def wrap_ascii(tag, conj, name, ascii, role='', classes=None):
    role = ('','') if role in ['',None] else (', ', role)
    if ascii:
        e = build(tag,
                build.span(conj, name, classes='non-ascii'),
                ' (',
                build.span(ascii, classes='ascii'),
                ')',
                *role,
                classes=classes
            )
    else:
        e = build(tag, conj, name, *role, classes=classes)
    return e

#def wrap_ascii_div(


class ClassElementMaker(ElementMaker):

    def __call__(self, tag, *children, **attrib):
        classes = attrib.pop('classes', None)
        attrib = dict( (k,v) for k,v in attrib.items() if v != None)
        elem = super(ClassElementMaker, self).__call__(tag, *children, **attrib)
        if classes:
            elem.set('class', classes)
        if is_htmlblock(elem) and (elem.tail is None or elem.tail.strip() == ''):
            elem.tail = '\n'
        return elem
build = ClassElementMaker(makeelement=html_parser.makeelement)

class ExtendingElementMaker(ClassElementMaker):

    def __call__(self, tag, parent, precursor, *children, **attrib):
        elem = super(ExtendingElementMaker, self).__call__(tag, *children, **attrib)
        is_block = is_htmlblock(elem)
        #
        child = elem
        if precursor != None:
            pn = precursor.get('pn')
            sn = precursor.get('slugifiedName')
            an = precursor.get('anchor')
            if   pn != None:
                elem.set('id', pn)
                if an != None and is_block:
                    child = wrap(elem, 'div', id=an)
            elif sn != None:
                elem.set('id', sn)
            elif an != None:
                elem.set('id', an)
            if not elem.text or elem.text.strip() == '':
                elem.text = precursor.text
            elem.tail = precursor.tail
        if parent != None:
            parent.append(child)
        if is_block and (elem.tail is None or elem.tail.strip() == ''):
            elem.tail = '\n'
        if is_block and child != elem and (child.tail is None or child.tail.strip() == ''):
            child.tail = '\n'
        return elem
add  = ExtendingElementMaker(makeelement=html_parser.makeelement)


pilcrow = '\u00b6'
mdash   = '\u2014'

# ------------------------------------------------------------------------------
# Address formatting functions, based on i18naddress functions, but rewritten to
# produce html entities, rather than text lines.

def _format_address_line(line_format, address, rules):
    def _get_field(name):
        field = []
        values = address.get(name, '')
        if isinstance(values, list):
            values = [ v for v in values if v ]
        if values:
            if isinstance(values, list):
                for value in values[:-1]:
                    field.append(build.div(value, classes=address_hcard_properties[name]))
                field.append(build.span(values[-1], classes=address_hcard_properties[name]))
            else:
                span = None
                if name == 'name':
                    role = address.get('role', '')
                    if role:
                        span = build.span(values,
                            ' (',
                            build.span(role, classes='role'),
                            ')',
                            classes=address_hcard_properties[name])
                if span == None:
                    span = build.span(values, classes=address_hcard_properties[name])
                field.append(span)
        return field

    replacements = {
        '%%%s' % code: _get_field(field_name)
        for code, field_name in address_field_mapping.items()}

    field_entries = re.split('(%.)', line_format)
    fields = [ f for n in field_entries for f in replacements.get(n, n) ]
    return fields

def format_address(address, latin=False):
    rules = i18naddress.get_validation_rules(address)
    address_format = (
        rules.address_latin_format if latin else rules.address_format)
    address_format = enhance_address_format(address, address_format)
    address_line_formats = address_format.split('%n')
    address_lines = [
        build.div(*_format_address_line(lf, address, rules), dir='auto')
        for lf in address_line_formats]
    address_lines = filter(lambda n: n!=None and ''.join(list(n.itertext())), address_lines)
    return address_lines

def get_bidi_alignment(address):
    # We don't attempt to control the bidi layout in detail, but leave that to
    #the html layout engine; but want to know whether we have Right-to-left content
    #in order to set the overall alignment of the address block.
    for field in address:
        line = address[field]
        if line:
            for ch in line:
                if isinstance(ch, six.text_type):
                    dir = unicodedata.bidirectional(ch)
                    if dir in ['R', 'AL']:
                        return 'right'
    return 'left'
    
# ------------------------------------------------------------------------------

class HtmlWriter(BaseV3Writer):

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today()):
        super(HtmlWriter, self).__init__(xmlrfc, quiet=quiet, options=options, date=date)
        self.anchor_tags = self.get_tags_with_anchor()
        self.duplicate_html_ids = set()

    def get_tags_with_anchor(self):
        anchor_nodes = self.schema.xpath("//x:define/x:element//x:attribute[@name='anchor']", namespaces=namespaces)
        element_nodes = set()
        for a in anchor_nodes:
            for e in a.iterancestors():
                if e.tag.endswith('element'):
                    element_nodes.add(e.get('name'))
                    break
        return element_nodes

    def html_tree(self):
        if not self.root.get('prepTime'):
            prep = xml2rfc.PrepToolWriter(self.xmlrfc, options=self.options, date=self.options.date, liberal=True, keep_pis=[xml2rfc.V3_PI_TARGET])
            tree = prep.prep()
            self.tree = tree
            self.root = self.tree.getroot()
        html_tree = self.render(None, self.root)
        html_tree = self.post_process(html_tree)
        return html_tree

    def html(self, html_tree=None):
        if html_tree is None:
            html_tree = self.html_tree()
        # 6.1.  DOCTYPE
        # 
        #    The DOCTYPE of the document is "html", which declares that the
        #    document is compliant with HTML5.  The document will start with
        #    exactly this string:
        # 
        #    <!DOCTYPE html>
        html = lxml.etree.tostring(html_tree, method='html', encoding='unicode', pretty_print=True, doctype="<!DOCTYPE html>")
        html = re.sub(r'[\x00-\x09\x0B-\x1F]+', ' ', html)
        return html

    def write(self, filename):
        self.filename = filename

        """Write the document to a file """
        html_tree = self.html_tree()

        # Check for duplicate IDs
        dups = set(find_duplicate_html_ids(html_tree)) - self.duplicate_html_ids
        for attr, id, e in dups:
            self.warn(self.root[-1], 'Duplicate %s="%s" found in generated HTML.' % (attr, id, ))

        if self.errors:
            log.write("Not creating output file due to errors (see above)")
            return

        # Use lxml's built-in serialization
        with open(filename, 'w', encoding='utf-8') as file:
            text = self.html(html_tree)
            file.write(text)

        if not self.options.quiet:
            log.write('Created file', filename)


    def render(self, h, x):
        res = None
        if x.tag in (lxml.etree.PI, lxml.etree.Comment):
            tail = x.tail if x.tail and x.tail.strip() else ''
            if len(h):
                last = h[-1]
                last.tail = (last.tail or '') + tail
            else:
                h.text = (h.text or '') + tail
        else:
            func_name = "render_%s" % (x.tag.lower(),)
            func = getattr(self, func_name, None)
            if func == None:
                func = self.default_renderer
                if x.tag in self.__class__.deprecated_element_tags:
                    self.warn(x, "Was asked to render a deprecated element: <%s>", (x.tag, ))
                elif not x.tag in seen:
                    self.warn(x, "No renderer for <%s> found" % (x.tag, ))
                    seen.add(x.tag)
            res = func(h, x)
        return res


    def default_renderer(self, h, x):
        hh = add(x.tag, h, x)
        for c in x.getchildren():
            self.render(hh, c)
        return hh

    def skip_renderer(self, h, x):
        part = self.part
        for c in x.getchildren():
            self.part = part
            self.render(h, c)

    def address_line_renderer(self, h, x, classes=None):
        if x.text:
            div = build.div(build.span(x.text.strip(), classes=classes))
            h.append(div)
        else:
            div = None
        return div

    def inline_text_renderer(self, h, x):
        h.text = x.text
        for c in x.getchildren():
            self.render(h, c)
        h.tail = x.tail

    def null_renderer(self, h, x):
        return None

    def maybe_add_pilcrow(self, e):
        if len(e.xpath('.//*[@class="pilcrow"]')) == 0:
            id = e.get('id')
            if id:
                add.a(e, None, pilcrow, classes='pilcrow', href='#%s'%id)
            else:
                self.warn(e, 'Tried to add a pilcrow to <%s>, but found no "id" attribute' % e.tag)

    # --- element rendering functions ------------------------------------------

    def render_rfc(self, h, x):
        self.part = x.tag
    # 6.2.  Root Element
    # 
    #    The root element of the document is <html>.  This element includes a
    #    "lang" attribute, whose value is a language tag, as discussed in
    #    [RFC5646], that describes the natural language of the document.  The
    #    language tag to be included is "en".  The class of the <html> element
    #    will be copied verbatim from the XML <rfc> element's <front>
    #    element's <seriesInfo> element's "name" attributes (separated by
    #    spaces; see Section 2.47.3 of [RFC7991]), allowing CSS to style RFCs
    #    and Internet-Drafts differently from one another (if needed):
    # 
    #    <html lang="en" class="RFC">

        classes = ' '.join( i.get('name') for i in x.xpath('./front/seriesInfo') )
        #
        html = h if h != None else build.html(classes=classes, lang='en')
        self.html_root = html

    # 6.3.  <head> Element
    # 
    #    The root <html> will contain a <head> element that contains the
    #    following elements, as needed.

        head = add.head(html, None)

    # 6.3.1.  Charset Declaration
    # 
    #    In order to be correctly processed by browsers that load the HTML
    #    using a mechanism that does not provide a valid content-type or
    #    charset (such as from a local file system using a "file:" URL), the
    #    HTML <head> element contains a <meta> element, whose "charset"
    #    attribute value is "utf-8":
    # 
    #    <meta charset="utf-8">

        add.meta(head, None, charset='utf-8')
        add.meta(head, None, name="scripts", content=x.get('scripts'))

    # 6.3.2.  Document Title
    # 
    #    The contents of the <title> element from the XML source will be
    #    placed inside an HTML <title> element in the header.

        title = x.find('./front/title')
        text = title.text
        if self.options.rfc:
            text = ("RFC %s: " % self.root.get('number')) + text
        add.title(head, None, text)

    # 6.3.3.  Document Metadata
    # 
    #    The following <meta> elements will be included:
    # 
    #    o  author - one each for the each of the "fullname"s and
    #       "asciiFullname"s of all of the <author>s from the <front> of the
    #       XML source
        for a in x.xpath('./front/author'):
            if not a.get('role') == 'contributor':
                name = full_author_name_expansion(a) or full_org_name(a)
                add.meta(head, None, name='author', content=name )

    #    o  description - the <abstract> from the XML source

        abstract = x.find('./front/abstract')
        if abstract != None:
            abstract_text = ' '.join(abstract.itertext())
            add.meta(head, None, name='description', content=abstract_text)

    #    o  generator - the name and version number of the software used to
    #       create the HTML

        generator = "%s %s" % (xml2rfc.NAME, xml2rfc.__version__)
        add.meta(head, None, name='generator', content=generator)
        
    #    o  keywords - comma-separated <keyword>s from the XML source

        for keyword in x.xpath('./front/keyword'):
            add.meta(head, None, name='keyword', content=keyword.text)

    #    For example:
    # 
    #    <meta name="author" content="Joe Hildebrand">
    #    <meta name="author" content="JOE HILDEBRAND">
    #    <meta name="author" content="Heather Flanagan">
    #    <meta name="description" content="This document defines...">
    #    <meta name="generator" content="xmljade v0.2.4">
    #    <meta name="keywords" content="html,css,rfc">
    # 
    #    Note: the HTML <meta> tag does not contain a closing slash.
    # 
    # 6.3.4.  Link to XML Source
    # 
    #    The <head> element contains a <link> tag, with "rel" attribute of
    #    "alternate", "type" attribute of "application/rfc+xml", and "href"
    #    attribute pointing to the prepared XML source that was used to
    #    generate this document.
    # 
    #    <link rel="alternate" type="application/rfc+xml" href="source.xml">

        add.link(head, None, rel='alternate', type='application/rfc+xml', href=self.xmlrfc.source)

    # 6.3.5.  Link to License
    # 
    #    The <head> element contains a <link> tag, with "rel" attribute of
    #    "license" and "href" attribute pointing to the an appropriate
    #    copyright license for the document.
    # 
    #    <link rel="license"
    #       href="https://trustee.ietf.org/trust-legal-provisions.html">

        add.link(head, None, rel='license', href="#copyright")

    # 6.3.6.  Style
    # 
    #    The <head> element contains an embedded CSS in a <style> element.
    #    The styles in the style sheet are to be set consistently between
    #    documents by the RFC Editor, according to the best practices of the
    #    day.
    # 
    #    To ensure consistent formatting, individual style attributes should
    #    not be used in the main portion of the document.
    # 
    #    Different readers of a specification will desire different formatting
    #    when reading the HTML versions of RFCs.  To facilitate this, the
    #    <head> element also includes a <link> to a style sheet in the same
    #    directory as the HTML file, named "rfc-local.css".  Any formatting in
    #    the linked style sheet will override the formatting in the included
    #    style sheet.  For example:
    # 
    #    <style>
    #      body {}
    #      ...
    #    </style>
    #    <link rel="stylesheet" type="text/css" href="rfc-local.css">

        cssin  = self.options.css or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'xml2rfc.css')
        with open(cssin, encoding='utf-8') as f:
            css = f.read()

        if self.options.external_css:
            cssout = os.path.join(os.path.dirname(self.filename), 'xml2rfc.css')
            with open(cssout, 'w', encoding='utf-8') as f:
                f.write(css)
            add.link(head, None, rel="stylesheet", href="xml2rfc.css", type="text/css")
        elif self.options.no_css:
            pass
        else:
            add.style(head, None, css, type="text/css")
        add.link(head, None, rel="stylesheet", href="rfc-local.css", type="text/css")

    # 6.3.7.  Links
    # 
    #    Each <link> element from the XML source is copied into the HTML
    #    header.  Note: the HTML <link> element does not include a closing
    #    slash.

        for link in x.xpath('./link'):
            head.append(link)

        body = add.body(html, None)

    # 6.4.  Page Headers and Footers
    # 
    #    In order to simplify printing by HTML renderers that implement
    #    [W3C.WD-css3-page-20130314], a hidden HTML <table> tag of class
    #    "ears" is added at the beginning of the HTML <body> tag, containing
    #    HTML <thead> and <tfoot> tags, each of which contains an HTML <tr>
    #    tag, which contains three HTML <td> tags with class "left", "center",
    #    and "right", respectively.
    # 
    #    The <thead> corresponds to the top of the page, the <tfoot> to the
    #    bottom.  The string "[Page]" can be used as a placeholder for the
    #    page number.  In practice, this must always be in the <tfoot>'s right
    #    <td>, and no control of the formatting of the page number is implied.
    #
    #    <table class="ears">
    #      <thead>
    #        <tr>
    #          <td class="left">Internet-Draft</td>
    #          <td class="center">HTML RFC</td>
    #          <td class="right">March 2016</td>
    #        </tr>
    #      </thead>
    #      <tfoot>
    #        <tr>
    #          <td class="left">Hildebrand</td>
    #          <td class="center">Expires September 2, 2016</td>
    #          <td class="right">[Page]</td>
    #        </tr>
    #      </tfoot>
    #    </table>

        body.append(
            build.table(
                build.thead(
                    build.tr(
                        build.td(self.page_top_left(), classes='left'),
                        build.td(self.page_top_center(), classes='center'),
                        build.td(self.page_top_right(), classes='right'),
                    ),
                ),
                build.tfoot(
                    build.tr(
                        build.td(self.page_bottom_left(), classes='left'),
                        build.td(self.page_bottom_center(), classes='center'),
                        build.td("[Page]", classes='right'),
                    ),
                ),
                classes='ears',
            )
        )

        for c in [ e for e in [ x.find('front'), x.find('middle'), x.find('back') ] if e != None]:
            self.part = c.tag
            self.render(body, c)

        jsin  = self.options.css or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'xml2rfc.js')
        with open(jsin, encoding='utf-8') as f:
            js = f.read()
        add.script(body, None, js)

        return html

    # 9.1.  <abstract>
    # 
    #    The abstract is rendered in a similar fashion to a <section> with
    #    anchor="abstract" and <name>Abstract</name>, but without a section
    #    number.
    # 
    #    <section id="abstract">
    #      <h2><a href="#abstract" class="selfRef">Abstract</a></h2>
    #      <p id="s-abstract-1">This document defines...
    #        <a href="#s-abstract-1" class="pilcrow">&para;</a>
    #      </p>
    #    </section>
    # 

    def render_abstract(self, h, x):
        if self.part == 'front':
            section = add.section(h, x)
            section.append( build.h2( build.a('Abstract', classes='selfRef', href="#abstract"), id="abstract"))
            for c in x.getchildren():
                self.render(section, c)
            return section
        else:
            return None

    # 9.2.  <address>
    # 
    #    This element is used in the Authors' Addresses section.  It is
    #    rendered as an HTML <address> tag of class "vcard".  If none of the
    #    descendant XML elements has an "ascii" attribute, the <address> HTML
    #    tag includes the HTML rendering of each of the descendant XML
    #    elements.  Otherwise, the <address> HTML tag includes an HTML <div>
    #    tag of class "ascii" (containing the HTML rendering of the ASCII
    #    variants of each of the descendant XML elements), an HTML <div> tag
    #    of class "alternative-contact", (containing the text "Alternate
    #    contact information:"), and an HTML <div> tag of class "non-ascii"
    #    (containing the HTML rendering of the non-ASCII variants of each of
    #    the descendant XML elements).
    # 
    #    Note: the following example shows some ASCII equivalents that are the
    #    same as their nominal equivalents for clarity; normally, the ASCII
    #    equivalents would not be included for these cases.
    # 
    #    <address class="vcard">
    #      <div class="ascii">
    #        <div class="nameRole"><span class="fn">Joe Hildebrand</span>
    #          (<span class="role">editor</span>)</div>
    #        <div class="org">Cisco Systems, Inc.</div>
    #      </div>
    #      <div class="alternative-contact">
    #        Alternate contact information:
    #      </div>
    #      <div class="non-ascii">
    #        <div class="nameRole"><span class="fn">Joe Hildebrand</span>
    #          (<span class="role">editor</span>)</div>
    #        <div class="org">Cisco Systems, Inc.</div>
    #      </div>
    #    </address>

    ## The above text is reasonable for author name and org, but nonsense for
    ## the <address> element.  The following text will be used:
    ##
    ## The <address> element will be rendered as a sequence of <div> elements,
    ## each corresponding to a child element of <address>.  Element classes
    ## will be taken from hcard, as specified on http://microformats.org/wiki/hcard
    ## 
    ##   <address class="vcard">
    ##
    ##     <!-- ... name, role, and organization elements ... -->
    ##
    ##      <div class="adr">
    ##        <div class="street-address">1 Main Street</div>
    ##        <div class="street-address">Suite 1</div>
    ##        <div class="city-region-code">
    ##          <span class="city">Denver</span>,&nbsp;
    ##          <span class="region">CO</span>&nbsp;
    ##          <span class="postal-code">80202</span>
    ##        </div>
    ##        <div class="country-name">USA</div>
    ##      </div>
    ##      <div class="tel">
    ##        <span>Phone:</span>
    ##        <a class="tel" href="tel:+1-720-555-1212">+1-720-555-1212</a>
    ##      </div>
    ##      <div class="fax">
    ##        <span>Fax:</span>
    ##        <span class="tel">+1-303-555-1212</span>
    ##      </div>
    ##      <div class="email">
    ##        <span>Email:</span>
    ##        <a class="email" href="mailto:author@example.com">author@example.com</a>
    ##      </div>
    ##    </address>
    render_address = skip_renderer

    # 9.3.  <annotation>
    # 
    #    This element is rendered as the text ", " (a comma and a space)
    #    followed by a <span> of class "annotation" at the end of a
    #    <reference> element, the <span> containing appropriately transformed
    #    elements from the children of the <annotation> tag.
    # 
    #     <span class="annotation">Some <em>thing</em>.</span>
    def render_annotation(self, h, x):
        span = add.span(h, x, classes='annotation')
        for c in x.getchildren():
            self.render(span, c)
        return span

    # 9.4.  <area>
    # 
    #    Not currently rendered to HTML.
    # 

    def render_artset(self, h, x):
        preflist = ['svg', 'binary-art', 'ascii-art', ]
        for t in preflist:
            for a in x.xpath('./artwork[@type="%s"]' % t):
                artwork = self.render(h, a)
                return artwork
        else:
            artwork = self.render(h, x[0])
        return artwork

    # 9.5.  <artwork>
    # 
    #    Artwork can consist of either inline text or SVG.  If the artwork is
    #    not inside a <figure> element, a pilcrow (Section 5.2) is included.
    #    Inside a <figure> element, the figure title serves the purpose of the
    #    pilcrow.  If the "align" attribute has the value "right", the CSS
    #    class "alignRight" will be added.  If the "align" attribute has the
    #    value "center", the CSS class "alignCenter" will be added.
    def render_artwork(self, h, x):
        type = x.get('type')
        align = x.get('align', 'left')

    # 9.5.1.  Text Artwork
    # 
    #    Text artwork is rendered inside an HTML <pre> element, which is
    #    contained by a <div> element for consistency with SVG artwork.  Note
    #    that CDATA blocks are not a part of HTML, so angle brackets and
    #    ampersands (i.e., <, >, and &) must be escaped as &lt;, &gt;, and
    #    &amp;, respectively.
    # 
    #    The <div> element will have CSS classes of "artwork", "art-text", and
    #    "art-" prepended to the value of the <artwork> element's "type"
    #    attribute, if it exists.
    # 
    #    <div class="artwork art-text art-ascii-art"  id="s-1-2">
    #      <pre>
    #     ______________
    #    &lt; hello, world &gt;
    #     --------------
    #      \   ^__^
    #       \  (oo)\_______
    #          (__)\       )\/\
    #              ||----w |
    #              ||     ||
    #      </pre>
    #      <a class="pilcrow" href="#s-1-2">&para;</a>
    #    </div>
        if type not in ['svg', 'binary-art', ]:
            if not x.text or not x.text.strip():
                self.err(x, 'Expected ascii-art artwork for <artwork type="%s">, but found %s...' % (x.get('type',''), lxml.etree.tostring(x)[:128]))
                return None
            else:
                pre = build.pre(x.text.expandtabs())
                classes = 'artwork art-text align%s' % align.capitalize()
                if type and type != 'text':
                    classes += ' art-%s' % type
                div = add.div(h, x, pre, classes=classes)
                div.text = None
                if x.getparent().tag != 'figure':
                    self.maybe_add_pilcrow(div)
                return div
            
    # 9.5.2.  SVG Artwork
    # 
    #    SVG artwork will be included inline.  The SVG is wrapped in a <div>
    #    element with CSS classes "artwork" and "art-svg".
    # 
    #    If the SVG "artwork" element is a child of <figure> and the artwork
    #    is specified as align="right", an empty HTML <span> element is added
    #    directly after the <svg> element, in order to get right alignment to
    #    work correctly in HTML rendering engines that do not support the
    #    flex-box model.
    # 
    #    Note: the "alt" attribute of <artwork> is not currently used for SVG;
    #    instead, the <title> and <desc> tags are used in the SVG.
    # 
    #    <div class="artwork art-svg" id="s-2-17">
    #      <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    #        <desc>Alt text here</desc>
    #        <circle
    #          cx="50" cy="50" r="40"
    #          stroke="green" stroke-width="4" fill="yellow" />
    #      </svg>
    #      <a href="#s-2-17" class="pilcrow">&para;</a>
    #    </div>
        elif type == 'svg':
            classes = 'artwork art-svg align%s' % align.capitalize()
            div = add.div(h, x, classes=classes)
            div.text = None
            src = x.get('src')
            if src:
                svgfile = x.get('originalSrc') or x.get('src')[:37]+' ...'
                if not src.startswith('data:'):
                    self.err(x, "Internal error: Got an <artwork> src: attribute that did not start with 'data:' after prepping")
                try:
                    f = urlopen(src)
                    data = f.read()
                    svg = lxml.etree.fromstring(data)
                except IOError as e:
                    self.err(x, str(e))
                    svg = None
            else:
                svg = x.find('svg:svg', namespaces=namespaces)
                svgfile = "inline:%s ..." % lxml.etree.tostring(svg)[:31]
            if svg == None:
                self.err(x, 'Expected <svg> content inside <artwork type="svg">, but did not find it:\n   %s ...' % (lxml.etree.tostring(x)[:256], ))
                return None
            # For w3.org validator compatibility
            if svg.get('attribute', None):
                del svg.attrib['version']
            #
            # Deal with possible svg scaling issues.
            vbox = svg.get('viewBox')
            svgw = maybefloat(svg.get('width'))
            svgh = maybefloat(svg.get('height'))
            try:
                if vbox:
                    if not (svgw and svgh):
                        xo,yo,w,h = re.split(',? +', vbox.strip('()'))
                        svgw = float(w)-float(xo)
                        svgh = float(h)-float(yo)
                else:
                    if svgw and svgh:
                        svg.set('viewBox', '0 0 %s %s' % (svgw, svgh))
                    else:
                        self.err(x, "Cannot place SVG properly when neither viewBox nor width and height is available") 
                        return None
            except ValueError as e:
                self.err(x, "Error when calculating SVG size: %s" % e)
            imgw = 660 if self.options.image_svg else 724
            if imgw < svgw:
                svg.set('width', str(svgw/svgw*imgw))
                svg.set('height', str(svgh/svgw*imgw))
            #
            if self.options.image_svg:
                data = build_dataurl('image/svg+xml', lxml.etree.tostring(svg))
                add.img(div, None, src=data, alt=x.get('alt'))
            else:
                div.append(svg)
            if x.getparent().tag != 'figure':
                self.maybe_add_pilcrow(div)
            else:
                if x.get('align') == 'right':
                    add.span(div, None)
            #
            dups = set(find_duplicate_html_ids(self.html_root))
            new  = dups - self.duplicate_html_ids
            for attr, id, e in new:
                self.warn(x, 'Duplicate attribute %s="%s" found after including svg from %s.  This can cause problems with some browsers.' % (attr, id, svgfile))
            self.duplicate_html_ids = self.duplicate_html_ids | dups

    # 9.5.3.  Other Artwork
    # 
    #    Other artwork will have a "src" attribute that uses the "data" URI
    #    scheme defined in [RFC2397].  Such artwork is rendered in an HTML
    #    <img> element.  Note: the HTML <img> element does not have a closing
    #    slash.
    # 
    #    Note: such images are not yet allowed in RFCs even though the format
    #    supports them.  A limited set of "data:" mediatypes for artwork may
    #    be allowed in the future.
    # 
    #    <div class="artwork art-logo" id="s-2-58">
    #      <img alt="IETF logo"
    #           src="data:image/gif;charset=utf-8;base64,...">
    #      <a class="pilcrow" href="#s-2-58">&para;</a>
    #    </div>
        elif type == 'binary-art':
            div = add.div(h, x, classes='artwork art-svg')
            data = x.get('src')
            if data:
                del div.attrib['src']
                add.img(div, None, src=data)
            else:
                self.err(x, 'Expected <img> data given by src="" for <artwork type="binary-art">, but did not find it: %s ...' % (lxml.etree.tostring(x)[:128], ))
            if x.getparent().tag != 'figure':
                self.maybe_add_pilcrow(div)

    # 9.6.  <aside>
    # 
    #    This element is rendered as an HTML <aside> element, with all child
    #    content appropriately transformed.
    # 
    #    <aside id="s-2.1-2">
    #      <p id="s-2.1-2.1">
    #        A little more than kin, and less than kind.
    #        <a class="pilcrow" href="#s-2.1-2.1">&para;</a>
    #      </p>
    #    </aside>
    render_aside = default_renderer
        

    # 
    # 9.7.  <author>
    # 
    #    The <author> element is used in several places in the output.
    #    Different rendering is used for each.
    def render_author(self, h, x):
        if len(x)==0 and len(x.attrib)==0:
            return None

    # 9.7.1.  Authors in Document Information
    # 
    #    As seen in the Document Information at the beginning of the HTML,
    #    each document author is rendered as an HTML <div> tag of class
    #    "author".
    # 
    #    Inside the <div class="author"> HTML tag, the author's initials and
    #    surname (or the fullname, if it exists and the others do not) will be
    #    rendered in an HTML <div> tag of class "author-name".  If the
    #    <author> contains "asciiInitials" and "asciiSurname" attributes, or
    #    contains as "asciiFullname" attribute, the author's name is rendered
    #    twice, with the first being the non-ASCII version, wrapped in an HTML
    #    <span> tag of class "non-ascii", followed by the ASCII version
    #    wrapped in an HTML <span> tag of class "ascii", wrapped in
    #    parentheses.  If the <author> has a "role" attribute of "editor", the
    #    <div class="author-name"> will also contain the text ", " (comma,
    #    space), followed by an HTML <span> tag of class "editor", which
    #    contains the text "Ed.".
    # 
    #    If the <author> element contains an <organization> element, it is
    #    also rendered inside the <div class="author"> HTML tag.
    # 
    #    <div class="author">
    #      <div class="author-name">
    #        H. Flanagan,
    #        <span class="editor">Ed.</span></div>
    #      <div class="org">Test Org</div>
    #    </div>
    #    <div class="author">
    #      <div class="author-name">
    #        <span class="non-ascii">Hildebrand</span>
    #        (<span class="ascii">HILDEBRAND</span>)
    #      </div>
    #      <div class="org">
    #        <span class="non-ascii">Test Org</span>
    #        (<span class="ascii">TEST ORG</span>)
    #      </div>
    #    </div>
        if   self.part == 'front':
            name, ascii = short_author_name_set(x)
            role = short_author_role(x)
            div = add.div(h, x, classes='author')
            if role:
                role = build.span(role, classes=x.get('role'))
            if name:
                div.append(wrap_ascii('div', '', name, ascii, role, classes='author-name'))
            o = x.find('organization')
            if o != None and o.get('showOnFrontPage') == 'true':
                org, ascii  = short_org_name_set(x)
                if org:
                    div.append(wrap_ascii('div', '', org, ascii, None, classes='org'))
            return div

    # 9.7.2.  Authors of This Document
    # 
    #    As seen in the Authors' Addresses section, at the end of the HTML,
    #    each document author is rendered into an HTML <address> element with
    #    the CSS class "vcard".
    # 
    #    The HTML <address> element will contain an HTML <div> with CSS class
    #    "nameRole".  That div will contain an HTML <span> element with CSS
    #    class "fn" containing the value of the "fullname" attribute of the
    #    <author> XML element and an HTML <span> element with CSS class "role"
    #    containing the value of the "role" attribute of the <author> XML
    #    element (if there is a role).  Parentheses will surround the <span
    #    class="role">, if it exists.
    # 
    #    <address class="vcard">
    #      <div class="nameRole">
    #        <span class="fn">Joe Hildebrand</span>
    #        (<span class="role">editor</span>)
    #      </div>
    #      ...
    # 
    #    After the name, the <organization> and <address> child elements of
    #    the author are rendered inside the HTML <address> tag.
    # 
    #    When the <author> element, or any of its descendant elements, has any
    #    attribute that starts with "ascii", all of the author information is
    #    displayed twice.  The first version is wrapped in an HTML <div> tag
    #    with class "ascii"; this version prefers the ASCII version of
    #    information, such as "asciiFullname", but falls back on the non-ASCII
    #    version if the ASCII version doesn't exist.  The second version is
    #    wrapped in an HTML <div> tag with class "non-ascii"; this version
    #    prefers the non-ASCII version of information, such as "fullname", but
    #    falls back on the ASCII version if the non-ASCII version does not
    #    exist.  Between these two HTML <div>s, a third <div> is inserted,
    #    with class "alternative-contact", containing the text "Alternate
    #    contact information:".
    # 
    #    <address class="vcard">
    #      <div class="ascii">
    #        <div class="nameRole">
    #          <span class="fn">The ASCII name</span>
    #        </div>
    #      </div>
    #      <div class="alternative-contact">
    #        Alternate contact information:
    #      </div>
    #      <div class="non-ascii">
    #        <div class="nameRole">
    #          <span class="fn">The non-ASCII name</span>
    #          (<span class="role">editor</span>)
    #        </div>
    #      </div>
    #    </address>
        elif self.part == 'back':
            # ascii will be set only if name has codepoints not in the Latin script blocks
            name, ascii  = full_author_name_set(x)
            #
            addr = add.address(h, x, classes='vcard')
            #
            address = x.find('./address')
            postal = x.find('./address/postal')
            if address is None:
                address = lxml.etree.Element('address')
                x.append(address)
            if postal is None:
                # We render author name as part of postal, so make sure it's there
                address.insert(0, lxml.etree.Element('postal'))
            if ascii:
                ascii_div = add.div(addr, None, classes='ascii')
                for c in x.getchildren():
                    self.render(ascii_div, c)
                add.div(addr, None, 'Additional contact information:', classes='alternative-contact')
                nonasc_div = add.div(addr, None, classes='non-ascii')
                for c in x.getchildren():
                    self.render(nonasc_div, c)
            else:
                for c in x.getchildren():
                    self.render(addr, c)
            return addr

    # 9.7.3.  Authors of References
    # 
    #    In the output generated from a reference element, author tags are
    #    rendered inside an HTML <span> element with CSS class "refAuthor".
    #    See Section 4.8.6.2 of [RFC7322] for guidance on how author names are
    #    to appear.
    # 
    #    <span class="refAuthor">Flanagan, H.</span> and
    #    <span class="refAuthor">N. Brownlee</span>
        elif self.part == 'references':
            prev  = x.getprevious()
            next  = x.getnext()
            role = short_author_role(x)
            if   prev == None or prev.tag != 'author':
                # single autor or the first author in a list
                name, ascii = ref_author_name_first(x)
                span = wrap_ascii('span', '', name, ascii, role, classes='refAuthor')
            elif prev != None and prev.tag == 'author' and next != None and next.tag == 'author':
                # not first and not last author in a list
                name, ascii = ref_author_name_first(x)
                span = wrap_ascii('span', ', ', name, ascii, role, classes='refAuthor')
            elif prev != None and prev.tag == 'author' and prev.getprevious() != None and prev.getprevious().tag == 'author':
                # last author in a list of authors
                name, ascii = ref_author_name_last(x)
                span = wrap_ascii('span', ', and ', name, ascii, role, classes='refAuthor')
            elif prev != None and prev.tag == 'author':
                # second author of two
                name, ascii = ref_author_name_last(x)
                span = wrap_ascii('span', ' and ', name, ascii, role, classes='refAuthor')
            else:
                self.err(x, "Internal error, unexpected state when rendering authors.")
            h.append(span)
            return span

        else:
            self.err(x, "Did not expect to be asked to render <%s> while in <%s>" % (x.tag, x.getparent().tag))

    # 9.8.  <back>
    # 
    #    If there is exactly one <references> child, render that child in a
    #    similar way to a <section>.  If there are more than one <references>
    #    children, render as a <section> whose name is "References",
    #    containing a <section> for each <references> child.
    # 
    #    After any <references> sections, render each <section> child of
    #    <back> as an appendix.
    # 
    #    <section id="n-references">
    #      <h2 id="s-2">
    #        <a class="selfRef" href="#s-2">2.</a>
    #        <a class="selfRef" href="#n-references">References</a>
    #      </h2>
    #      <section id="n-normative">
    #        <h3 id="s-2.1">
    #          <a class="selfRef" href="#s-2.1">2.1.</a>
    #          <a class="selfRef" href="#n-normative">Normative</a>
    #        </h3>
    #        <dl class="reference"></dl>
    #      </section>
    #      <section id="n-informational">
    #        <h3 id="s-2.2">
    #          <a class="selfRef" href="#s-2.2">2.2.</a>
    #          <a class="selfRef" href="#n-informational">Informational</a>
    #        </h3>
    #        <dl class="reference"></dl>
    #      </section>
    #    </section>
    #    <section id="n-unimportant">
    #      <h2 id="s-A">
    #        <a class="selfRef" href="#s-A">Appendix A.</a>
    #        <a class="selfRef" href="#n-unimportant">Unimportant</a>
    #      </h2>
    #    </section>
    render_back = skip_renderer

    # 9.9.  <bcp14>
    # 
    #    This element marks up words like MUST and SHOULD [BCP14] with an HTML
    #    <span> element with the CSS class "bcp14".
    # 
    #    You <span class="bcp14">MUST</span> be joking.
    def render_bcp14(self, h, x):
        return add.span(h, x, classes='bcp14')

    # 9.10.  <blockquote>
    # 
    #    This element renders in a way similar to the HTML <blockquote>
    #    element.  If there is a "cite" attribute, it is copied to the HTML
    #    "cite" attribute.  If there is a "quoteFrom" attribute, it is placed
    #    inside a <cite> element at the end of the quote, with an <a> element
    #    surrounding it (if there is a "cite" attribute), linking to the cited
    #    URL.
    # 
    #    If the <blockquote> does not contain another element that gets a
    #    pilcrow (Section 5.2), a pilcrow is added.
    # 
    #    Note that the "&mdash;" at the beginning of the <cite> element should
    #    be a proper emdash, which is difficult to show in the display of the
    #    current format.
    # 
    #    <blockquote id="s-1.2-1"
    #      cite="http://...">
    #      <p id="s-1.2-2">Four score and seven years ago our fathers
    #        brought forth on this continent, a new nation, conceived
    #        in Liberty, and dedicated to the proposition that all men
    #        are created equal.
    #        <a href="#s-1.2-2" class="pilcrow">&para;</a>
    #      </p>
    #      <cite>&mdash; <a href="http://...">Abraham Lincoln</a></cite>
    #    </blockquote>
    def render_blockquote(self, h, x):
        frm  = x.get('quotedFrom')
        cite = x.get('cite')
        quote = add.blockquote(h, x)
        if cite:
            quote.set('cite', cite)
        for c in x.getchildren():
            self.render(quote, c)
        self.maybe_add_pilcrow(quote)
        if frm:
            if cite:
                frm = build.a(frm, href=cite)
            add.cite(quote, None, mdash, ' ', frm)
        return quote

    # 9.11.  <boilerplate>
    # 
    #    The Status of This Memo and the Copyright statement, together
    #    commonly referred to as the document boilerplate, appear after the
    #    Abstract.  The children of the input <boilerplate> element are
    #    treated in a similar fashion to unnumbered sections.
    # 
    #    <section id="status-of-this-memo">
    #      <h2 id="s-boilerplate-1">
    #        <a href="#status-of-this-memo" class="selfRef">
    #          Status of this Memo</a>
    #      </h2>
    #      <p id="s-boilerplate-1-1">This Internet-Draft is submitted in full
    #        conformance with the provisions of BCP 78 and BCP 79.
    #        <a href="#s-boilerplate-1-1" class="pilcrow">&para;</a>
    #      </p>
    #    ...
    render_boilerplate = skip_renderer

    # 9.12.  <br>
    # 
    #    This element is directly rendered as its HTML counterpart.  Note: in
    #    HTML, <br> does not have a closing slash.
    ## Removed from schema
    def render_br(self, h, x):
        return add.br(h, x)

    # 
    # 9.13.  <city>
    # 
    #    This element is rendered as a <span> element with CSS class
    #    "locality".
    # 
    #    <span class="locality">Guilford</span>
    def render_city(self, h, x):
        return self.address_line_renderer(h, x, classes='locality')

    def render_cityarea(self, h, x):
        return self.address_line_renderer(h, x, classes='locality')

    # 
    # 9.14.  <code>
    # 
    #    This element is rendered as a <span> element with CSS class "postal-
    #    code".
    # 
    #    <span class="postal-code">GU16 7HF<span>
    def render_code(self, h, x):
        return self.address_line_renderer(h, x, classes='postal-code')

    def render_sortingcode(self, h, x):
        return self.address_line_renderer(h, x, classes='postal-code')

    # 9.15.  <country>
    # 
    #    This element is rendered as a <div> element with CSS class "country-
    #    name".
    # 
    #    <div class="country-name">England</div>
    def render_country(self, h, x):
        return self.address_line_renderer(h, x, classes='country-name')

    # 9.16.  <cref>
    # 
    #    This element is rendered as a <span> element with CSS class "cref".
    #    Any anchor is copied to the "id" attribute.  If there is a source
    #    given, it is contained inside the "cref" <span> element with another
    #    <span> element of class "crefSource".
    # 
    #    <span class="cref" id="crefAnchor">Just a brief comment
    #    about something that we need to remember later.
    #    <span class="crefSource">--life</span></span>
    def render_cref(self, h, x):
        span = add.span(h, x, classes='cref')
        disp = x.get('display') == 'true'
        if disp:
            for c in x.getchildren():
                self.render(span, c)
            source = x.get('source')
            if source:
                add.span(span, None, source, classes='crefSource')
        return span

    # 9.17.  <date>
    # 
    #    This element is rendered as the HTML <time> element.  If the "year",
    #    "month", or "day" attribute is included on the XML element, an
    #    appropriate "datetime" element will be generated in HTML.
    # 
    #    If this date is a child of the document's <front> element, it gets
    #    the CSS class "published".
    # 
    #    If this date is inside a <reference> element, it gets the CSS class
    #    "refDate".
    # 
    #    <time datetime="2014-10" class="published">October 2014</time>
    def render_date(self, h, x):
        parts = extract_date(x, self.options.date)
        text = format_date(*parts, legacy=self.options.legacy_date_format)
        datetime = format_date_iso(*parts)
        time = add.time(h, x, text, datetime=datetime)
        if x.getparent() == self.root.find('front'):
            time.set('class', 'published')
        return time

    # 9.18.  <dd>
    # 
    #    This element is directly rendered as its HTML counterpart.
    def render_dd(self, h, x):
        indent = x.getparent().get('indent')
        style = 'margin-left: %.1fem' % (int(indent)*0.5) if indent else None
        dd = add.dd(h, x, style=style)
        for c in x.getchildren():
            self.render(dd, c)
        return dd

    # 9.19.  <displayreference>
    # 
    #    This element does not affect the HTML output, but it is used in the
    #    generation of the <reference>, <referencegroup>, <relref>, and <xref>
    #    elements.
    render_displayreference = null_renderer

    # 9.20.  <dl>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    #    If the hanging attribute is "false", add the "dlParallel" class, else
    #    add the "dlHanging" class.
    # 
    #    If the spacing attribute is "compact", add the "dlCompact" class.
    def render_dl(self, h, x):
        newline = x.get('newline')
        spacing = x.get('spacing')
        classes = []
        if   newline == 'true':
            classes.append('dlNewline')
        elif newline == 'false':
            classes.append('dlParallel')
        if   spacing == 'compact':
            classes.append('dlCompact')
        classes = ' '.join(classes)
        dl = add.dl(h, x, classes=classes)
        for c in x.getchildren():
            self.render(dl, c)
        return dl

    # 9.21.  <dt>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_dt = default_renderer

    # 
    # 9.22.  <em>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_em = default_renderer

    # 9.23.  <email>
    # 
    #    This element is rendered as an HTML <div> containing the string
    #    "Email:" and an HTML <a> element with the "href" attribute set to the
    #    equivalent "mailto:" URI, a CSS class of "email", and the contents
    #    set to the email address.  If this is the version of the address with
    #    ASCII, the "ascii" attribute is preferred to the element text.
    # 
    #    <div>
    #      <span>Email:</span>
    #      <a class="email" href="mailto:joe@example.com">joe@example.com</a>
    #    </div>
    def render_email(self, h, x):
        value = x.text.strip()
        cls = 'email'
        div = add.div(h, None,
                    build.span("Email:"), '\n',
                    build.a(value, href='mailto:%s'%value, classes=cls),
                    classes=cls,
                )
        return div

    # 
    # 9.24.  <eref>
    # 
    #    This element is rendered as an HTML <a> element, with the "href"
    #    attribute set to the value of the "target" attribute and the CSS
    #    class of "eref".
    # 
    #    <a href="https://..." class="eref">the text</a>
    def render_eref(self, h, x):
        target = x.get('target')
        if x.text:
            hh = add.a(h, x, href=target)            
        else:
            hh = add.span(h, x, build.a(target, href=target))
        return hh

    # 9.25.  <figure>
    # 
    #    This element renders as the HTML <figure> element, containing the
    #    artwork or sourcecode indicated and an HTML <figcaption> element.
    #    The <figcaption> element will contain an <a> element around the
    #    figure number.  It will also contain another <a> element with CSS
    #    class "selfRef" around the figure name, if a name was given.
    # 
    #    <figure id="f-1">
    #      ...
    #      <figcaption>
    #        <a href="#f-1">Figure 1.</a>
    #        <a href="#n-it-figures" id="n-it-figures" class="selfRef">
    #          It figures
    #        </a>
    #      </figcaption>
    #    </figure>
    def render_figure(self, h, x):
        name = x.find('name')
        if name != None and name.text:
            add.span(h, None, id=name.get('slugifiedName'))
        figure = add.figure(h, x)
        for c in x.iterchildren('artset', 'artwork', 'sourcecode'):
            self.render(figure, c)
        pn = x.get('pn')
        caption = add.figcaption(figure, None)
        a = add.a(caption, None, pn.replace('-',' ',1).title(), href='#%s'%pn)
        if name != None and name.text:
            a.tail = ':\n'
            a = add.a(caption, None, href='#%s'%name.get('slugifiedName'), classes='selfRef')
            self.inline_text_renderer(a, name)
        return figure

    # 9.26.  <front>
    # 
    #    See "Document Information" (Section 6.5) for information on this
    #    element.
    def render_front(self, h, x):
        if self.part == 'front':
            # 6.5.  Document Information
            # 
            #    Information about the document as a whole will appear as the first
            #    child of the HTML <body> element, embedded in an HTML <dl> element
            #    with id="identifiers".  The defined terms in the definition list are
            #    "Workgroup:", "Series:", "Status:", "Published:", and "Author:" or
            #    "Authors:" (as appropriate).  For example:
            # 
            #    <dl id="identifiers">
            #      <dt>Workgroup:</dt>
            #        <dd class="workgroup">rfc-interest</dd>
            #      <dt>Series:</dt>
            #        <dd class="series">Internet-Draft</dd>
            #      <dt>Status:</dt>
            #        <dd class="status">Informational</dd>
            #      <dt>Published:</dt>
            #        <dd><time datetime="2014-10-25"
            #                  class="published">2014-10-25</time></dd>
            #      <dt>Authors:</dt>
            #        <dd class="authors">
            #          <div class="author">
            #            <span class="initial">J.</span>
            #            <span class="surname">Hildebrand</span>
            #            (<span class="organization">Cisco Systems, Inc.</span>)
            #            <span class="editor">Ed.</span>
            #          </div>
            #          <div class="author">
            #            <span class="initial">H.</span>
            #            <span class="surname">Flanagan</span>
            #            (<span class="organization">RFC Editor</span>)
            #          </div>
            #        </dd>
            #    </dl>
            # 

            # Now, a text format RFC has the following information, optionals in
            # parentheses:
            # 
            # If RFC:
            #   * <Stream Name>
            #   * Request for Comments: <Number>
            #   * (STD|BCP|FYI: <Number>)
            #   * (Obsoletes: <Number>[, <Number>]*)
            #   * (Updates: <Number>[, <Number>]*)
            #   * Category: <Category Name>
            #   * ISSN: 2070-1721
            # else:
            #   * <Workgroup name> or "Network Working Group"
            #   * Internet-Draft
            #   * (STD|BCP|FYI: <Number> (if approved))
            #   * (Obsoletes: <Number>[, <Number>]*)
            #   * (Updates: <Number>[, <Number>]*)
            #   * Intended Status: <Cagegory Name>
            #   * Expires: <Date>

            def entry(dl, name, value):
                if value != None:
                    cls = slugify(name)
                    dl.append( build.dt('%s:'%name, classes='label-%s'%cls))
                    dl.append( build.dd(value, classes=cls))
            #
            dl = build.dl(id='identifiers')
            h.append( build.div(dl, classes='document-information' ))
            if self.options.rfc:
                # Stream
                stream = self.root.get('submissionType')
                entry(dl, 'Stream', strings.stream_name[stream])
                # Series info
                for series in x.xpath('./seriesInfo'):
                    self.render_seriesinfo(dl, series)
                for section in ['obsoletes', 'updates']:
                    items = self.root.get(section)
                    if items:
                        alist = []
                        for num in items.split(','):
                            num = num.strip()
                            a = build.a(num, href=os.path.join(self.options.rfc_base_url, 'rfc%s.txt'%num), classes='eref')
                            a.tail = ' '
                            alist.append(a)
                        entry(dl, section.title(), *alist)

                category = self.root.get('category', '')
                if category:
                    entry(dl, 'Category', strings.category_name[category])
                # Publication date
                entry(dl, 'Published', self.render_date(None, x.find('date')))
                # ISSN
                entry(dl, 'ISSN', '2070-1721')

            else:
                # Workgroup
                for wg in x.xpath('./workgroup'):
                    entry(dl, 'Workgroup', wg.text)
                # Internet-Draft
                for series in x.xpath('./seriesInfo'):
                    entry(dl, series.get('name'), series.get('value'))
                # Obsoletes and Updates
                for section in ['obsoletes', 'updates']:
                    items = self.root.get(section)
                    if items:
                        for num in items.split(','):
                            num = num.strip()
                            a = build.a(num, href=os.path.join(self.options.rfc_base_url, 'rfc%s.txt'%num), classes='eref')
                            a.tail = ' '
                            entry(dl, section.title(), a)
                        a.tail += '(if approved)'
                # Publication date
                entry(dl, 'Published', self.render_date(None, x.find('date')))
                # Intended category
                category = self.root.get('category', '')
                if category:
                    entry(dl, 'Intended Status', strings.category_name[category])
                # Expiry date
                if self.root.get('ipr') != 'none':
                    exp = get_expiry_date(self.root, self.date)
                    expdate = build.date(year=str(exp.year), month=str(exp.month))
                    if exp.day:
                        expdate.set('day', str(exp.day))
                    entry(dl, 'Expires', self.render_date(None, expdate))

            authors = x.xpath('./author')
            dl.append( build.dt('Authors:' if len(authors)>1 else 'Author:', classes='label-authors' ))
            dd = add.dd(dl, None, classes='authors')
            for a in authors:
                self.render(dd, a)

            for c in x.iterchildren('title', 'abstract', 'note', 'boilerplate'):
                self.render(h, c)

        elif self.part == 'references':
            self.default_renderer(h, x)
        else:
            self.err(x, "Did not expect to be asked to render <%s> while in <%s> (self.part: %s)" % (x.tag, x.getparent().tag, self.part))
        

    # 9.27.  <iref>
    # 
    #    This element is rendered as an empty <> tag of class "iref", with an
    #    "id" attribute consisting of the <iref> element's "irefid" attribute:
    # 
    #    <span class="iref" id="s-Paragraphs-first-1"/>
    def render_iref(self, h, x):
        span = add.span(None, x, classes='iref', id=x.get('pn'))
        if h.tag in ['table', ]:
            h.addprevious(span)
        else:
            h.append(span)
        return span

    # 9.28.  <keyword>
    # 
    #    Each <keyword> element renders its text into the <meta> keywords in
    #    the document's header, separated by commas.
    # 
    #    <meta name="keywords" content="html,css,rfc">
    # 
    # 9.29.  <li>
    # 
    #    This element is rendered as its HTML counterpart.  However, if there
    #    is no contained element that has a pilcrow (Section 5.2) attached, a
    #    pilcrow is added.
    # 
    #    <li id="s-2-7">Item <a href="#s-2-7" class="pilcrow">&para;</a></li>
    def render_li_ul(self, h, x):
        li = add.li(h, x, classes=h.get('class'))
        for c in x.getchildren():
            self.render(li, c)
        self.maybe_add_pilcrow(li)
        return li

    def render_li(self, h, x):
        if   h.tag == 'ul':
            li = self.render_li_ul(h, x)
        elif h.tag == 'dl':
            li = self.render_li_dl(h, x)
        elif h.tag == 'ol':
            li = self.render_li_ol(h, x)
        else:
            self.err(x, "Did not expect to be asked to render <%s> while in <%s>" % (x.tag, h.tag))
            li = None
        return li

    # 9.30.  <link>
    # 
    #    This element is rendered as its HTML counterpart, in the HTML header.
    def render_link(self, h, x):
        link = add.link(h, x, rel=x.get('rel'), href=x.get('href'))
        return link
        
    # 9.31.  <middle>
    # 
    #    This element does not add any direct output to HTML.
    render_middle = skip_renderer

    ## Potential extension: <math>
    ##
    ## Same content as for instance <name>, but may contain unicode
    ## characters of categories L*, P*, Sm, Sk or Zs.  For categories L*, the script
    ## must be either Common, Greek, or Hebrew.
    ##
    ## def render_math(self, s, x):
    ##     for t in x.itertext():
    ##         for c in t:
    ##             cat = unicode.category(c)
    ##             if cat.beginswith('L'):
    ##                scr = get_script(c)
    ##                if not scr in ['Common', 'Greek', 'Hebrew', ]:
    ##                   self.err(x, ...)
    ##     div = add.div(h, x, classes="inline-math")
    ##     for c in x.getchildren():
    ##         self.render(div, c)
    ##

    # 9.32.  <name>
    # 
    #    This element is never rendered directly; it is only rendered when
    #    considering a parent element, such as <figure>, <references>,
    #    <section>, or <table>.
    def render_name(self, s, x):
        p = x.getparent()
        if   p.tag in [ 'note', 'section', 'references' ]:
            pn = p.get('pn')
            prefix, number = pn.split('-', 1)
            number += '.'
            if re.search(r'^[a-z]', number):
                num = number.split('.', 1)[1]
            else:
                num = number
            level = min([6, len(num.split('.')) ])
            tag = 'h%d' % level
            h = build(tag, id=x.get('slugifiedName'))
            s.append(h)
            #
            numbered = p.get('numbered') or ('true' if p.tag == 'references' else 'false')
            if numbered == 'true':
                if number.startswith('appendix'):
                    number = number.replace('.', ' ', 1).title()
                elif re.search('^[a-z]', number):
                    number = number.title()
                a_number = build.a(number, '\u00a0', href='#%s'%pn, classes='section-number selfRef')
                h.append( a_number)
            a_title = build.a(href='#%s'%x.get('slugifiedName'), classes='section-name selfRef')
            self.inline_text_renderer(a_title, x)
            h.append(a_title)
            return h
        elif p.tag in [ 'table', 'figure' ]:
            return None
        else:
            self.warn(x, "Did not expect to be asked to render <%s> while in <%s>" % (x.tag, x.getparent().tag))
            self.default_renderer(s, x)


    # 9.33.  <note>
    # 
    #    This element is rendered like a <section> element, but without a
    #    section number and with the CSS class of "note".  If the
    #    "removeInRFC" attribute is set to "yes", the generated <div> element
    #    will also include the CSS class "rfcEditorRemove".
    # 
    #    <section id="s-note-1" class="note rfcEditorRemove">
    #      <h2>
    #        <a href="#n-editorial-note" class="selfRef">Editorial Note</a>
    #      </h2>
    #      <p id="s-note-1-1">
    #        Discussion of this draft takes place...
    #        <a href="#s-note-1-1" class="pilcrow">&para;</a>
    #      </p>
    #    </section>
    def render_note(self, h, x):
        classes = 'note'
        if x.get('removeInRFC') == 'true':
            classes += ' rfcEditorRemove'
        section = add.section(h, x, classes=classes)
        for c in x.getchildren():
            self.render(section, c)
        return section

    # 9.34.  <ol>
    # 
    #    The output created from an <ol> element depends upon the "style"
    #    attribute.
    # 
    #    If the "spacing" attribute has the value "compact", a CSS class of
    #    "olCompact" will be added.
    # 
    #    The group attribute is not copied; the input XML should have start
    #    values added by a prep tool for all grouped <ol> elements.
    def render_ol(self, h, x):
        type = x.get('type')
        if len(type) > 1 and '%' in type:
            ol = add.dl(h, x, classes='olPercent')
        else:
            attrib = dict([ (k,v) for (k,v) in x.attrib.items() if k in ['start', 'type', ] ])
            ol = add.ol(h, x, classes=x.get('spacing'), **attrib)
        for c in x.getchildren():
            self.render(ol, c)
        return ol

    # 9.34.1.  Percent Styles
    # 
    #    If the style attribute includes the character "%", the output is a
    #    <dl> tag with the class "olPercent".  Each contained <li> element is
    #    emitted as a <dt>/<dd> pair, with the generated label in the <dt> and
    #    the contents of the <li> in the <dd>.
    # 
    #    <dl class="olPercent">
    #      <dt>Requirement xviii:</dt>
    #      <dd>Wheels on a big rig</dd>
    #    </dl>
    def render_li_dl(self, h, x):
        label = x.get('derivedCounter')
        dt = add.dt(h, None, label)
        dd = add.dd(h, x)
        for c in x.getchildren():
            self.render(dd, c)
        self.maybe_add_pilcrow(dd)
        return dt, dd

    # 9.34.2.  Standard Styles
    # 
    #    For all other styles, an <ol> tag is emitted, with any "style"
    #    attribute turned into the equivalent HTML attribute.
    # 
    #    <ol class="compact" type="I" start="18">
    #      <li>Wheels on a big rig</li>
    #    </ol>
    def render_li_ol(self, h, x):
        li = add.li(h, x)
        for c in x.getchildren():
            self.render(li, c)
        self.maybe_add_pilcrow(li)
        return li

    # 9.35.  <organization>
    # 
    #    This element is rendered as an HTML <div> tag with CSS class "org".
    # 
    #    If the element contains the "ascii" attribute, the organization name
    #    is rendered twice: once with the non-ASCII version wrapped in an HTML
    #    <span> tag of class "non-ascii" and then as the ASCII version wrapped
    #    in an HTML <span> tag of class "ascii" wrapped in parentheses.
    # 
    #    <div class="org">
    #      <span class="non-ascii">Test Org</span>
    #      (<span class="ascii">TEST ORG</span>)
    #    </div>
    render_organization = null_renderer # handled in render_address

    # 9.36.  <phone>
    # 
    #    This element is rendered as an HTML <div> tag containing the string
    #    "Phone:" (wrapped in a span), an HTML <a> tag with CSS class "tel"
    #    containing the phone number (and an href with a corresponding "tel:"
    #    URI), and an HTML <span> with CSS class "type" containing the string
    #    "VOICE".
    # 
    #    <div>
    #      <span>Phone:</span>
    #      <a class="tel" href="tel:+1-720-555-1212">+1-720-555-1212</a>
    #      <span class="type">VOICE</span>
    #    </div>
    def render_phone(self, h, x):
        # The content of <span class="type">VOICE</span> seems to violate the
        # vcard types (they identify things like 'Home', 'Work', etc) and
        # will be skipped.  The 
        if not x.text:
            return None
        value = x.text.strip()
        cls = 'tel'
        div = add.div(h, None,
                    build.span("Phone:"), '\n',
                    build.a(value, href='tel:%s'%value, classes=cls),
                    classes=cls,
                )
        return div

    # 9.37.  <postal>
    # 
    #    This element renders as an HTML <div> with CSS class "adr", unless it
    #    contains one or more <postalLine> child elements; in which case, it
    #    renders as an HTML <pre> element with CSS class "label".
    # 
    #    When there is no <postalLine> child, the following child elements are
    #    rendered into the HTML:
    # 
    #    o  Each <street> is rendered
    # 
    #    o  A <div> that includes:
    # 
    #       *  The rendering of all <city> elements
    # 
    #       *  A comma and a space: ", "
    # 
    #       *  The rendering of all <region> elements
    # 
    #       *  Whitespace
    # 
    #       *  The rendering of all <code> elements
    # 
    #    o  The rendering of all <country> elements
    # 
    #    <div class="adr">
    #      <div class="street-address">1 Main Street</div>
    #      <div class="street-address">Suite 1</div>
    #      <div>
    #        <span class="city">Denver</span>,
    #        <span class="region">CO</span>
    #        <span class="postal-code">80212</span>
    #      </div>
    #      <div class="country-name">United States of America</div>
    #    </div>
    ##
    ##  Much of the description above is much too americentric, and also
    ##  conflicts with hCard.  Examples from hCard will be used instead,
    ##  and addresses rendered in a format appropriate for their country.
    ##  
    ##   <span class="adr">
    ##      <span class="street-address">12 rue Danton</span>
    ##      <span class="postal-code">94270</span>
    ##      <span class="locality">Le Kremlin-Bicetre</span>
    ##      <span class="country-name">France</span>
    ##   </span>    
    def render_postal(self, h, x):
        latin = h.get('class') == 'ascii'
        adr = get_normalized_address_info(self, x, latin=latin)
        if adr:
            align = 'left' if latin else get_bidi_alignment(adr)
            for item in format_address(adr, latin=latin):
                item.set('class', align)
                h.append(item)
        else:
            # render elements in found order
            for c in x.getchildren():
                self.render(h, c)

    # 9.38.  <postalLine>
    # 
    #    This element renders as the text contained by the element, followed
    #    by a newline.  However, the last <postalLine> in a given <postal>
    #    element should not be followed by a newline.  For example:
    # 
    #    <postal>
    #      <postalLine>In care of:</postalLine>
    #      <postalLine>Computer Sciences Division</postalLine>
    #    </postal>
    # 
    #    Would be rendered as:
    # 
    #    <pre class="label">In care of:
    #    Computer Sciences Division</pre>
    def render_postalline(self, h, x):
        return self.address_line_renderer(h, x, classes='extended-address')

    # 9.39.  <refcontent>
    # 
    #    This element renders as an HTML <span> with CSS class "refContent".
    # 
    #    <span class="refContent">Self-published pamphlet</span>
    def render_refcontent(self, h, x):
        span = add.span(h, x, classes='refContent')
        for c in x.getchildren():
            self.render(span, c)
        return span


    # 9.40.  <reference>
    # 
    #    If the parent of this element is not a <referencegroup>, this element
    #    will render as a <dt> <dd> pair with the defined term being the
    #    reference "anchor" attribute surrounded by square brackets and the
    #    definition including the correct set of bibliographic information as
    #    specified by [RFC7322].  The <dt> element will have an "id" attribute
    #    of the reference anchor.
    # 
    #    <dl class="reference">
    #      <dt id="RFC5646">[RFC5646]</dt>
    #      <dd>
    #        <span class="refAuthor">Phillips, A.</span>
    #        <span>and</span>
    #        <span class="refAuthor">M. Davis</span>
    #        <span class="refTitle">"Tags for Identifying Languages"</span>,
    #        ...
    #      </dd>
    #    </dl>
    # 
    #    If the child of a <referencegroup>, this element renders as a <div>
    #    of class "refInstance" whose "id" attribute is the value of the
    #    <source> element's "anchor" attribute.
    # 
    #    <div class="refInstance" id="RFC5730">
    #      ...
    #    </div>
    def render_reference(self, h, x):
        p = x.getparent()
        if   p.tag == 'referencegroup':
            div = add.div(h, x, classes='refInstance')
            outer = div
            inner = div
        elif p.tag != 'referencegroup':
            dt = add.dt(h, x, '[%s]'%x.get('derivedAnchor'))
            dd = add.dd(h, None)
            outer = dt, dd
            inner = dd
        else:
            self.err(x, "Did not expect to be asked to render <%s> while in <%s>" % (x.tag, x.getparent().tag))
        # Deal with parts in the correct order
        for c in x.iterdescendants('author'):
            self.render(inner, c)
        for ctag in ('title', 'refcontent', 'stream', 'seriesInfo', 'date', ):
            for c in x.iterdescendants(ctag):
                if len(inner):
                    inner[-1].tail = ', '
                self.render(inner, c)
        if p.tag != 'referencegroup':
            target = x.get('target')
            if target:
                inner.append( build.span(', <', build.a(target, href=target), '>') )
        if len(inner):
            inner[-1].tail = '. '
        for ctag in ('annotation', ):
            for c in x.iterdescendants(ctag):
                self.render(inner, c)
        #
        return outer

    # 9.41.  <referencegroup>
    # 
    #    A <referencegroup> is translated into a <dt> <dd> pair, with the
    #    defined term being the referencegroup "anchor" attribute surrounded
    #    by square brackets, and the definition containing the translated
    #    output of all of the child <reference> elements.
    # 
    #    <dt id="STD69">[STD69]</dt>
    #    <dd>
    #      <div class="refInstance" id="RFC5730">
    #        <span class="refAuthor">Hollenbeck, S.</span>
    #        ...
    #      </div>
    #      <div class="refInstance" id="RFC5731">
    #        <span class="refAuthor">Hollenbeck, S.</span>
    #        ...
    #      </div>
    #      ...
    #    </dd>
    def render_referencegroup(self, h, x):
        dt = add.dt(h, x, '[%s]'%x.get('derivedAnchor'))
        dd = add.dd(h, None)
        for c in x.getchildren():
            self.render(dd, c)
        target = x.get('target')
        if target:
            dd.append( build.span('<', build.a(target, href=target), '>') )
        return dt, dd

    # 9.42.  <references>
    # 
    #    If there is at exactly one <references> element, a section is added
    #    to the document, continuing with the next section number after the
    #    last top-level <section> in <middle>.  The <name> element of the
    #    <references> element is used as the section name.
    # 
    #    <section id="n-my-references">
    #      <h2 id="s-3">
    #        <a href="#s-3" class="selfRef">3.</a>
    #        <a href="#n-my-references class="selfRef">My References</a>
    #      </h2>
    #      ...
    #    </section>
    # 
    #    If there is more than one <references> element, an HTML <section>
    #    element is created to contain a subsection for each of the
    #    <references>.  The section number will be the next section number
    #    after the last top-level <section> in <middle>.  The name of this
    #    section will be "References", and its "id" attribute will be
    #    "n-references".
    # 
    #    <section id="n-references">
    #      <h2 id="s-3">
    #        <a href="#s-3" class="selfRef">3.</a>
    #        <a href="#n-references" class="selfRef">References</a>
    #      </h2>
    #      <section id="n-informative-references">
    #        <h3 id="s-3.1">
    #          <a href="#s-3.1" class="selfRef">3.1.</a>
    #          <a href="#n-informative-references" class="selfRef">
    #            Informative References</a></h3>
    #        <dl class="reference">...
    #        </dl>
    #      </section>
    #      ...
    #    </section>
    def render_references(self, h, x):
        self.part = x.tag
        section = add.section(h, x)
        hh = section
        for c in x.getchildren():
            if c.tag in ['reference', 'referencegroup'] and hh.tag != 'dl':
                hh = add.dl(hh, None, classes='references')
            self.render(hh, c)
        return section

    # 
    # 9.43.  <region>
    # 
    #    This element is rendered as a <span> tag with CSS class "region".
    # 
    #    <span class="region">Colorado</span>
    def render_region(self, h, x):
        return self.address_line_renderer(h, x, classes='region')

    # 
    # 9.44.  <relref>
    # 
    #    This element is rendered as an HTML <a> tag with CSS class "relref"
    #    and "href" attribute of the "derivedLink" attribute of the element.
    #    Different values of the "displayFormat" attribute cause the text
    #    inside that HTML <a> tag to change and cause extra text to be
    #    generated.  Some values of the "displayFormat" attribute also cause
    #    another HTML <a> tag to be rendered with CSS class "xref" and an
    #    "href" of "#" and the "target" attribute (modified by any applicable
    #    <displayreference> XML element) and text inside of the "target"
    #    attribute (modified by any applicable <displayreference> XML
    #    element).  When used, this <a class='xref'> HTML tag is always
    #    surrounded by square brackets, for example, "[<a class='xref'
    #    href='#foo'>foo</a>]".

    ## Deprecated, removed by preptool


    # 9.44.1.  displayFormat='of'
    # 
    #    The output is an <a class='relref'> HTML tag, with contents of
    #    "Section " and the value of the "section" attribute.  This is
    #    followed by the word "of" (surrounded by whitespace).  This is
    #    followed by the <a class='xref'> HTML tag (surrounded by square
    #    brackets).
    # 
    #    For example, with an input of:
    # 
    #    See <relref section="2.3" target="RFC9999" displayFormat="of"
    #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"/>
    #    for an overview.
    # 
    #    The HTML generated will be:
    # 
    #    See <a class="relref"
    #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section
    #    2.3</a> of [<a class="xref" href="#RFC9999">RFC9999</a>]
    #    for an overview.
    # 
    # 9.44.2.  displayFormat='comma'
    # 
    #    The output is an <a class='xref'> HTML tag (wrapped by square
    #    brackets), followed by a comma (","), followed by whitespace,
    #    followed by an <a class='relref'> HTML tag, with contents of
    #    "Section " and the value of the "section" attribute.
    # 
    #    For example, with an input of:
    # 
    #    See <relref section="2.3" target="RFC9999" displayFormat="comma"
    #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"/>,
    #    for an overview.
    # 
    #    The HTML generated will be:
    # 
    #    See [<a class="xref" href="#RFC9999">RFC9999</a>], <a class="relref"
    #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section 2.3</a>,
    #    for an overview.
    # 
    # 9.44.3.  displayFormat='parens'
    # 
    #    The output is an <a> element with "href" attribute whose value is the
    #    value of the "target" attribute prepended by "#", and whose content
    #    is the value of the "target" attribute; the entire element is wrapped
    #    in square brackets.  This is followed by whitespace.  This is
    #    followed by an <a> element whose "href" attribute is the value of the
    #    "derivedLink" attribute and whose content is the value of the
    #    "derivedRemoteContent" attribute; the entire element is wrapped in
    #    parentheses.
    # 
    #    For example, if Section 2.3 of RFC 9999 has the title "Protocol
    #    Overview", for an input of:
    # 
    #    See <relref section="2.3" target="RFC9999" displayFormat="parens"
    #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"
    #    derivedRemoteContent="Section 2.3"/> for an overview.
    # 
    #    The HTML generated will be:
    # 
    #    See [<a class="relref" href="#RFC9999">RFC9999</a>]
    #    (<a class="relref"
    #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section
    #    2.3</a>) for an overview.
    # 
    # 9.44.4.  displayFormat='bare'
    # 
    #    The output is an <a> element whose "href" attribute is the value of
    #    the "derivedLink" attribute and whose content is the value of the
    #    "derivedRemoteContent" attribute.
    # 
    #    For this input:
    # 
    #    See <relref section="2.3" target="RFC9999" displayFormat="bare"
    #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"
    #    derivedRemoteContent="Section 2.3"/> and ...
    # 
    #    The HTML generated will be:
    # 
    #    See <a class="relref"
    #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section
    #    2.3</a> and ...

    # 9.45.  <rfc>
    # 
    #    Various attributes of this element are represented in different parts
    #    of the HTML document.

    # 9.46.  <section>
    # 
    #    This element is rendered as an HTML <section> element, containing an
    #    appropriate level HTML heading element (<h2>-<h6>).  That heading
    #    element contains an <a> element around the part number (pn), if
    #    applicable (for instance, <abstract> does not get a section number).
    #    Another <a> element is included with the section's name.
    # 
    #    <section id="intro">
    #      <h2 id="s-1">
    #        <a href="#s-1" class="selfRef">1.</a>
    #        <a href="#intro" class="selfRef">Introduction</a>
    #      </h2>
    #      <p id="s-1-1">Paragraph <a href="#s-1-1" class="pilcrow">&para;</a>
    #      </p>
    #    </section>
    def render_section(self, h, x):
        section = add(x.tag, h, x)
        anchor = x.get('anchor')
        if anchor == 'toc':
            add.a(section, None, "\u25b2", href="#", onclick="scroll(0,0)", classes="toplink")
        for c in x.getchildren():
            self.render(section, c)
        return section


    # 9.47.  <seriesInfo>
    # 
    #    This element is rendered in an HTML <span> element with CSS name
    #    "seriesInfo".
    # 
    #    <span class="seriesInfo">RFC 5646</span>
    ## This is different from what's shown in the sample documents, _and_
    ## different from what's shown in Section 6.5.  Following the sample doc
    ## here.
    def render_seriesinfo(self, h, x):
        def entry(dl, name, value):
            cls = slugify(name)
            dl.append( build.dt('%s:'%name, classes='label-%s'%cls))
            dl.append( build.dd(value, classes=cls))
        #
        name  = x.get('name') 
        value = x.get('value')
        if   self.part == 'front':
            if   name == 'RFC':
                value = build.a(value, href=os.path.join(self.options.rfc_base_url, 'rfc%s.txt'%value), classes='eref')
            elif name == 'DOI':
                value = build.a(value, href=os.path.join(self.options.doi_base_url, value), classes='eref')
            elif name == 'Internet-Draft':
                value = build.a(value, href=os.path.join(self.options.id_base_url, value), classes='eref')
            entry(h, name, value)
            return h
        elif self.part == 'references':
            span = add.span(h, x, name, ' ', value, classes='seriesInfo')
            return span
        else:
            self.err(x, "Did not expect to be asked to render <%s> while in <%s>" % (x.tag, x.getparent().tag))


    # 9.48.  <sourcecode>
    # 
    #    This element is rendered in an HTML <pre> element with a CSS class of
    #    "sourcecode".  Note that CDATA blocks do not work consistently in
    #    HTML, so all <, >, and & must be escaped as &lt;, &gt;, and &amp;,
    #    respectively.  If the input XML has a "type" attribute, another CSS
    #    class of "lang-" and the type is added.
    # 
    #    If the sourcecode is not inside a <figure> element, a pilcrow
    #    (Section 5.2) is included.  Inside a <figure> element, the figure
    #    title serves the purpose of the pilcrow.
    # 
    #    <pre class="sourcecode lang-c">
    #    #include &lt;stdio.h&gt;
    # 
    #    int main(void)
    #    {
    #        printf(&quot;hello, world\n&quot;);
    #        return 0;
    #    }
    #    </pre>
    def render_sourcecode(self, h, x):
        file = x.get('name')
        type = x.get('type')
        mark = x.get('markers') == 'true'
        classes = 'sourcecode'
        if type:
            classes += ' lang-%s' % type
        div = add.div(h, x)
        div.text = None
        pre = add.pre(div, None, x.text, classes=classes)
        if mark:
            text = pre.text
            text = (' file "%s"\n%s' % (file, text)) if text else '\n%s' % text
            text = "<CODE BEGINS>%s\n<CODE ENDS>" % text
            pre.text = text
        self.maybe_add_pilcrow(div)
        return div


    def render_stream(self, h, x):
        return add.span(h, x, classes="stream")

    # 9.49.  <street>
    # 
    #    This element renders as an HTML <div> element with CSS class "street-
    #    address".
    # 
    #    <div class="street-address">1899 Wynkoop St, Suite 600</div>
    def render_street(self, h, x):
        return self.address_line_renderer(h, x, classes='street-address')

    def render_extaddr(self, h, x):
        return self.address_line_renderer(h, x, classes='extended-address')

    def render_pobox(self, h, x):
        return self.address_line_renderer(h, x, classes='post-office-box')


    # 9.50.  <strong>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_strong = default_renderer

    # 9.51.  <sub>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_sub = default_renderer

    # 9.52.  <sup>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_sup = default_renderer

    # 9.53.  <t>
    # 
    #    This element is rendered as an HTML <p> element.  A pilcrow
    #    (Section 5.2) is included.
    # 
    #    <p id="s-1-1">A paragraph.
    #      <a href="#s-1-1" class="pilcrow">&para;</a></p>
    def render_t(self, h, x):
        p = add.p(h, x)
        for c in x.getchildren():
            self.render(p, c)
        add.a(p, None, pilcrow, classes='pilcrow', href='#%s'%x.get('pn'))
        return p

    # 
    # 9.54.  <table>
    # 
    #    This element is directly rendered as its HTML counterpart.
    def render_table(self, h, x):
        name = x.find('name')
        if name != None and name.text:
            add.span(h, None, id=name.get('slugifiedName'))
        align = x.get('align')
        table = add.table(h, x, classes=align)
        caption = add.caption(table, None)
        pn = x.get('pn')
        a = add.a(caption, None, pn.replace('-',' ',1).title(), href='#%s'%pn)
        if name != None:
            a.tail = ':\n'
            a = add.a(caption, None, href='#%s'%name.get('slugifiedName'), classes='selfRef')
            self.inline_text_renderer(a, name)
        for c in x.getchildren():
            self.render(table, c)
        return table

    # 9.55.  <tbody>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_tbody = default_renderer

    # 9.56.  <td>
    # 
    #    This element is directly rendered as its HTML counterpart.
    def render_td(self, h, x):
        classes = "text-%s" % x.get('align')
        hh = add(x.tag, h, x, classes=classes)
        hh.set('rowspan', x.get('rowspan', '1'))
        hh.set('colspan', x.get('colspan', '1'))
        for c in x.getchildren():
            self.render(hh, c)

    # 9.57.  <tfoot>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_tfoot = default_renderer

    # 9.58.  <th>
    # 
    #    This element is directly rendered as its HTML counterpart.
    def render_th(self, h, x):
        classes = "text-%s" % x.get('align')
        hh = add(x.tag, h, x, classes=classes)
        hh.set('rowspan', x.get('rowspan', '1'))
        hh.set('colspan', x.get('colspan', '1'))
        for c in x.getchildren():
            self.render(hh, c)

    # 9.59.  <thead>
    #
    #    This element is directly rendered as its HTML counterpart.
    render_thead = default_renderer
 
    # 9.60.  <title>
    # 
    #    The title of the document appears in a <title> element in the <head>
    #    element, as described in Section 6.3.2.
    # 
    #    The title also appears in an <h1> element and follows directly after
    #    the Document Information.  The <h1> element has an "id" attribute
    #    with value "title".
    # 
    #    <h1 id="title">HyperText Markup Language Request For
    #        Comments Format</h1>
    # 
    #    Inside a reference, the title is rendered as an HTML <span> tag with
    #    CSS class "refTitle".  The text is surrounded by quotes inside the
    #    <span>.
    # 
    #    <span class="refTitle">"Tags for Identifying Languages"</span>
    def render_title(self, h, x):
        pp = x.getparent().getparent()
        title = x.text
        if pp.get("quoteTitle") == 'true':
            title = '"%s"' % title
        ascii = x.get('ascii')
        if ascii and not is_script(title, 'Latin'):
            if pp.get("quoteTitle") == 'true':
                ascii = '"%s"' % ascii
        #
        if self.part == 'references':
            if title:
                span = wrap_ascii('span', '', title, ascii, '', classes='refTitle')
                h.append(span)
                return span
        else:
            h1 = build.h1(title, id='title')
            h.append(h1)
            return h1

    # 9.61.  <tr>
    # 
    #    This element is directly rendered as its HTML counterpart.
    render_tr = default_renderer

    # 9.62.  <tt>
    # 
    #    This element is rendered as an HTML <code> element.
    def render_tt(self, h, x):
        hh = add.code(h, x)
        for c in x.getchildren():
            self.render(hh, c)

    # 9.63.  <ul>
    # 
    #    This element is directly rendered as its HTML counterpart.  If the
    #    "spacing" attribute has the value "compact", a CSS class of
    #    "ulCompact" will be added.  If the "empty" attribute has the value
    #    "true", a CSS class of "ulEmpty" will be added.
    def render_ul(self, h, x):
        ul = build.ul()
        p = x.getparent()
        panchor = p.get('anchor')
        classes = h.get('class', '')
        if panchor in ['toc', ]:
            hh = wrap(ul, 'nav', **{'class': panchor})
            classes += ' '+panchor if classes else panchor
        else:
            hh = ul
        h.append(hh)
        if x.get('empty')=='true':
            if not 'ulEmpty' in classes:
                if classes:
                    classes += ' '
                classes += 'ulEmpty' 
        if classes:
            ul.set('class', classes)
        for c in x.getchildren():
            self.render(ul, c)
        return ul

    # RFC 7997
    # 3.4.  Body of the Document
    # 
    #    When the mention of non-ASCII characters is required for correct
    #    protocol operation and understanding, the characters' Unicode
    #    character name or code point MUST be included in the text.
    # 
    #    o  Non-ASCII characters will require identifying the Unicode code
    #       point.
    # 
    #    o  Use of the actual UTF-8 character (e.g., Δ) is encouraged so
    #       that a reader can more easily see what the character is, if their
    #       device can render the text.
    # 
    #    o  The use of the Unicode character names like "INCREMENT" in
    #       addition to the use of Unicode code points is also encouraged.
    #       When used, Unicode character names should be in all capital
    #       letters.
    # 
    #    Examples:
    # 
    #    OLD [RFC7564]:
    # 
    #    However, the problem is made more serious by introducing the full
    #    range of Unicode code points into protocol strings.  For example,
    #    the characters U+13DA U+13A2 U+13B5 U+13AC U+13A2 U+13AC U+13D2 from
    #    the Cherokee block look similar to the ASCII characters  "STPETER" as
    #    they might appear when presented using a "creative" font family.
    # 
    #    NEW/ALLOWED:
    # 
    # However, the problem is made more serious by introducing the full
    # range of Unicode code points into protocol strings.  For example,
    # the characters U+13DA U+13A2 U+13B5 U+13AC U+13A2 U+13AC U+13D2
    # (ᏚᎢᎵᎬᎢᎬᏒ) from the Cherokee block look similar to the ASCII
    # characters "STPETER" as they might appear when presented using a
    # "creative" font family.
    # 
    #    ALSO ACCEPTABLE:
    # 
    # However, the problem is made more serious by introducing the full
    # range of Unicode code points into protocol strings.  For example,
    # the characters "ᏚᎢᎵᎬᎢᎬᏒ" (U+13DA U+13A2 U+13B5 U+13AC U+13A2
    # U+13AC U+13D2) from the Cherokee block look similar to the ASCII
    # characters "STPETER" as they might appear when presented using a
    # "creative" font family.
    # 
    #    Example of proper identification of Unicode characters in an RFC:
    # 
    # Flanagan                Expires October 27, 2016                [Page 6]
    # 
    #  
    # Internet-Draft              non-ASCII in RFCs                 April 2016
    # 
    # 
    #    Acceptable:
    # 
    #    o  Temperature changes in the Temperature Control Protocol are
    #       indicated by the U+2206 character.
    # 
    #    Preferred:
    # 
    #    1.  Temperature changes in the Temperature Control Protocol are
    #        indicated by the U+2206 character ("Δ").
    # 
    #    2.  Temperature changes in the Temperature Control Protocol are
    #        indicated by the U+2206 character (INCREMENT).
    # 
    #    3.  Temperature changes in the Temperature Control Protocol are
    #        indicated by the U+2206 character ("Δ", INCREMENT).
    # 
    #    4.  Temperature changes in the Temperature Control Protocol are
    #        indicated by the U+2206 character (INCREMENT, "Δ").
    # 
    #    5.  Temperature changes in the Temperature Control Protocol are
    #        indicated by the "Delta" character "Δ" (U+2206).
    # 
    #    6.  Temperature changes in the Temperature Control Protocol are
    #        indicated by the character "Δ" (INCREMENT, U+2206).
    def render_u(self, h, x):
        try:
            text = expand_unicode_element(x)
        except (RuntimeError, ValueError) as e:
            self.err(x, e)
            text = ''
        anchor = x.get('anchor')
        xref = self.root.find('.//xref[@target="%s"]'%anchor) if anchor else None
        if xref != None:
            # render only literal here
            text = x.text
        span = add.span(h, None, text, classes="unicode", id=anchor)
        span.tail = x.tail
        return span
        
    # 9.64.  <uri>
    # 
    #    This element is rendered as an HTML <div> containing the string
    #    "URI:" and an HTML <a> element with the "href" attribute set to the
    #    linked URI, CSS class of "url" (note that the value is "url", not
    #    "uri" as one might expect), and the contents set to the linked URI.
    # 
    #    <div>URI:
    #      <a href="http://www.example.com"
    #         class="url">http://www.example.com</a>
    #    </div>
    def render_uri(self, h, x):
        if not x.text:
            return None
        value = x.text.strip()
        cls = 'url'
        div = add.div(h, None,
                    build.span("URI:"), '\n',
                    build.a(value, href=value, classes=cls),
                    classes=cls,
                )
        return div

    # 9.65.  <workgroup>
    # 
    #    This element does not add any direct output to HTML.
    render_workgroup = null_renderer    # handled in render_rfc, when rendering the page top for drafts

    # 9.66.  <xref>
    # 
    #    This element is rendered as an HTML <a> element containing an
    #    appropriate local link as the "href" attribute.  The value of the
    #    "href" attribute is taken from the "target" attribute, prepended by
    #    "#".  The <a> element generated will have class "xref".  The contents
    #    of the <a> element are the value of the "derivedContent" attribute.
    #    If the "format" attribute has the value "default", and the "target"
    #    attribute points to a <reference> or <referencegroup> element, then
    #    the generated <a> element is surrounded by square brackets in the
    #    output.
    # 
    #    <a class="xref" href="#target">Table 2</a>
    # 
    #    or
    # 
    #    [<a class="xref" href="#RFC1234">RFC1234</a>]
    # 
    def render_xref(self, h, x):
        # possible attributes:
        target  = x.get('target')
        #pageno  = x.get('pageno')
        #format  = x.get('format')
        section = x.get('section')
        relative= x.get('relative')
        #sformat  = x.get('sectionFormat')
        reftext = x.get('derivedContent', '')
        in_name = len(list(x.iterancestors('name'))) > 0
        if reftext is None:
            self.die(x, "Found an <%s> without derivedContent: %s" % (x.tag, lxml.etree.tostring(x),))
        if not (section or relative):
            # plain xref
            if in_name:
                hh = build.em(reftext, classes="xref")
            else:
                if reftext:
                    a = build.a(reftext, href='#%s'%target, classes='xref')
                    if target in self.refname_mapping:
                        if x.text and x.text.strip() and x.text.strip() != reftext:
                            aa = build.a(x.text, href='#%s'%target, classes='xref')
                            hh = build.span(aa, ' [', a, ']')
                        else:
                            hh = build.span('[', a, ']')
                    else:
                        if x.text and x.text.strip() and x.text.strip() != reftext:
                            aa = build.a(x.text, href='#%s'%target, classes='xref')
                            hh = build.span(aa, ' (', a, ')')
                        else:
                            hh = a
                else:
                    a = build.a(x.text or '', href='#%s'%target, classes='xref')
                    hh = a
            hh.tail = x.tail
            h.append(hh)
            return hh
        else:
            link    = x.get('derivedLink')
            format  = x.get('sectionFormat')
            # 9.44.1.  displayFormat='of'
            # 
            #    The output is an <a class='relref'> HTML tag, with contents of
            #    "Section " and the value of the "section" attribute.  This is
            #    followed by the word "of" (surrounded by whitespace).  This is
            #    followed by the <a class='xref'> HTML tag (surrounded by square
            #    brackets).
            # 
            #    For example, with an input of:
            # 
            #    See <relref section="2.3" target="RFC9999" displayFormat="of"
            #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"/>
            #    for an overview.
            # 
            #    The HTML generated will be:
            # 
            #    See <a class="relref"
            #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section
            #    2.3</a> of [<a class="xref" href="#RFC9999">RFC9999</a>]
            #    for an overview.
            if format == 'of':
                span = add.span(h, None,
                    build.a('Section %s'%section, href=link, classes='relref'),
                    ' of [',
                    build.a(reftext, href='#%s'%target, classes='xref'),
                    ']',
                )
                return span

            # 9.44.2.  displayFormat='comma'
            # 
            #    The output is an <a class='xref'> HTML tag (wrapped by square
            #    brackets), followed by a comma (","), followed by whitespace,
            #    followed by an <a class='relref'> HTML tag, with contents of
            #    "Section " and the value of the "section" attribute.
            # 
            #    For example, with an input of:
            # 
            #    See <relref section="2.3" target="RFC9999" displayFormat="comma"
            #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"/>,
            #    for an overview.
            # 
            #    The HTML generated will be:
            # 
            #    See [<a class="xref" href="#RFC9999">RFC9999</a>], <a class="relref"
            #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section 2.3</a>,
            #    for an overview.
            elif format == 'comma':
                span = add.span(h, None,
                    '[',
                    build.a(reftext, href='#%s'%target, classes='xref'),
                    '], ',
                    build.a('Section %s'%section, href=link, classes='relref'),
                )
                return span


            # 9.44.3.  displayFormat='parens'
            # 
            #    The output is an <a> element with "href" attribute whose value is the
            #    value of the "target" attribute prepended by "#", and whose content
            #    is the value of the "target" attribute; the entire element is wrapped
            #    in square brackets.  This is followed by whitespace.  This is
            #    followed by an <a> element whose "href" attribute is the value of the
            #    "derivedLink" attribute and whose content is the value of the
            #    "derivedRemoteContent" attribute; the entire element is wrapped in
            #    parentheses.
            # 
            #    For example, if Section 2.3 of RFC 9999 has the title "Protocol
            #    Overview", for an input of:
            # 
            #    See <relref section="2.3" target="RFC9999" displayFormat="parens"
            #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"
            #    derivedRemoteContent="Section 2.3"/> for an overview.
            # 
            #    The HTML generated will be:
            # 
            #    See [<a class="relref" href="#RFC9999">RFC9999</a>]
            #    (<a class="relref"
            #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section
            #    2.3</a>) for an overview.
            elif format == 'parens':
                span = add.span(h, None,
                    '[',
                    build.a(reftext, href='#%s'%target, classes='xref'),
                    '] (',
                    build.a('Section %s'%section, href=link, classes='relref'),
                    ')',
                )
                return span

            # 
            # 9.44.4.  displayFormat='bare'
            # 
            #    The output is an <a> element whose "href" attribute is the value of
            #    the "derivedLink" attribute and whose content is the value of the
            #    "derivedRemoteContent" attribute.
            # 
            #    For this input:
            # 
            #    See <relref section="2.3" target="RFC9999" displayFormat="bare"
            #    derivedLink="http://www.rfc-editor.org/info/rfc9999#s-2.3"
            #    derivedRemoteContent="Section 2.3"/> and ...
            # 
            #    The HTML generated will be:
            # 
            #    See <a class="relref"
            #    href="http://www.rfc-editor.org/info/rfc9999#s-2.3">Section
            #    2.3</a> and ...
            elif format == 'bare':
                span = add.span(h, None,
                    build.a('Section %s'%section, href=link, classes='relref'),
                )
                return span
            else:
                self.err(x, 'Unexpected value combination: section: %s  relative: %s  format: %s' %(section, relative, format))


    # --------------------------------------------------------------------------
    # Post processing
    def post_process(self, h):
        for x in h.iter():
            if x.text and x.text.strip() and '\u2028' in x.text:
                parts = x.text.split('\u2028')
                x.text = parts[0]
                for t in parts[1:]:
                    br = build.br()
                    br.tail = t
                    x.append( br )
            if x.tail and x.tail.strip() and '\u2028' in x.tail:
                p = x.getparent()
                i = p.index(x)+1
                parts = x.tail.split('\u2028')
                x.tail = parts[0]
                for t in parts[1:]:
                    br = build.br()
                    br.tail = t
                    p.insert(br, i)
                    i += 1
        return h

    # --- class variables ------------------------------------------------------

    element_tags = [
        'abstract',
        'address',
        'annotation',
        'artset',
        'artwork',
        'aside',
        'author',
        'back',
        'bcp14',
        'blockquote',
        'boilerplate',
        'br',
        'city',
        'code',
        'country',
        'cref',
        'date',
        'dd',
        'displayreference',
        'dl',
        'dt',
        'em',
        'email',
        'eref',
        'figure',
        'front',
        'iref',
        'li',
        'link',
        'middle',
        'name',
        'note',
        'ol',
        'organization',
        'phone',
        'postal',
        'postalLine',
        'refcontent',
        'reference',
        'referencegroup',
        'references',
        'region',
        'relref',
        'rfc',
        'section',
        'seriesInfo',
        'sourcecode',
        'street',
        'strong',
        'sub',
        'sup',
        't',
        'table',
        'tbody',
        'td',
        'tfoot',
        'th',
        'thead',
        'title',
        'tr',
        'tt',
        'ul',
        'uri',
        'xref',
    ]
    deprecated_element_tags = [
        'list',
        'spanx',
        'vspace',
        'c',
        'texttable',
        'ttcol',
        'facsimile',
        'format',
        'preamble',
        'postamble',
    ]
    unused_front_element_renderers = [
        'area',
        'keyword',
        'workgroup',
    ]
    all_element_tags = element_tags + deprecated_element_tags + unused_front_element_renderers
    deprecated_attributes = [
        # element, attrbute
        ('figure', 'align'),
        ('section', 'title'),
        ('note', 'title'),
        ('figure', 'title'),
        ('references', 'title'),
        ('texttable', 'title'),
        ('figure', 'src'),
        ('artwork', 'xml:space'),
        ('artwork', 'height'),
        ('artwork', 'width'),
        ('figure', 'height'),
        ('figure', 'width'),
        ('xref', 'pageno'),
    ]
