#!/usr/bin/env python
# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import os
import re
from codecs import open
from setuptools import setup
import sys

description = "Xml2rfc generates RFCs and IETF drafts from document source in XML according to the dtd in RFC2629."

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README'), encoding='utf-8') as file:
    long_description = file.read()

# Get the requirements from the local requirements.txt file
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as file:
    requirements = file.read().splitlines()

# Check python versions
major, minor = sys.version_info[:2] 
if not ((major == 2 and minor >= 6) or (major == 3 and minor >= 3)):
    print("") 
    print("The xml2rfc installation requires python 2.6, 2.7, or 3.3") 
    print("Can't proceed, quitting.") 
    exit() 

def parse(changelog):
    ver_line = "^([a-z0-9+-]+) \(([^)]+)\)(.*?) *$"
    sig_line = "^ -- ([^<]+) <([^>]+)>  (.*?) *$"

    entries = []
    if type(changelog) == type(''):
        changelog = open(changelog, encoding='utf-8')
    for line in changelog:
        if re.match(ver_line, line):
            package, version, rest = re.match(ver_line, line).groups()
            entry = {}
            entry["package"] = package
            entry["version"] = version
            entry["logentry"] = ""
        elif re.match(sig_line, line):
            author, email, date = re.match(sig_line, line).groups()
            entry["author"] = author
            entry["email"] = email
            entry["datetime"] = date
            entry["date"] = " ".join(date.split()[:3])

            entries += [ entry ]
        else:
            entry["logentry"] += line
    changelog.close()
    return entries

changelog_entry_template = """
Version %(version)s (%(date)s)
------------------------------------------------

%(logentry)s

"""

long_description += """
Changelog
=========

""" + "\n".join([ changelog_entry_template % entry for entry in parse("changelog")[:3] ])

setup(
    # Package metadata
    name='xml2rfc',
    version='2.10.3',
    author='Henrik Levkowetz, Josh Bothun',
    author_email='tools-discuss@ietf.org',
    maintainer = "Henrik Levkowetz",
    maintainer_email = "henrik@levkowetz.com",
    url='https://tools.ietf.org/tools/xml2rfc/trac/',
    description=description,
    long_description=long_description,
    download_url = "https://pypi.python.org/pypi/xml2rfc",
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
    ],
    license="Simplified BSD Licence",

    # Program data
    #scripts=['scripts/xml2rfc'],
    entry_points = {
        'console_scripts' : [
            'xml2rfc = xml2rfc.run:main',
        ],
    },

    packages=['xml2rfc', 'xml2rfc/writers'],
    package_data={'xml2rfc': [
        'templates/*',
        'data/*',
    ]},

    install_requires = requirements,

    zip_safe = False,                   # We're reading templates from a package directory.
)
