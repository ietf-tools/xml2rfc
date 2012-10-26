#!/usr/bin/env python
# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

from setuptools import setup
import xml2rfc_gui.main

APP = ['xml2rfc-gui.py']
DATA = ['xml2rfc/templates']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/xml2rfc.icns',         
    'includes': ['sip', 'PyQt4', 'lxml.etree', 'lxml._elementpath'],
    'frameworks' : ['/usr/lib/libxml2.2.dylib'],
}
 
setup(
    name='xml2rfc',
    version='.'.join(map(str, xml2rfc_gui.main.VERSION)),
    app=APP,
    data_files = DATA,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
