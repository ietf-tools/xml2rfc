#!/usr/bin/env python

import xml2rfc.parser
import sys

def main():
    if len(sys.argv) > 1:
        tree = xml2rfc.parser.XmlRfcTree()
        parser = xml2rfc.parser.XmlRfcParser(tree)
        parser.parse(str(sys.argv[1]))
        print repr(tree)
    else:
        print ("Needs xml file argument")

if __name__ == '__main__':
    main()
