#!/usr/bin/env python

import copy
import difflib
import lxml
import re
import unittest
import xml2rfc
import xml2rfc.utils

from xml2rfc.boilerplate_rfc_7841 import boilerplate_rfc_status_of_memo
from xml2rfc.walkpdf import xmldoc
from xml2rfc.writers.base import default_options, BaseV3Writer, RfcWriterError
from xml2rfc.writers.text import MAX_WIDTH

try:
    from xml2rfc import debug
    assert debug
except ImportError:
    pass


# Set up options before declaring classes - some are used during class construction.
options_for_xmlrfcparser = dict()
def _load_environment():
    from os import environ
    cache_path =  environ.get('IETF_TEST_CACHE_PATH', None)
    if cache_path:
        options_for_xmlrfcparser['cache_path'] = cache_path


default_options.allow_local_file_access = True
_load_environment()


def arrstrip(arr):
    """ Strip beginning and end blanklines of an array """
    if not arr[0]: arr.pop(0)
    if not arr[-1]: arr.pop()
    return arr


def diff_test(case, valid, test, failpath, format):
    """ Compare two strings.  If not equal, fail with a useful diff and save
        second string to a file.
    """
    # The following 2 lines does the right thing for both python 2.x and 3.x
    test  = str(test)
    valid = str(valid)
    # replace the current version with something static, if present
    test  =  str(test.replace(xml2rfc.__version__, 'N.N.N'))
    validarr = [line.rstrip() for line in valid.splitlines()]
    testarr = [line.rstrip() for line in test.splitlines()]
    if testarr != validarr:
        diff = difflib.ndiff(validarr, testarr)
        fh = open(failpath, 'w')
        fh.write(test)
        fh.close()
        case.fail("Output doesn't match for %s, file saved to %s.\nDIFF:\n%s" % (format, failpath, '\n'.join(diff)))

def strip_formatting_whitespace(text):
    """ We use non-breaking space, non-breaking hyphen
        internally for formattin purposes - they need to be cleaned out
    """
    return text.replace(u'\u00A0', ' ').replace(u'\u2011', '-').replace(u'\uE060', '')

class XmlRfcDummy():
    """ Dummy rfc used for test fixtures """
    def __init__(self):
        self.pis = {
            "artworkdelimiter":	None,
            "artworklines":	"0",
            "authorship":	"yes",
            "autobreaks":	"yes",
            "background":	"" ,
            "colonspace":	"no" ,
            "comments":		"no" ,
            "docmapping":	"no",
            "editing":		"no",
            #"emoticonic":	"no",
            #"footer":		Unset
            "figurecount":      "no",
            #"header":		Unset
            "inline":		"no",
            #"iprnotified":	"no",
            "linkmailto":	"yes",
            #"linefile":	Unset
            #"needLines":       Unset
            "multiple-initials":"no",
            #"notedraftinprogress": "yes",
            "orphanlimit":      "2",
            "private":		"",
            "refparent":	"References",
            "rfcedstyle":	"no",
            #"rfcprocack":	"no",
            "sectionorphan":    "4",
            #"slides":		"no",
            "sortrefs":		"yes",  # different from default
            #"strict":		"no",
            "symrefs":		"yes",
            "tablecount":       "no",
            "text-list-symbols": "o*+-",
            "toc":		"no",
            "tocappendix":	"yes",
            "tocdepth":		"3",
            "tocindent":	"yes",
            "tocnarrow":	"yes",
            #"tocompact":	"yes",
            "tocpagebreak":	"no",
            "topblock":		"yes",
            #"typeout":		Unset
            #"useobject":	"no" ,
            "widowlimit":       "2",
        }
        self.pis["compact"] = self.pis["rfcedstyle"]
        self.pis["subcompact"] = self.pis["compact"]

    def getroot(self):
        return lxml.etree.Element('rfc')

    def getpis(self):
        return self.pis

    def parse_pi(self, pi):
        if pi.text:
            # Split text in the format 'key="val"'
            chunks = re.split(r'=[\'"]([^\'"]*)[\'"]', pi.text)
            # Create pairs from this flat list, discard last element if odd
            tmp_dict = dict(zip(chunks[::2], chunks[1::2]))
            for key, val in tmp_dict.items():
                # Update main PI state
                self.pis[key] = val
            # Return the new values added

def html_post_rendering(text):
    return text.encode('ascii', 'xmlcharrefreplace').decode('ascii')

output_format = [
    {
        "ext": "txt",
        "spacefix": xml2rfc.utils.formatXmlWhitespace,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "slashfix": xml2rfc.utils.safeTagSlashedWords,
        "writer": xml2rfc.PaginatedTextRfcWriter,
        "postrendering": lambda x: x,
        "postprocesslines": "post_process_lines",
    },
    {
        "ext": "raw.txt",
        "spacefix": xml2rfc.utils.formatXmlWhitespace,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "slashfix": xml2rfc.utils.safeTagSlashedWords,
        "writer": xml2rfc.RawTextRfcWriter,
        "postrendering": lambda x: x,
        "postprocesslines": "post_process_lines",
    },
    {
        "ext": "nroff",
        "spacefix": xml2rfc.utils.formatXmlWhitespace,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "slashfix": xml2rfc.utils.safeTagSlashedWords,
        "writer": xml2rfc.NroffRfcWriter,
        "postrendering": lambda x: x,
        "postprocesslines": "post_process_lines",
    },
    {
        "ext": "html",
        "spacefix": lambda x: x,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "slashfix": xml2rfc.utils.safeTagSlashedWords,
        "writer": xml2rfc.HtmlRfcWriter,
        "postrendering": html_post_rendering,
        "postprocesslines": "post_process_lines",
    },
]

class AnnotatedElement(lxml.etree.ElementBase):
    pis = None

class WriterElementTest(unittest.TestCase):
    """ Performs tests of isolated XML elements against text writer functions """

    def setUp(self):
        xml2rfc.log.quiet = True

    def function_test(self, name, func_name):
        """ Skeleton method for testing an XML element with a writer function """
        xmlpath = "tests/input/%s.xml" % name
        parser = lxml.etree.XMLParser()
        element_lookup = lxml.etree.ElementDefaultClassLookup(element=AnnotatedElement)
        parser.set_element_class_lookup(element_lookup)
        element = lxml.etree.parse(xmlpath, parser).getroot()
        xmlrfc = XmlRfcDummy()
        pis = xmlrfc.pis.copy()
        element.pis = pis
        elements_cache = []
        for e in element.iterdescendants():
            elements_cache.append(e)
            if e.tag is lxml.etree.PI:
                xmlrfc.parse_pi(e)
                pis = xmlrfc.pis.copy()
            else:
                if isinstance(e, AnnotatedElement):
                    e.pis = pis

        for format in output_format:
            ext = format["ext"]
            spacefix = format["spacefix"]
            unicodefix = format["unicodefix"]
            slashfix = format["slashfix"]
            writer = format["writer"](xmlrfc, quiet=True)
            testfunc = getattr(writer, func_name)
            postprocessing = getattr(writer, format["postprocesslines"])
            postrendering = format['postrendering']
            #
            validpath = "tests/valid/%s.%s" % (name, ext)
            try:
                fh = open(validpath)
            except IOError:
                fh = open(validpath, "w+")
            valid = fh.read()
            fh.close()
            #
            spacefix(element)
            unicodefix(element)
            slashfix(element)
            testfunc(element)
            output = postrendering('\n'.join(arrstrip(postprocessing(writer.buf))))  # Don't care about initial blank
            diff_test(self, valid, output, validpath.replace('valid', 'failed'), format['ext'])

    def test_references(self):
        return self.function_test('references', 'write_reference_list')

    def test_list_format(self):
        return self.function_test("list_format", "write_t_rec")

    def test_list_hanging(self):
        return self.function_test("list_hanging", "write_t_rec")

    def test_list_letters(self):
        return self.function_test("list_letters", "write_t_rec")
    
    def test_texttable_small(self):
        return self.function_test("texttable_small", "draw_table")

    def test_texttable_small_full(self):
        return self.function_test("texttable_small_full", "draw_table")

    def test_texttable_small_all(self):
        return self.function_test("texttable_small_all", "draw_table")

    def test_texttable_small_headers(self):
        return self.function_test("texttable_small_headers", "draw_table")

    def test_texttable_small_none(self):
        return self.function_test("texttable_small_none", "draw_table")

    def test_texttable_full(self):
        return self.function_test("texttable_full", "write_section_rec")

    def test_figure_title(self):
        return self.function_test("figure_title", "write_t_rec")

    def test_texttable_title(self):
        return self.function_test("texttable_title", "write_section_rec")

    def test_section(self):
        return self.function_test("section", "write_section_rec")

    def test_textwrap(self):
        return self.function_test("textwrap", "write_section_rec")

    def test_slashbreak(self):
        return self.function_test("slashbreak", "write_section_rec")

    def test_abbreviations(self):
        return self.function_test("abbreviations", "write_t_rec")

class WriterRootTest(unittest.TestCase):
    """ Performs tests of full <rfc> + <front> trees against text writer functions """

    def parse(self, path):
        """ Parse a minimal RFC tree and instantiate a writer """
        self.parser = xml2rfc.XmlRfcParser(path, quiet=True, options=default_options, **options_for_xmlrfcparser)
        self.xmlrfc = self.parser.parse()
        self.writer = xml2rfc.PaginatedTextRfcWriter(self.xmlrfc, quiet=True)
        self.writer._format_date()
        self.writer.pre_rendering()

    def set_root_attrs(self, submissionType, category, consensus):
        """ Modify basic attributes on root element for testing """
        self.xmlrfc.getroot().attrib['submissionType'] = submissionType
        self.xmlrfc.getroot().attrib['category'] = category
        self.xmlrfc.getroot().attrib['consensus'] = consensus

    def set_valid(self, validpath):
        """ Set the output to validate against and the path to fail to """
        assert('valid' in validpath)
        fh = open(validpath)
        self.valid = fh.read()
        self.failpath = validpath.replace('valid', 'failed')
        fh.close()

    def header_footer_test(self):
        output = '\n'.join(self.writer._make_footer_and_header(1))
        output = strip_formatting_whitespace(output)
        diff_test(self, self.valid, output, self.failpath, 'txt')

    def top_test(self):
        self.writer.write_top(self.writer._prepare_top_left(), 
                              self.writer._prepare_top_right())
        output = '\n'.join(self.writer.buf)  # Care about initial blank
        output = strip_formatting_whitespace(output)
        diff_test(self, self.valid, output, self.failpath, 'txt')

    def status_test(self):
        self.writer.write_status_section()
        output = '\n'.join(arrstrip(self.writer.buf))  # Don't care about initial blank
        output = strip_formatting_whitespace(output)
        diff_test(self, self.valid, output, self.failpath, 'txt')


class WriterDraftTest(WriterRootTest):
    """ Test Internet-Draft boilerplate"""

    def setUp(self):
        self.parse('tests/input/draft_root.xml')
    
    def test_header_footer(self):
        self.set_valid('tests/valid/header_footer_draft.txt')
        return self.header_footer_test()

    def test_top(self):
        self.set_valid('tests/valid/top_draft.txt')
        return self.top_test()


class WriterRfcTest(WriterRootTest):
    """ Test RFC boilerplate """

    def setUp(self):
        self.parse('tests/input/rfc_root.xml')

    def test_header_footer(self):
        self.set_valid('tests/valid/header_footer_rfc.txt')
        return self.header_footer_test()

    def test_top(self):
        self.set_valid('tests/valid/top_rfc.txt')
        return self.top_test()

    def test_status_ietf_std_yes(self):
        self.set_root_attrs('IETF', 'std', 'yes')
        self.set_valid('tests/valid/status_ietf_std_yes.txt')
        return self.status_test()

    def test_status_ietf_bcp_yes(self):
        self.set_root_attrs('IETF', 'bcp', 'yes')
        self.set_valid('tests/valid/status_ietf_bcp_yes.txt')
        return self.status_test()

    def test_status_ietf_exp_yes(self):
        self.set_root_attrs('IETF', 'exp', 'yes')
        self.set_valid('tests/valid/status_ietf_exp_yes.txt')
        return self.status_test()

    def test_status_ietf_exp_no(self):
        self.set_root_attrs('IETF', 'exp', 'no')
        self.set_valid('tests/valid/status_ietf_exp_no.txt')
        return self.status_test()

    def test_status_ietf_historic_no(self):
        self.set_root_attrs('IETF', 'historic', 'no')
        self.set_valid('tests/valid/status_ietf_historic_no.txt')
        return self.status_test()

    def test_status_ietf_historic_yes(self):
        self.set_root_attrs('IETF', 'historic', 'yes')
        self.set_valid('tests/valid/status_ietf_historic_yes.txt')
        return self.status_test()

    def test_status_ietf_info_yes(self):
        self.set_root_attrs('IETF', 'info', 'yes')
        self.set_valid('tests/valid/status_ietf_info_yes.txt')
        return self.status_test()

    def test_status_ietf_info_no(self):
        self.set_root_attrs('IETF', 'info', 'no')
        self.set_valid('tests/valid/status_ietf_info_no.txt')
        return self.status_test()

    def test_status_iab_info(self):
        self.set_root_attrs('IAB', 'info', 'no')
        self.set_valid('tests/valid/status_iab_info.txt')
        return self.status_test()

    def test_status_iab_historic(self):
        self.set_root_attrs('IAB', 'historic', 'no')
        self.set_valid('tests/valid/status_iab_historic.txt')
        return self.status_test()

    def test_status_iab_exp(self):
        self.set_root_attrs('IAB', 'exp', 'no')
        self.set_valid('tests/valid/status_iab_exp.txt')
        return self.status_test()

    def test_status_irtf_exp_yes(self):
        self.set_root_attrs('IRTF', 'exp', 'yes')
        self.set_valid('tests/valid/status_irtf_exp_yes.txt')
        return self.status_test()

    def test_status_irtf_exp_no(self):
        self.set_root_attrs('IRTF', 'exp', 'no')
        self.set_valid('tests/valid/status_irtf_exp_no.txt')
        return self.status_test()

    def test_status_irtf_exp_nowg(self):
        self.xmlrfc.getroot().find('front/workgroup').text = ''
        self.set_root_attrs('IRTF', 'exp', 'no')
        self.set_valid('tests/valid/status_irtf_exp_nowg.txt')
        return self.status_test()

    def test_status_irtf_historic_yes(self):
        self.set_root_attrs('IRTF', 'historic', 'yes')
        self.set_valid('tests/valid/status_irtf_historic_yes.txt')
        return self.status_test()

    def test_status_irtf_historic_no(self):
        self.set_root_attrs('IRTF', 'historic', 'no')
        self.set_valid('tests/valid/status_irtf_historic_no.txt')
        return self.status_test()

    def test_status_irtf_historic_nowg(self):
        self.xmlrfc.getroot().find('front/workgroup').text = ''
        self.set_root_attrs('IRTF', 'historic', 'no')
        self.set_valid('tests/valid/status_irtf_historic_nowg.txt')
        return self.status_test()

    def test_status_irtf_info_yes(self):
        self.set_root_attrs('IRTF', 'info', 'yes')
        self.set_valid('tests/valid/status_irtf_info_yes.txt')
        return self.status_test()

    def test_status_irtf_info_no(self):
        self.set_root_attrs('IRTF', 'info', 'no')
        self.set_valid('tests/valid/status_irtf_info_no.txt')
        return self.status_test()

    def test_status_irtf_info_nowg(self):
        self.xmlrfc.getroot().find('front/workgroup').text = ''
        self.set_root_attrs('IRTF', 'info', 'no')
        self.set_valid('tests/valid/status_irtf_info_nowg.txt')
        return self.status_test()

    def test_status_independent_info(self):
        self.set_root_attrs('independent', 'info', 'no')
        self.set_valid('tests/valid/status_independent_info.txt')
        return self.status_test()

    def test_status_independent_historic(self):
        self.set_root_attrs('independent', 'historic', 'no')
        self.set_valid('tests/valid/status_independent_historic.txt')
        return self.status_test()

    def test_status_independent_exp(self):
        self.set_root_attrs('independent', 'exp', 'no')
        self.set_valid('tests/valid/status_independent_exp.txt')
        return self.status_test()


class PdfWriterTests(unittest.TestCase):
    elements_root = None
    elements_pdfxml = None

    @classmethod
    def setUpClass(cls) -> None:
        # Putting this in setUpClass() allows this module to be imported even if this
        # procedure will fail. This improves some error messages and makes debugging
        # a little bit easier. The setUpClass() method is run by unittest during init.
        # This happens only once, avoiding repeated execution of slow operations.
        def _pdfwriter(path):
            """ Parse a minimal RFC tree and instantiate a writer """
            parser = xml2rfc.XmlRfcParser(path, quiet=True, **options_for_xmlrfcparser)
            xmlrfc = parser.parse()
            writer = xml2rfc.writers.pdf.PdfWriter(xmlrfc, quiet=True, )
            return writer

        elements_writer = _pdfwriter('tests/input/elements.xml')
        try:
            elements_pdfdoc = elements_writer.pdf() # has side effects on .root
        except Exception as e:
            print(e)
            raise
        cls.pdf_writer = elements_writer
        cls.elements_root   = elements_writer.root
        cls.elements_pdfxml = xmldoc(None, bytes=elements_pdfdoc)

    def setUp(self):
        xml2rfc.log.quiet = True
        self.pdfxml = copy.deepcopy(self.elements_pdfxml)
        self.root = copy.deepcopy(self.elements_root)

    def test_text_content(self):
        def norm(t):
            return re.sub(r'\s+', ' ', t).strip()
        #
        text = norm('\n'.join( p.text for p in self.pdfxml.xpath('.//Page/text') ))
        for e in self.root.xpath('./middle//*'):
            if e.text and e.text.strip() and e.tag not in xml2rfc.util.unicode.unicode_content_tags and not xml2rfc.util.unicode.is_svg(e):
                t =  norm(e.text.split(None, 1)[0])
                self.assertIn(t, text)

    def test_included_fonts(self):
        if xml2rfc.HAVE_WEASYPRINT and xml2rfc.HAVE_PANGO:
            font_families = set([ f.text for f in self.pdfxml.xpath('.//FontFamily') ])
            for script in self.root.get('scripts').split(','):
                family = xml2rfc.util.fonts.get_noto_serif_family_for_script(script)
                self.assertIn(family, font_families, 'Missing font match for %s' % script)

    def test_flatten_unicode_spans(self):
        input_html = '<body><p>f<span class="unicode">o</span>o<span class="unicode">ba</span>r</p></body>'
        output_html = self.pdf_writer.flatten_unicode_spans(input_html)
        self.assertEqual(output_html, '<body><p>foobar</p></body>')

    def test_get_serif_fonts(self):
        fonts = self.pdf_writer.get_serif_fonts()
        for font in ['Noto Serif', 'Noto Sans Cherokee', 'Noto Serif CJK SC', 'Noto Serif Hebrew', 'NotoSansSymbols2', 'NotoSansMath']:
            self.assertIn(font, fonts)

    def test_get_mono_fonts(self):
        fonts = self.pdf_writer.get_mono_fonts()
        for font in ['Roboto Mono', 'Noto Sans Cherokee', 'Noto Serif CJK SC', 'Noto Serif Hebrew', 'NotoSansSymbols2', 'NotoSansMath']:
            self.assertIn(font, fonts)


class HtmlWriterTest(unittest.TestCase):
    '''HtmlWriter tests'''

    def setUp(self):
        xml2rfc.log.quiet = True
        path = 'tests/input/elements.xml'
        self.parser = xml2rfc.XmlRfcParser(path,
                                           quiet=True,
                                           options=default_options,
                                           **options_for_xmlrfcparser)
        self.xmlrfc = self.parser.parse()
        self.writer = xml2rfc.HtmlWriter(self.xmlrfc, quiet=True)

    def test_get_font_family(self):
        font_families = {
                'serif': 'Noto Serif',
                'sans-serif': 'Noto Sans',
                'monospace': 'Roboto Mono',
                'inherit': 'inherit'}

        for value, font_family in font_families.items():
            self.assertEqual(self.writer.get_font_family(value), font_family)

    def test_set_font_family(self):
        input_svg = lxml.etree.fromstring('''
<svg xmlns="http://www.w3.org/2000/svg">
  <path />
  <g>
    <text>foobar</text>
    <text font-family="serif">serif</text>
    <text font-family="inherit">inherit</text>
    <text font-family="monospace">monospace</text>
    <text font-family="sans-serif">sans-serif'</text>
  </g>
</svg>''')
        expected_svg = lxml.etree.tostring(lxml.etree.fromstring('''
<svg xmlns="http://www.w3.org/2000/svg">
  <path />
  <g>
    <text>foobar</text>
    <text font-family="Noto Serif">serif</text>
    <text font-family="inherit">inherit</text>
    <text font-family="Roboto Mono">monospace</text>
    <text font-family="Noto Sans">sans-serif'</text>
  </g>
</svg>'''))
        result_svg = self.writer.set_font_family(input_svg)
        result = lxml.etree.tostring(result_svg)
        self.assertEqual(result, expected_svg)


class PrepToolWriterTest(unittest.TestCase):
    '''PrepToolWriter tests'''

    def setUp(self):
        xml2rfc.log.quiet = True
        path = 'tests/input/elements.xml'
        self.parser = xml2rfc.XmlRfcParser(path,
                                           quiet=True,
                                           options=default_options,
                                           **options_for_xmlrfcparser)
        self.xmlrfc = self.parser.parse()
        self.writer = xml2rfc.PrepToolWriter(self.xmlrfc, quiet=True)

    def test_rfc_check_attribute_values_editorial(self):
        rfc = lxml.etree.fromstring('''
<rfc
    submissionType="editorial"
    category="info">
</rfc>''')
        self.writer.root = rfc

        self.writer.check_attribute_values(rfc, None)
        self.assertEqual(len(self.writer.errors), 0)

    def test_boilerplate_insert_status_of_memo_editorial(self):
        rfc = lxml.etree.fromstring('''
<rfc
    number="9280"
    ipr="trust200902"
    submissionType="editorial"
    category="info">
</rfc>''')
        self.writer.options.rfc = True
        self.writer.root = rfc
        self.writer.rfcnumber = 9280

        self.writer.boilerplate_insert_status_of_memo(rfc, rfc)
        self.assertEqual(len(self.writer.errors), 0)
        self.assertEqual(len(rfc.xpath('./section/name[text()="Status of This Memo"]')), 1)
        paras = rfc.xpath('./section/t')
        boilerplate_text = boilerplate_rfc_status_of_memo['editorial']['info']['n/a']
        self.assertEqual(len(paras), len(boilerplate_text))
        index = 0
        for boilerplate in boilerplate_text[-1]:
            for line in boilerplate.split('\n')[1:-1]:
                self.assertIn(line.strip(), paras[index].text)
            index += 1

        # test eref element
        target = 'https://www.rfc-editor.org/info/rfc9280'
        self.assertEqual(target, rfc.xpath('./section/t/eref')[0].get('target'))

class TextWriterTest(unittest.TestCase):
    '''TextWriter tests'''

    def setUp(self):
        xml2rfc.log.quiet = True
        path = 'tests/input/elements.xml'
        self.parser = xml2rfc.XmlRfcParser(path,
                                           quiet=True,
                                           options=default_options,
                                           **options_for_xmlrfcparser)
        self.xmlrfc = self.parser.parse()
        self.writer = xml2rfc.TextWriter(self.xmlrfc, quiet=True)

    def test_render_reference(self):
        # test annotations
        reference = '''
<references>
  <reference anchor="REFTEST">
    <front>
      <title>Reference Test</title>
      <author initials="J." surname="Doe" fullname="Jane Doe">
        <organization>ACMI Corp.</organization>
      </author>
      <date month="February" year="2024"/>
    </front>
    <annotation>{annotation}</annotation>
  </reference>
</references>'''
        self.writer.refname_mapping['REFTEST'] = 'REFTEST'

        # single line annotation
        annotation = 'foobar'
        references = lxml.etree.fromstring(reference.format(annotation=annotation))
        lines = self.writer.render_reference(references.getchildren()[0], width=60)
        self.assertEqual(len(lines), 1)
        self.assertIn(annotation, lines[0].text)

        # multi line annotation
        annotation = '''Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa.
               Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.'''
        references = lxml.etree.fromstring(reference.format(annotation=annotation))
        lines = self.writer.render_reference(references.getchildren()[0], width=60)
        self.assertGreater(len(lines), 1)
        self.assertIn(annotation[:5], lines[0].text)

        # single line annotation (larger than width and smaller than MAX_WIDTH)
        annotation = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commo'
        references = lxml.etree.fromstring(reference.format(annotation=annotation))
        lines = self.writer.render_reference(references.getchildren()[0], width=len(annotation)-5)
        self.assertGreater(MAX_WIDTH, len(annotation))
        self.assertGreater(len(lines), 1)
        self.assertIn(annotation[:5], lines[0].text)

        # annotation with URL
        url = 'https://example.org'
        annotation = f'Example: <eref target="{url}" />'
        references = lxml.etree.fromstring(reference.format(annotation=annotation))
        lines = self.writer.render_reference(references.getchildren()[0], width=60)
        self.assertEqual(len(lines), 2)
        self.assertIn(url, lines[1].text)

    def test_render_artwork_svg_only(self):
        artwork_str = '''
<artwork type="svg">
    <svg xmlns="http://www.w3.org/2000/svg">
      <text x="10" y="15">foobar</text>
    </svg>
</artwork>'''
        artwork = lxml.etree.fromstring(artwork_str)

        # for RFC
        self.writer.root = lxml.etree.fromstring(f'<rfc number="1234"></rfc>')
        self.writer.options.rfc = True
        self.writer.rfcnumber = 1234
        lines = self.writer.render_artwork(artwork, width=60)
        text = ''.join(line.text for line in lines)
        self.assertIn("Artwork only available as svg", text)
        self.assertIn(default_options.rfc_html_archive_url, text)
        self.assertIn('rfc1234.html', text)

        # for Draft
        self.writer.options.rfc = None
        lines = self.writer.render_artwork(artwork, width=60)
        text = ' '.join(line.text for line in lines)
        self.assertIn("Artwork only available as svg", text)
        self.assertIn(default_options.id_html_archive_url, text)
        self.assertIn(".html", text)



class BaseV3WriterTest(unittest.TestCase):
    '''BaseV3Writer tests'''

    def setUp(self):
        xml2rfc.log.quiet = True
        path = 'tests/input/elements.xml'
        self.parser = xml2rfc.XmlRfcParser(path,
                                           quiet=True,
                                           options=default_options,
                                           **options_for_xmlrfcparser)
        self.xmlrfc = self.parser.parse()
        self.writer = BaseV3Writer(self.xmlrfc, quiet=True)

    def test_validate_draft_name(self):
        # Valid documents
        valid_docs = []
        valid_docs.append(lxml.etree.fromstring('''
<rfc
    number="9280"
    docName = "draft-ietf-foo-bar-23"
    ipr="trust200902"
    submissionType="editorial"
    category="info">
    <link href="https://datatracker.ietf.org/doc/draft-ietf-foo-bar-23" rel="prev"/>
    <front>
        <seriesInfo name="RFC" value="9280" stream="IETF" />
    </front>
</rfc>'''))
        valid_docs.append(lxml.etree.fromstring('''
<rfc
    docName = "draft-ietf-foo-bar-23"
    ipr="trust200902"
    submissionType="editorial"
    category="info">
    <front>
        <seriesInfo name="Internet-Draft" value="draft-ietf-foo-bar-23" />
    </front>
</rfc>'''))
        valid_docs.append(lxml.etree.fromstring('''
<rfc
    docName = "draft-ietf-foo-bar-23"
    ipr="trust200902"
    submissionType="editorial"
    category="info">
    <front>
    </front>
</rfc>'''))
        valid_docs.append(lxml.etree.fromstring('''
<rfc
    ipr="trust200902"
    submissionType="editorial"
    category="info">
    <front>
        <seriesInfo name="Internet-Draft" value="draft-ietf-foo-bar-23" />
    </front>
</rfc>'''))
        for valid_doc in valid_docs:
            self.writer.root = valid_doc
            self.assertTrue(self.writer.validate_draft_name())

        # Invalid document
        invalid_doc = lxml.etree.fromstring('''
<rfc
    docName = "draft-ietf-foo-bar-23"
    ipr="trust200902"
    submissionType="editorial"
    category="info">
    <front>
        <seriesInfo name="Internet-Draft" value="draft-ietf-foo-bar-3" />
    </front>
</rfc>''')
        self.writer.root = invalid_doc
        with self.assertRaises(RfcWriterError):
            self.writer.validate_draft_name()


if __name__ == '__main__':
    unittest.main()
