#!/usr/bin/env python

import unittest
import difflib
import xml2rfc
import xml2rfc.utils
import lxml
import tempfile
import re

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
    test  =  test.replace(xml2rfc.__version__, 'N.N.N')
    validarr = [line.rstrip() for line in valid.splitlines()]
    testarr = [line.rstrip() for line in test.splitlines()]
    if testarr != validarr:
        diff = difflib.ndiff(validarr, testarr)
        fh = open(failpath, 'w')
        fh.write(test.encode('ascii', 'xmlcharrefreplace'))
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
            "sectionorphan":    5,
            "slides":		"no",
            "sortrefs":		"yes",  # different from default
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

output_format = [
    {
        "ext": "txt",
        "spacefix": xml2rfc.utils.formatXmlWhitespace,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "writer": xml2rfc.PaginatedTextRfcWriter,
        "postprocesslines": "post_process_lines"
    },
    {
        "ext": "raw.txt",
        "spacefix": xml2rfc.utils.formatXmlWhitespace,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "writer": xml2rfc.RawTextRfcWriter,
        "postprocesslines": "post_process_lines"
    },
    {
        "ext": "nroff",
        "spacefix": xml2rfc.utils.formatXmlWhitespace,
        "unicodefix": xml2rfc.utils.safeReplaceUnicode,
        "writer": xml2rfc.NroffRfcWriter,
        "postprocesslines": "post_process_lines"
    },
    {
        "ext": "html",
        "spacefix": lambda x: x,
        "unicodefix": lambda x: x,
        "writer": xml2rfc.HtmlRfcWriter,
        "postprocesslines": "post_process_lines"
    },
    {
        "ext": "exp.xml",
        "spacefix": lambda x: x,
        "unicodefix": lambda x: x,
        "writer": xml2rfc.HtmlRfcWriter,
        "postprocesslines": "post_process_lines"
    },
]

class WriterElementTest(unittest.TestCase):
    """ Performs tests of isolated XML elements against text writer functions """

    def setUp(self):
        xml2rfc.log.quiet = True

    def function_test(self, name, func_name):
        """ Skeleton method for testing an XML element with a writer function """
        xmlpath = "tests/input/%s.xml" % name
        element = lxml.etree.parse(xmlpath).getroot()
        for format in output_format:
            ext = format["ext"]
            spacefix = format["spacefix"]
            unicodefix = format["unicodefix"]
            writer = format["writer"](XmlRfcDummy(), quiet=True)
            testfunc = getattr(writer, func_name)
            postprocessing = getattr(writer, format["postprocesslines"])
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
            testfunc(element)
            output = '\n'.join(arrstrip(postprocessing(writer.buf)))  # Don't care about initial blank
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

if __name__ == '__main__':
    unittest.main()
