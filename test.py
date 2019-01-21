#!/usr/bin/env python

import copy
import difflib
import lxml
import re
import six
import tempfile
import unittest
import xml2rfc
import xml2rfc.utils

from xml2rfc.walkpdf import xmldoc

try:
    import debug
    assert debug
except ImportError:
    pass

def arrstrip(arr):
    """ Strip beginning and end blanklines of an array """
    if not arr[0]: arr.pop(0)
    if not arr[-1]: arr.pop()
    return arr


def diff_test(case, valid, test, failpath):
    """ Compare two strings.  If not equal, fail with a useful diff and save
        second string to a file.
    """
    # The following 2 lines does the right thing for both python 2.x and 3.x
    test  = str(test)
    valid = str(valid)
    # replace the current version with someting static, if present
    test  =  str(test.replace(xml2rfc.__version__, 'N.N.N'))
    validarr = [line.rstrip() for line in valid.splitlines()]
    testarr = [line.rstrip() for line in test.splitlines()]
    if testarr != validarr:
        diff = difflib.ndiff(validarr, testarr)
        fh = open(failpath, 'w')
        fh.write(test)
        fh.close()
        case.fail("Output doesn't match, file saved to %s.\nDIFF:\n%s" % (failpath, '\n'.join(diff)))

def strip_formatting_whitespace(text):
    """ We use non-breaking space, non-breaking hyphen
        internally for formattin purposes - they need to be cleaned out
    """
    return text.replace(u'\u00A0', ' ').replace(u'\u2011', '-')

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
        "unicodefix": lambda x: x,
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
            diff_test(self, valid, output, validpath.replace('valid', 'failed'))

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
        self.parser = xml2rfc.XmlRfcParser(path, quiet=True)
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
        diff_test(self, self.valid, output, self.failpath)

    def top_test(self):
        self.writer.write_top(self.writer._prepare_top_left(), 
                              self.writer._prepare_top_right())
        output = '\n'.join(self.writer.buf)  # Care about initial blank
        output = strip_formatting_whitespace(output)
        diff_test(self, self.valid, output, self.failpath)

    def status_test(self):
        self.writer.write_status_section()
        output = '\n'.join(arrstrip(self.writer.buf))  # Don't care about initial blank
        output = strip_formatting_whitespace(output)
        diff_test(self, self.valid, output, self.failpath)


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

    def test_status_ietf_exp_yes(self):
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


def pdfwriter(path):
    """ Parse a minimal RFC tree and instantiate a writer """
    parser = xml2rfc.XmlRfcParser(path, quiet=True)
    xmlrfc = parser.parse()
    writer = xml2rfc.writers.pdf.PdfWriter(xmlrfc, quiet=True, )
    return writer

elements_writer = pdfwriter('tests/input/elements.xml')
elements_pdfdoc = elements_writer.pdf() # has side effects on .root
elements_root   = elements_writer.root
elements_pdfxml = xmldoc(None, bytes=elements_pdfdoc)

class PdfWriterTests(unittest.TestCase):

    def setUp(self):
        xml2rfc.log.quiet = True
        self.pdfxml = copy.deepcopy(elements_pdfxml)
        self.root = copy.deepcopy(elements_root)


    def test_text_content(self):
        def norm(t):
            return re.sub(r'\s+', ' ', t).strip()
        #
        text = norm('\n'.join( p.text for p in self.pdfxml.xpath('.//Page/text') ))
        for e in self.root.xpath('./middle//*'):
            if e.text and e.text.strip() and e.tag not in xml2rfc.util.unicode.unicode_content_tags:
                t =  norm(e.text.split(None, 1)[0])
                self.assertIn(t, text)

    def test_included_fonts(self):
        if xml2rfc.HAVE_WEASYPRINT and xml2rfc.HAVE_PYCAIRO and xml2rfc.HAVE_CAIRO and xml2rfc.HAVE_PANGO:
            font_families = set([ f.text for f in self.pdfxml.xpath('.//FontFamily') ])
            for script in self.root.get('scripts').split(','):
                family = xml2rfc.util.fonts.get_noto_serif_family_for_script(script)
                self.assertIn(family, font_families, 'Missing font match for %s' % script)

if __name__ == '__main__':
    unittest.main()
