#!/usr/bin/env python

import os, subprocess

indir = 'ui'
outdir = 'xml2rfc_gui'

def main():
    if not os.path.exists(outdir):
    	print 'Created directory', outdir
    	os.makedirs(outdir)
    for file in (f for f in os.listdir(indir) if f.endswith('.ui')):
        infile = os.path.join(indir, file)
        outname = 'ui_' + os.path.splitext(file)[0] + '.py'
        outfile = os.path.join(outdir, outname)
        print 'Compiling', infile, '\n      -->', outfile
        subprocess.call(['pyuic4', infile, '-o', outfile])
                        
if __name__ == '__main__':
    main()
