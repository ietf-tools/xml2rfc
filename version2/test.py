#!/usr/bin/env python
""" Tests all output writers with a given input file """

import xml2rfc
import sys
import unittest
import os.path

class WriterTests(unittest.TestCase):
    def test_rawtext(self):
        xml2rfc.RawTextRfcWriter(self.xmlrfc).write('output-raw.txt')
        
    def test_pagedtext_writer(self):
        xml2rfc.PaginatedTextRfcWriter(self.xmlrfc).write('output.txt')
        
    def test_nroff(self):
        xml2rfc.NroffRfcWriter(self.xmlrfc).write('output.nroff')
        
    def test_html(self):
        xml2rfc.HtmlRfcWriter(self.xmlrfc).write('output.html')



def main():
    if len(sys.argv) < 2:
        print 'Needs xml file argument'
        sys.exit(1)
    else:
        if not os.path.exists(sys.argv[1]):
            print 'File doesnt exist:', sys.argv[1]
            sys.exit(1)

    parser = xml2rfc.parser.XmlRfcParser(str(sys.argv[1]), verbose=True)
    WriterTests.xmlrfc = parser.parse()
    suite = unittest.TestLoader().loadTestsFromTestCase(WriterTests)
    result = unittest.TestResult()
    suite.run(result)
    
    # Display errors
    for errors in result.errors:
        print '-' * 80
        print 'From test:', errors[0]
        print '-' * 80, '\n'
        print errors[1]

if __name__ == '__main__':
    main()
