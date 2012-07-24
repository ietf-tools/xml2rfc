#!/usr/bin/env python
# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import os
from setuptools import setup

description = 'Validate and convert XML RFC documents to various output ' \
              'formats'

try:
    long_description = open(os.path.join(os.path.dirname(__file__), 
                                         'README.rst')).read()
except Exception:
    long_description = description

setup(
    # Package metadata
    name='xml2rfc',
    version='2.3.7',
    description=description,
    long_description=long_description,
    author='Concentric Sky',
    author_email='tools-discuss@ietf.org',
    url='http://tools.ietf.org/',
    classifiers= [
        'Environment :: Console',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup :: XML',
    ],

    # Program data
    scripts=['scripts/xml2rfc'],
    packages=['xml2rfc', 'xml2rfc/writers'],
    package_data={'xml2rfc': ['templates/*',
                              ]},
                 
    install_requires=['lxml>=2.2.8'],
)
