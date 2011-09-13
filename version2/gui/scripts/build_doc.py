#!/usr/bin/env python

from lxml import etree
from lxml.builder import E
import os
import subprocess

root    = '../cli'
docpath = 'doc'
qrcpath = 'doc.qrc'
rccpath = 'xml2rfc_gui/doc.py'

def main():
    res = E.qresource()
    for path, dirs, files in os.walk(os.path.join(root, docpath)):
        if not '.svn' in path:
            for file in files:
                full = os.path.join(path, file)
                print 'Reading', full
                res.append(E.file(full, alias=os.path.relpath(full, root)))

    fh = open(qrcpath, 'w')
    fh.write('<!DOCTYPE RCC><RCC version="1.0">\n')
    fh.write(etree.tostring(res, pretty_print=True))
    fh.write('</RCC>')
    fh.close()

    print 'Wrote', qrcpath

    subprocess.call(['pyrcc4', qrcpath, '-o', rccpath])
    
    print 'Wrote', rccpath

if __name__ == '__main__':
    main()
