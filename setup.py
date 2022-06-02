#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------
# Copyright The IETF Trust 2011-2022, All Rights Reserved
# -------------------------------------------------------

import os
from codecs import open
from setuptools import setup
import sys
# This workaround is necessary to make setup.py upload work with non-ascii
# arguments to setup().  
try:
    reload(sys).setdefaultencoding("UTF-8") 
except NameError:
    pass

description = "Xml2rfc generates RFCs and IETF drafts from document source in XML according to the IETF xml2rfc v2 and v3 vocabularies."

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

# Get the requirements from the local requirements.txt file
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as file:
    requirements = file.read().splitlines()


setup(
    # Package metadata
    name='xml2rfc',
    author='Henrik Levkowetz',
    author_email='tools-discuss@ietf.org',
    maintainer = "Kesara Rathnayake",
    maintainer_email = "kesara@staff.ietf.org",
    url='https://github.com/ietf-tools/xml2rfc',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url = "https://github.com/ietf-tools/xml2rfc/releases",
    classifiers= [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup :: XML',
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license="BSD-3-Clause",

    # Program data
    #scripts=['scripts/xml2rfc'],
    entry_points = {
        'console_scripts' : [
            'xml2rfc = xml2rfc.run:main',
        ],
    },

    packages=['xml2rfc', 'xml2rfc/writers', 'xml2rfc/util', 'xml2rfc/uniscripts', ],
    package_data={'xml2rfc': [
        'templates/*',
        'data/*',
    ]},

    install_requires = requirements,
    tests_require = [
        'decorator',
        'dict2xml',
        'pycairo',
        'pypdf2',
        'tox',
        'weasyprint',
    ],

    zip_safe = False,                   # We're reading templates from a package directory.
)
