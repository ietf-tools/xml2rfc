#!/usr/bin/env python
# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

# from setuptools import setup
from distutils.core import setup
import xml2rfc_gui.main

setup(
    name='xml2rfc-gui',
    version='.'.join(map(str, xml2rfc_gui.main.VERSION)),
    description='Validate and convert XML RFC documents to various output formats',
    long_description="Xml2rfc will allow you to take your XML source (using the format defined in\n"
                     "RFC 2629 and its unofficial successor) and see how the results look like in\n"
                     "the original ASCII look-and-feel or the new modern HTML rendition of that\n"
                     "look-and-feel.",
    author='Concentric Sky',
    author_email='tools-discuss@ietf.org',
    url='http://tools.ietf.org',
    scripts=['bin/xml2rfc-gui'],
    packages=['xml2rfc_gui', 'xml2rfc', 'xml2rfc/writers'],
    package_data={'xml2rfc': ['templates/*',
                              ]},
)
