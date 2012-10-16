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
    description='Graphical version of xml2rfc written in Qt and Python',
    author='Concentric Sky',
    author_email='tools-discuss@ietf.org',
    url='http://tools.ietf.org',
    scripts=['xml2rfc-gui'],
    packages=['xml2rfc_gui', 'xml2rfc', 'xml2rfc/writers'],
    package_data={'xml2rfc': ['templates/*',
                              ]},
    install_requires=['lxml>=2.2.8'],
)
