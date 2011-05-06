#!/usr/bin/env python

import xml2rfc.parser
import xml2rfc.writers
import sys

def main():
    if len(sys.argv) > 1:
<<<<<<< HEAD
        parser = xml2rfc.parser.XmlRfcParser()
        xmlrfc = parser.parse(str(sys.argv[1]))
        writer = xml2rfc.writers.RawTextRfcWriter(xmlrfc)
=======
        tree = xml2rfc.parser.XmlRfc()
        parser = xml2rfc.parser.XmlRfcParser(tree)
        writer = xml2rfc.writers.PaginatedTextRfcWriter(tree)
        parser.parse(str(sys.argv[1]))
>>>>>>> PEP-8 Fixes
        writer.write('output.txt')
    else:
        print ("Needs xml file argument")

if __name__ == '__main__':
    main()
