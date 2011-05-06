#!/usr/bin/env python

import xml2rfc.parser
import xml2rfc.writers
import sys

def main():
    if len(sys.argv) > 1:
        parser = xml2rfc.parser.XmlRfcParser()
        xmlrfc = parser.parse(str(sys.argv[1]))
        writer = xml2rfc.writers.RawTextRfcWriter(xmlrfc)
        writer.write('output.txt')
    else:
        print ("Needs xml file argument")

if __name__ == '__main__':
    main()
