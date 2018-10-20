# Copyright The IETF Trust 2018, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import copy
import datetime
#import inspect
import lxml
import os
import re
#import sys
#import six

from io import open
from lxml.html.builder import E as build
#from collections import namedtuple

try:
    import debug
    debug.debug = True
except ImportError:
    pass

import xml2rfc
from xml2rfc import log, strings, util as utils, uniscripts
from xml2rfc.writers.base import default_options, BaseV3Writer
from xml2rfc.util.name import full_author_name, full_org_name

#from xml2rfc import utils

# ------------------------------------------------------------------------------

seen = set()

def wrap(e, tag, **kwargs):
    w = build(tag, **kwargs)
    w.append(e)
    return w

# ------------------------------------------------------------------------------

class HtmlWriter(BaseV3Writer):

    def __init__(self, xmlrfc, quiet=None, options=default_options, date=datetime.date.today()):
        super(HtmlWriter, self).__init__(xmlrfc, quiet=quiet, options=options, date=date)

    def write(self, filename):
        self.filename = filename

        """Write the document to a file """
        # get rid of comments so we can ignore them in the rest of the code
        for c in self.tree.xpath('.//comment()'):
            p = c.getparent()
            p.remove(c)
        html = self.render(None, self.root)
        html = self.post_process(html)

        if self.errors:
            log.write("Not creating output file due to errors (see above)")
            return

        # Use lxml's built-in serialization
        with open(filename, 'w', encoding='utf-8') as file:

            # 6.1.  DOCTYPE
            # 
            #    The DOCTYPE of the document is "html", which declares that the
            #    document is compliant with HTML5.  The document will start with
            #    exactly this string:
            # 
            #    <!DOCTYPE html>


            text = lxml.etree.tostring(html, method='html', encoding='unicode', pretty_print=True, doctype="<!DOCTYPE html>")
            # Required by RFC7992:
            text = re.sub(r'[\x00-\x09\x0B-\x1F]+', ' ', text)

            file.write(text)

        if not self.options.quiet:
            log.write('Created file', filename)


    def render(self, h, e, **kw):
        kwargs = copy.deepcopy(kw)
        func_name = "render_%s" % (e.tag.lower(),)
        func = getattr(self, func_name, self.default_renderer)
        if func == self.default_renderer:
            if e.tag in self.__class__.deprecated_element_tags:
                self.warn(e, "Was asked to render a deprecated element: <%s>", (e.tag, ))
            elif not e.tag in seen:
                self.warn(e, "No renderer for <%s> found" % (e.tag, ))
                seen.add(e.tag)
        res = func(h, e, **kwargs)
        return res


    def default_renderer(self, h, e, **kwargs):
        hh = build(e.tag, e.text or '')
        hh.tail = e.tail
        for c in e.getchildren():
            self.render(hh, c, **kwargs)
        h.append(hh)

    def inner_text_renderer(self, h, e, **kwargs):
        h.text = e.text
        for c in e.getchildren():
            self.render(h, c, **kwargs)
        h.tail = e.tail

    # --- element rendering functions ------------------------------------------

    def render_rfc(self, h, e, **kwargs):
        self.part = e.tag
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

        classes = ' '.join( i.get('name') for i in e.xpath('./front/seriesInfo') )
        #
        html = h if h != None else build.html({'class':classes}, lang='en')

    # 6.3.  <head> Element
    # 
    #    The root <html> will contain a <head> element that contains the
    #    following elements, as needed.

        head = build.head()
        html.append(head)

    # 6.3.1.  Charset Declaration
    # 
    #    In order to be correctly processed by browsers that load the HTML
    #    using a mechanism that does not provide a valid content-type or
    #    charset (such as from a local file system using a "file:" URL), the
    #    HTML <head> element contains a <meta> element, whose "charset"
    #    attribute value is "utf-8":
    # 
    #    <meta charset="utf-8">

        head.append( build.meta(charset='utf-8') )

        # This is not required
        meta = build.meta()
        meta.set('http-equiv', 'Content-Type')
        meta.set('content', 'text/html; charset=utf-8')
        head.append(meta)

    # 6.3.2.  Document Title
    # 
    #    The contents of the <title> element from the XML source will be
    #    placed inside an HTML <title> element in the header.

        title = e.find('./front/title').text
        head.append( build.title(title) )

    # 6.3.3.  Document Metadata
    # 
    #    The following <meta> elements will be included:
    # 
    #    o  author - one each for the each of the "fullname"s and
    #       "asciiFullname"s of all of the <author>s from the <front> of the
    #       XML source

        for a in e.xpath('./front/author'):
            name = full_author_name(a)
            if not name:
                name = full_org_name(a)
            head.append( build.meta(name='author', content=name ))

    #    o  description - the <abstract> from the XML source

        abstract = ' '.join(e.find('./front/abstract').itertext())
        head.append( build.meta(name='description', content=abstract) )

    #    o  generator - the name and version number of the software used to
    #       create the HTML

        generator = "%s %s" % (xml2rfc.NAME, xml2rfc.__version__)
        head.append( build.meta(name='generator', content=generator))
        
    #    o  keywords - comma-separated <keyword>s from the XML source

        for keyword in e.xpath('./front/keyword'):
            head.append( build.meta(name='keyword', content=keyword.text))

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

        head.append( build.link(rel='alternate', type='application/rfc+xml', href=self.xmlrfc.source))

    # 6.3.5.  Link to License
    # 
    #    The <head> element contains a <link> tag, with "rel" attribute of
    #    "license" and "href" attribute pointing to the an appropriate
    #    copyright license for the document.
    # 
    #    <link rel="license"
    #       href="https://trustee.ietf.org/trust-legal-provisions.html">

        head.append( build.link(rel='license', href="https://trustee.ietf.org/license-info/IETF-TLP-5.htm"))

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
            head.append(build.link(rel="stylesheet", href="xml2rfc.css", type="text/css"))
        else:
            style = build.style(css, type="text/css")
            head.append(style)
        head.append(build.link(rel="stylesheet", href="rfc-local.css", type="text/css"))

    # 6.3.7.  Links
    # 
    #    Each <link> element from the XML source is copied into the HTML
    #    header.  Note: the HTML <link> element does not include a closing
    #    slash.

        for link in e.xpath('./link'):
            head.append(link)

        body = build.body()
        html.append(body)

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

        if False:
            # Is this pure placeholder, or does it need data from the document?
            body.append(
                build.table({'class': 'ears'},
                    build.thead(
                        build.tr(
                            build.td({'class': 'left'}, "Left"),
                            build.td({'class': 'middle'}, "Middle"),
                            build.td({'class': 'right'}, "Right"),
                        ),
                    ),
                    build.tfoot(
                        build.tr(
                            build.td({'class': 'left'}, "Left"),
                            build.td({'class': 'middle'}, "Middle"),
                            build.td({'class': 'right'}, "[Page]"),
                        ),
                    ),
                )
            )

        for c in [ e.find('./front'), e.find('./middle'), e.find('./back'), ]:
            self.part = c.tag
            self.render(body, c, **kwargs)

        jsin  = self.options.css or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'xml2rfc.js')
        with open(jsin, encoding='utf-8') as f:
            js = f.read()
        body.append( build.script(js, type='text/javascript'))

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

    def render_abstract(self, h, e, **kwargs):
        if self.part != 'front':
            return
        section = build.section(id=e.get('pn'))
        section.append( build.h2( build.a('Abstract', {'class':'selfRef'}, href="#abstract"), id="abstract"))
        for c in e.getchildren():
            self.render(section, c, **kwargs)
        h.append(section)

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
    # 
    # 9.3.  <annotation>
    # 
    #    This element is rendered as the text ", " (a comma and a space)
    #    followed by a <span> of class "annotation" at the end of a
    #    <reference> element, the <span> containing appropriately transformed
    #    elements from the children of the <annotation> tag.
    # 
    #     <span class="annotation">Some <em>thing</em>.</span>
    # 
    # 9.4.  <area>
    # 
    #    Not currently rendered to HTML.
    # 
    # 9.5.  <artwork>
    # 
    #    Artwork can consist of either inline text or SVG.  If the artwork is
    #    not inside a <figure> element, a pilcrow (Section 5.2) is included.
    #    Inside a <figure> element, the figure title serves the purpose of the
    #    pilcrow.  If the "align" attribute has the value "right", the CSS
    #    class "alignRight" will be added.  If the "align" attribute has the
    #    value "center", the CSS class "alignCenter" will be added.
    # 
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
    # 
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
    # 
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
    # 
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
    # 
    # 9.7.  <author>
    # 
    #    The <author> element is used in several places in the output.
    #    Different rendering is used for each.
    def render_author(self, h, e, **kwargs):

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
            name = utils.name.short_author_name(e)
            aname = utils.name.short_author_ascii_name(e)
            
            def wrap_nonascii(e, name, ascii):
                if uniscripts.is_script(name, 'Latin'):
                    div = build.div(name)
                    if e.get('role') == 'editor':
                        div.append( build.span({'class': 'editor'}, "Ed.") )
                else:
                    div = build.div()
                    div.append( build.span({'class': 'non-ascii'}, name))
                    if e.get('role') == 'editor':
                        div.append( build.span({'class': 'editor'}, "Ed.") )
                    div.append( build.span({'class': 'ascii'}, '(%s)' % ascii))
                return div
                
            div = build.div({'class': 'author'})
            if name:
                ndiv = wrap_nonascii(e, name, aname)
                ndiv.set('class', 'author-name')
                div.append(ndiv)

            org  = utils.name.short_org_name(e)
            aorg = utils.name.short_org_ascii_name(e)
            if org:
                odiv = wrap_nonascii(e.find('organization'), org, aorg)
                odiv.set('class', 'org')
                div.append(odiv)
            h.append(div)

    # 9.7.2.  Authors of This Document
    # 
    #    As seen in the Authors' Addresses section, at the end of the HTML,
    #    each document author is rendered into an HTML <address> element with
    #    the CSS class "vcard".
    # 
    #    The HTML <address> element will contain an HTML <div> with CSS class
    #    "nameRole".  That div will contain an HTML <span> element with CSS
    #    class "fn" containing the value of the "fullname" attribute of the
    # 
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
            self.default_renderer(h, e, **kwargs)

    # 
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
            self.default_renderer(h, e, **kwargs)

        else:
            self.err(e, "Did not expect to be asked to render <%s> while in <%s>" % (e.tag, e.getparent().tag))

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
    def render_back(self, h, e, **kwargs):
        self.default_renderer(h, e, **kwargs)


    # 9.9.  <bcp14>
    # 
    #    This element marks up words like MUST and SHOULD [BCP14] with an HTML
    #    <span> element with the CSS class "bcp14".
    # 
    #    You <span class="bcp14">MUST</span> be joking.
    # 
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
    # 
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
    def render_boilerplate(self, h, e, **kwargs):
        for c in e.getchildren():
            self.render(h, c, **kwargs)

    # 9.12.  <br>
    # 
    #    This element is directly rendered as its HTML counterpart.  Note: in
    #    HTML, <br> does not have a closing slash.
    ## Removed from schema

    # 
    # 9.13.  <city>
    # 
    #    This element is rendered as a <span> element with CSS class
    #    "locality".
    # 
    #    <span class="locality">Guilford</span>
    # 
    # 9.14.  <code>
    # 
    #    This element is rendered as a <span> element with CSS class "postal-
    #    code".
    # 
    #    <span class="postal-code">GU16 7HF<span>
    # 
    # 9.15.  <country>
    # 
    #    This element is rendered as a <div> element with CSS class "country-
    #    name".
    # 
    #    <div class="country-name">England</div>
    # 
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
    # 
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
    # 
    # 9.18.  <dd>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.19.  <displayreference>
    # 
    #    This element does not affect the HTML output, but it is used in the
    #    generation of the <reference>, <referencegroup>, <relref>, and <xref>
    #    elements.
    # 
    # 9.20.  <dl>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    #    If the hanging attribute is "false", add the "dlParallel" class, else
    #    add the "dlHanging" class.
    # 
    #    If the spacing attribute is "compact", add the "dlCompact" class.
    def render_dl(self, h, e, **kwargs):
        classes = kwargs.get('classes', [])
        #
        dl = build.dl()
        newline = e.get('newline')
        spacing = e.get('spacing')
        classes = []
        if   newline == 'true':
            classes.append('dlNewline')
        elif newline == 'false':
            classes.append('dlParallel')
        if   spacing == 'compact':
            classes.append('dlCompact')
        dl.set('class', ' '.join(classes))
        for c in e.getchildren():
            self.render(dl, c, **kwargs)

    # 9.21.  <dt>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.22.  <em>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
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
    # 
    # 9.24.  <eref>
    # 
    #    This element is rendered as an HTML <a> element, with the "href"
    #    attribute set to the value of the "target" attribute and the CSS
    #    class of "eref".
    # 
    #    <a href="https://..." class="eref">the text</a>
    # 
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
    # 
    # 9.26.  <front>
    # 
    #    See "Document Information" (Section 6.5) for information on this
    #    element.
    def render_front(self, h, e, **kwargs):
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

            dl = build.dl(id='identifiers')
            h.append( build.div({'class': 'document-information'}, dl ))
            if self.options.rfc:
                # Stream
                stream = self.root.get('submissionType')
                dl.append( build.dt('Stream:'))
                dl.append( build.dd({'class':'stream'}, strings.stream_name[stream]))
                # Series info
                for series in e.xpath('./seriesInfo'):
                    dl.append( build.dt('%s:' % series.get('name')))
                    dl.append(build.dd({'class':'series'}, series.get('value')))

                for section in ['obsoletes', 'updates']:
                    items = self.root.get(section)
                    if items:
                        dl.append( build.dt('%s:'%section.capitalize()) )
                        dd = build.dd({'class': section})
                        for num in items.split(','):
                            num = num.strip()
                            a = build.a(num, {'class':'eref'}, href=os.path.join(self.options.rfc_base_url, 'rfc%s.txt'%num))
                            a.tail = ' '
                            dd.append(a)
                        dl.append( dd )

                category = self.root.get('category', '')
                if category:
                    dl.append( build.dt('Category:'))
                    dl.append( build.dd({'class': category.lower()}, strings.category_name[category] ))
                dl.append( build.dt('ISSN:'))
                dl.append( build.dd({'class':'issn'}, '2070-1721'))

            else:
                # Workgroup
                for wg in e.xpath('./workgroup'):
                    dl.append( build.dt('Workgroup:'))
                    dl.append( build.dd({'class':'workgroup'}, wg))
                for series in e.xpath('./seriesInfo'):
                    dl.append( build.dt('%s:' % series.get('name')))
                    dl.append( build.dd({'class':'series'}, series.get('value')))

                for section in ['obsoletes', 'updates']:
                    items = self.root.get(section)
                    if items:
                        dl.append( build.dt('%s:'%section.capitalize()) )
                        dd = build.dd({'class': section})
                        for num in items.split(','):
                            num = num.strip()
                            a = build.a(num, {'class':'eref'}, href=os.path.join(self.options.rfc_base_url, 'rfc%s.txt'%num))
                            a.tail = ' '
                            dd.append(a)
                        dl.append( dd )

                # Intended category
                category = self.root.get('category', '')
                if category:
                    dl.append( build.dt('Intended Status:'))
                    dl.append( build.dd({'class': category.lower()}, strings.category_name[category] ))
                # Expiry date
                exp = utils.date.get_expiry_date(self.root, self.date)
                dl.append( build.dt('Expires'))
                dl.append( build.dd({'class': 'date'}, utils.date.format_date(exp.year, exp.month, exp.day, self.options.legacy_date_format) ))

            authors = e.xpath('./author')
            dl.append( build.dt('Authors:' if len(authors)>1 else 'Author:') )
            dd = build.dd({'class':'authors'})
            dl.append(dd)
            for a in authors:
                self.render(dd, a, **kwargs)

            for c in e.iterchildren('title', 'abstract', 'note', 'boilerplate'):
                self.render(h, c, **kwargs)

        elif self.part == 'references':
            self.default_renderer(h, e, **kwargs)
        else:
            self.err(e, "Did not expect to be asked to render <%s> while in <%s>" % (e.tag, e.getparent().tag))
            

    # 9.27.  <iref>
    # 
    #    This element is rendered as an empty <> tag of class "iref", with an
    #    "id" attribute consisting of the <iref> element's "irefid" attribute:
    # 
    #    <span class="iref" id="s-Paragraphs-first-1"/>
    # 
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
    def render_li(self, h, e, **kwargs):
        li = build.li()
        classes = h.get('class')
        if classes:
            li.set('class', classes)
        h.append(li)
        self.inner_text_renderer(li, e, **kwargs)




    # 9.30.  <link>
    # 
    #    This element is rendered as its HTML counterpart, in the HTML header.
    # 
    # 9.31.  <middle>
    # 
    #    This element does not add any direct output to HTML.

    def render_middle(self, h, e, **kwargs):
        self.default_renderer(h, e, **kwargs)


    # 9.32.  <name>
    # 
    #    This element is never rendered directly; it is only rendered when
    #    considering a parent element, such as <figure>, <references>,
    #    <section>, or <table>.
    def render_name(self, s, e, **kwargs):
        p = e.getparent()
        if p.tag in [ 'note', 'section', 'references' ]:
            pn = p.get('pn')
            prefix, number = pn.split('-', 1)
            number += '.'
            if re.search(r'^[a-z]', number):
                __, num = number.split('.', 1)
            else:
                num = number
            level = min([6, len(num.split('.')) ])
            tag = 'h%d' % level
            h = build(tag, id=e.get('slugifiedName'))
            s.append(h)
            #
            numbered = p.get('numbered')
            if numbered == 'true':
                a_number = build.a(number, {'class': 'selfRef'}, href='#%s'%pn)
                h.append( a_number)
            a_title = build.a({'class': 'selfRef'})
            h.append(a_title)
            anchor = p.get('anchor')
            if anchor:
                a_title.set('href', '#%s'%anchor)
            self.inner_text_renderer(a_title, e, **kwargs)
        else:
            self.warn(e, "Did not expect to be asked to render <%s> while in <%s>" % (e.tag, e.getparent().tag))
            self.default_renderer(s, e, **kwargs)

    # 
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
    # 
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
    # 
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
    # 
    # 9.34.2.  Standard Styles
    # 
    #    For all other styles, an <ol> tag is emitted, with any "style"
    #    attribute turned into the equivalent HTML attribute.
    # 
    #    <ol class="compact" type="I" start="18">
    #      <li>Wheels on a big rig</li>
    #    </ol>
    # 
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
    # 
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
    # 
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
    # 
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
    # 
    # 9.39.  <refcontent>
    # 
    #    This element renders as an HTML <span> with CSS class "refContent".
    # 
    #    <span class="refContent">Self-published pamphlet</span>
    # 
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
    # 
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
    # 
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
    def render_references(self, h, e, **kwargs):
        self.part = e.tag
        self.default_renderer(h, e, **kwargs)

    # 
    # 9.43.  <region>
    # 
    #    This element is rendered as a <span> tag with CSS class "region".
    # 
    #    <span class="region">Colorado</span>
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
    def render_relref(self, h, e, **kwargs):
        self.render_xref(h, e, **kwargs)


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
    # 
    # 9.45.  <rfc>
    # 
    #    Various attributes of this element are represented in different parts
    #    of the HTML document.
    # 
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
    def render_section(self, h, e, **kwargs):
        pn = e.get('pn')
        section = build.section(id=pn)
        #
        anchor = e.get('anchor')
        if anchor:
            div = build.div(id=anchor)
            section.append(div)
            hh = div
        else:
            hh = section
        #
        for c in e.getchildren():
            self.render(hh, c, **kwargs)
        h.append(section)

    # 9.47.  <seriesInfo>
    # 
    #    This element is rendered in an HTML <span> element with CSS name
    #    "seriesInfo".
    # 
    #    <span class="seriesInfo">RFC 5646</span>
    # 
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
    # 
    # 9.49.  <street>
    # 
    #    This element renders as an HTML <div> element with CSS class "street-
    #    address".
    # 
    #    <div class="street-address">1899 Wynkoop St, Suite 600</div>
    # 
    # 9.50.  <strong>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.51.  <sub>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.52.  <sup>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.53.  <t>
    # 
    #    This element is rendered as an HTML <p> element.  A pilcrow
    #    (Section 5.2) is included.
    # 
    #    <p id="s-1-1">A paragraph.
    #      <a href="#s-1-1" class="pilcrow">&para;</a></p>
    def render_t(self, h, e, **kwargs):
        id = e.get('anchor') or e.get('pn')
        if id is None:
            debug.show('h')
            debug.show('lxml.etree.tostring(h)')
            debug.show('e')
            debug.show('e.text')
        if (e.tail and e.tail.strip()) or h.tag not in ['li', 'p', ] :
            p = build.p(e.text or '', id=id)
            p.tail = e.tail
            h.append(p)
            hh = p
        else:
            hh = h
        for c in e.getchildren():
            self.render(hh, c, **kwargs)


    # 
    # 9.54.  <table>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.55.  <tbody>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.56.  <td>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.57.  <tfoot>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.58.  <th>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.59.  <thead>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
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
    def render_title(self, h, e, **kwargs):
        pp = e.getparent().getparent()
        title = e.text
        if self.part == 'references':
            if pp.get("quoteTitle") == 'true':
                title = '"%s"' % title
            span = build.span({'class':'refTitle'}, title)
            h.append(span)
        else:
            h1 = build.h1(title, id='title')
            h.append(h1)

    # 9.61.  <tr>
    # 
    #    This element is directly rendered as its HTML counterpart.
    # 
    # 9.62.  <tt>
    # 
    #    This element is rendered as an HTML <code> element.
    # 
    # 9.63.  <ul>
    # 
    #    This element is directly rendered as its HTML counterpart.  If the
    #    "spacing" attribute has the value "compact", a CSS class of
    #    "ulCompact" will be added.  If the "empty" attribute has the value
    #    "true", a CSS class of "ulEmpty" will be added.
    def render_ul(self, h, e, **kwargs):
        ul = build.ul()
        p = e.getparent()
        panchor = p.get('anchor')
        classes = h.get('class', '')
        if panchor in ['toc', ]:
            hh = wrap(ul, 'nav', **{'class': panchor})
            classes += ' '+panchor if classes else panchor
        else:
            hh = ul
        h.append(hh)
        if classes:
            ul.set('class', classes)
        for c in e.getchildren():
            self.render(ul, c, **kwargs)

    # 
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
    # 
    # 9.65.  <workgroup>
    # 
    #    This element does not add any direct output to HTML.
    # 
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
    def render_xref(self, h, e, **kwargs):
        # possible attributes:
        target  = e.get('target')
        #pageno  = e.get('pageno')
        #format  = e.get('format')
        section = e.get('section')
        relative= e.get('relative')
        #link    = e.get('derivedLink')
        #sformat  = e.get('sectionFormat')
        content = e.get('derivedContent', '')
        if content is None:
            self.die(e, "Found an <%s> without derivedContent: %s" % (e.tag, lxml.etree.tostring(e),))
        if not (section or relative):
            # plain xref
            a = build.a(content, {'class': 'xref'}, href='#%s'%target)
            a.tail = ''
            if target in self.refname_mapping:
                hh = build.span('[', a, ']', e.tail or '')
            else:
                a.tail = e.tail
                hh = a
            h.append(hh)
        
            
    # --------------------------------------------------------------------------
    # Post processing
    def post_process(self, h):
        for e in h.iter():
            if e.text and e.text.strip() and '\u2028' in e.text:
                parts = e.text.split('\u2028')
                e.text = parts[0]
                for t in parts[1:]:
                    br = build.br()
                    br.tail = t
                    e.append( br )
            if e.tail and e.tail.strip() and '\u2028' in e.tail:
                p = e.getparent()
                i = p.index(e)+1
                parts = e.tail.split('\u2028')
                e.tail = parts[0]
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
