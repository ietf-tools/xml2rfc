#!/usr/bin/env python
# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

from setuptools import setup
import xml2rfc

setup(
    name='xml2rfc',
    version='.'.join(map(str, xml2rfc.VERSION)),
    description='Validate and convert XML RFC documents to various output ' \
                  'formats',
    author='Concentric Sky',
    author_email='tools-discuss@ietf.org',
    url='',
    scripts=['scripts/xml2rfc'],
    packages=['xml2rfc', 'xml2rfc/writers'],
    package_data={'xml2rfc': ['templates/*',
                              ]},
                 
    install_requires=['lxml>=2.3'],
)
