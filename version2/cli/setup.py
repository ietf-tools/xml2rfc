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
    version='2.3.11',
    author='Josh Bothun (Concentric Sky)',
    author_email='tools-discuss@ietf.org',
    maintainer = "Henrik Levkowetz",
    maintainer_email = "henrik@levkowetz.com",
    url='http://tools.ietf.org/tools/xml2rfc/trac/',
    description=description,
    long_description=long_description,
    download_url = "http://pypi.python.org/pypi/xml2rfc",
    classifiers= [
        'Environment :: Console',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup :: XML',
        'License :: OSI Approved :: BSD License',
    ],
    license="Simplified BSD Licence",

    # Program data
    scripts=['scripts/xml2rfc'],
    packages=['xml2rfc', 'xml2rfc/writers'],
    package_data={'xml2rfc': ['templates/*',
                              ]},

    install_requires=['lxml>2.2.7'],
)
