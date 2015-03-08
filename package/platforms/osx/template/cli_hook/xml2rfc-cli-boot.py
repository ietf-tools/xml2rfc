import os
import sys

if __name__ == '__main__':
    resdir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    # Import modules
    sys.path.append(os.path.join(resdir, 'lib', 'python2.7', 'site-packages.zip'))
    # Override templates path
    globals()['_TEMPLATESPATH'] = os.path.join(resdir, 'templates')
    mainscript = os.path.join(resdir, 'xml2rfc-cli.py')
    sys.argv[0] = __file__ = mainscript
    execfile(mainscript, globals(), globals())
