# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-

import importlib
import sys
import warnings


errors = 0

sys.stderr.write("Checking installation of test and development packages:\n")
for (pname, mname) in [
            ('decorator', 'decorator'),
            ('dict2xml', 'dict2xml'),
            ('PyPDF2', 'PyPDF2'),
        ]:
    try:
        sys.stderr.write("  '%s'...\n" % pname)
        m = importlib.import_module(mname)
    except ImportError:
        errors += 1
        sys.stderr.write("  Missing package: '%s'\n" % (pname, ))

if errors:
    sys.stderr.write("Not all test requirements are fulfilled\n")
    sys.exit(errors)

try:
    import fontconfig
except ImportError:
    sys.stderr.write("Python-fontconfig not installed, will try to use fontconfig command-line tools\n"
                     "Install python-fontconfig for better performance.\n")
    fontconfig = None

for (fname, fcount) in [
            ('Noto Serif', 72),
            ('Roboto Mono', 10)
        ]:
    if fontconfig:
        available = fontconfig.query(family=fname)
        acount = len(available)
    else:
        # try external program

        import subprocess
        done = subprocess.run(["fc-list", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if done.returncode == 0:
            available = done.stdout.decode().splitlines()
            acount = len(available)
        else:
            sys.exit(done.stderr)
    if acount < fcount:
        errors += 1
        sys.stderr.write("  Missing fonts: found %s fonts for family %s, but expected at least %s\n" % (acount, fname, fcount))

if errors:
    sys.stderr.write("Not all test requirements are fulfilled\n")
    sys.exit(errors)

