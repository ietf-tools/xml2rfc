#!/usr/bin/env python

import os, subprocess

indir = 'ui'
outdir = 'src/ui'

def main():
    if not os.path.exists(outdir):
	print 'Created directory', outdir
	os.makedirs(outdir)
    if not os.path.exists(os.path.join(outdir, '__init__.py')):
	open(os.path.join(outdir, '__init__.py'), 'w').close()	
    for file in os.listdir(indir):
        print '--> Compiling', file
        infile = os.path.join(indir, file)
        outname = os.path.splitext(file)[0] + '.py'
        outfile = os.path.join(outdir, outname)
        subprocess.call(['pyuic4', infile, '-o', outfile])
                        
if __name__ == '__main__':
    main()

