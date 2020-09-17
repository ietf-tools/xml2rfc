# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-

import importlib
import sys
import warnings

warnings.filterwarnings("ignore", message='There are known rendering problems and missing features with cairo < 1.15.4')

errors = 0
for (pname, mname) in [
            ('decorator', 'decorator'),
            ('dict2xml', 'dict2xml'),
            ('pycairo', 'cairo'),
            ('PyPDF2', 'PyPDF2'),
            ('python-fontconfig', 'fontconfig'),
            ('tox', 'tox'),
            ('weasyprint', 'weasyprint'),
        ]:
    try:
        m = importlib.import_module(mname)
    except ModuleNotFoundError:
        errors += 1
        sys.stderr.write("  Missing package: %s\n" % (pname, ))

if errors:
    sys.stderr.write("Not all test requirements are fulfilled")
    sys.exit(errors)

import fontconfig
for (fname, fcount) in [
            ('Noto Serif', 72),
            ('Roboto Mono', 10)
        ]:
    available = fontconfig.query(family=fname)
    acount = len(available)
    if acount < fcount:
        errors += 1
        sys.stderr.write("  Missing fonts: found %s fonts for family %s, but expected at least %s\n" % (acount, fname, fcount))

if errors:
    sys.stderr.write("Not all test requirements are fulfilled")
    sys.exit(errors)

