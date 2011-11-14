#!/usr/bin/env python

import unittest
import difflib
import xml2rfc
import xml2rfc.utils
import lxml
import tempfile


def diff_test(case, valid, test, failpath):
    """ Compare two strings.  If not equal, fail with a useful diff and save
        second string to a file.
    """
    validarr = [line.rstrip() for line in valid.splitlines()]
    testarr = [line.rstrip() for line in test.splitlines()]
    for arr in (validarr, testarr):
        if not arr[0]: arr.pop(0)
        if not arr[-1]: arr.pop()
    if testarr != validarr:
        diff = difflib.ndiff(testarr, validarr)
        fh = open(failpath, 'w')
        fh.write(test)
        fh.close()
        case.fail("Output doesn't match, file saved to %s.\nDIFF:\n%s" % (failpath, '\n'.join(diff)))


class XmlRfcDummy():
    """ Dummy rfc used for test fixtures """
    def getroot(self):
        return lxml.etree.Element('rfc')

    def getpis(self):
        return {
            'sortrefs': 'yes'
        }

    def parse_pi(self, pi):
        pass


class TextWriterElementTest(unittest.TestCase):
    """ Performs tests of isolated XML elements against text writer functions """

    def setUp(self):
        """ Instantiate a writer with a mock object """
        self.writer = xml2rfc.PaginatedTextRfcWriter(XmlRfcDummy(), quiet=True)
        xml2rfc.log.quiet = True

    def function_test(self, xmlpath, validpath, function):
        """ Skeleton method for testing an XML element with a writer function """
        assert('valid' in validpath)
        fh = open(validpath)
        valid = fh.read()
        fh.close()
        element = lxml.etree.parse(xmlpath).getroot()
        xml2rfc.utils.formatXmlWhitespace(element)
        xml2rfc.utils.safeReplaceUnicode(element)
        function(element)
        output = '\n'.join(self.writer.buf)
        diff_test(self, valid, output, validpath.replace('valid', 'failed'))

    def test_references(self):
        return self.function_test('tests/input/references.xml',
                                  'tests/valid/references.txt',
                                  self.writer.write_reference_list)

    def test_list_format(self):
        return self.function_test('tests/input/list_format.xml',
                                  'tests/valid/list_format.txt',
                                  self.writer.write_t_rec)

    def test_list_hanging(self):
        return self.function_test('tests/input/list_hanging.xml',
                                  'tests/valid/list_hanging.txt',
                                  self.writer.write_t_rec)

    def test_list_letters(self):
        return self.function_test('tests/input/list_letters.xml',
                                  'tests/valid/list_letters.txt',
                                  self.writer.write_t_rec)
    
    def test_texttable_small(self):
        return self.function_test('tests/input/texttable_small.xml',
                                  'tests/valid/texttable_small.txt',
                                  self.writer.draw_table)

class TextWriterRootTest(unittest.TestCase):
    """ Performs tests of full <rfc> + <front> trees against text writer functions """

    def init_test(self, path):
        """ Parse a minimal tree and instantiate a writer """
        self.parser = xml2rfc.XmlRfcParser(path, quiet=True)
        self.xmlrfc = self.parser.parse()
        self.writer = xml2rfc.PaginatedTextRfcWriter(self.xmlrfc, quiet=True)
        self.writer._format_date()
        self.writer.pre_processing()

    def header_footer_test(self, validpath):
        assert('valid' in validpath)
        fh = open(validpath)
        valid = fh.read()
        fh.close()
        output = self.writer._make_footer_and_header(1)
        diff_test(self, valid, output, validpath.replace('valid', 'failed'))

    def top_test(self, validpath):
        assert('valid' in validpath)
        fh = open(validpath)
        valid = fh.read()
        fh.close()
        self.writer.write_top(self.writer._prepare_top_left(), 
                              self.writer._prepare_top_right())
        output = '\n'.join(self.writer.buf)
        diff_test(self, valid, output, validpath.replace('valid', 'failed'))


class TextWriterDraftTest(TextWriterRootTest):
    """ Test Internet-Draft boilerlpate"""

    def setUp(self):
        self.init_test('tests/input/draft_root.xml')
    
    def test_header_footer(self):
        return self.header_footer_test('tests/valid/header_footer_draft.txt')

    def test_top(self):
        return self.top_test('tests/valid/top_draft.txt')


class TextWriterRfcTest(TextWriterRootTest):
    """ Test RFC boilerplate """

    def setUp(self):
        self.init_test('tests/input/rfc_root.xml')

    def test_header_footer(self):
        return self.header_footer_test('tests/valid/header_footer_rfc.txt')

    def test_top(self):
        return self.top_test('tests/valid/top_rfc.txt')


if __name__ == '__main__':
    unittest.main(verbosity=2)
