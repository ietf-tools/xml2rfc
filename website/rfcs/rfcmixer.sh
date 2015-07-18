#!/bin/sh

XML2RFC=/www/tools.ietf.org/tools/xml2rfc
DIR=$XML2RFC/rfcs/
BIBDIR=$XML2RFC/web/public/rfc

SKIPINDEXER=n
SKIPMIXER=n
SKIPRSYNC=n

usage()
{
    exec 1>&2
    echo "Usage: $0 [-d directory] [-I] [-M] [-v]"
    echo "-d dir\trun in this directory instead of $WWW"
    echo "-I\tskip the indexer step"
    echo "-M\tskip the mixer step"
    echo "-R\tskip the bibxml rsync step"
    echo "-v\tbe verbose"
}

while getopts d:IMRv c
do
    case $c in
	d ) DIR="$OPTARG" ;;
	I ) SKIPINDEXER=y ;;
	M ) SKIPMIXER=y ;;
	R ) SKIPRSYNC=y ;;
	v ) set -x ;;
	? ) usage ;;
    esac
done

cd $DIR

umask 0002

PATH=$PATH:$DIR

case $SKIPRSYNC in
    y ) echo "Skipping rsync from rfc-editor for bibxml" ;;
    n )
	mkBibxml -v -t $BIBDIR -1 bibxml > logs/mkBibxml.log 2> logs/mkBibxml.err
	;;
esac

TCLLIBPATH=$DIR/scripts/
export TCLLIBPATH

fixlog() {
python -c ' 
import sys
for line in sys.stdin:
    try:
	f = line.strip().split()
	print f[1], f[5], f[6].split("/")[-1], " ".join(f[7:])
    except IndexError:
	print line
'
}

# rfcindexer.tcl:
#    retrieves rfc-index.xml
#    parses rfc-index.xml to create data/rfc-index.tcl

case $SKIPINDEXER in
    y ) echo "Skipping invocation of rfcindexer.tcl" ;;
    n )
	cp /dev/null logs/indexer.log

	./rfcindexer.tcl . logs/indexer.log 2>&1 | grep -v "package mime 1.5.1 failed"

	if [ "`wc -l logs/indexer.log | awk '{print $1}'`" -ne 2 ]; then
	    echo " --- xml2rfc indexer.log --- "
	    cat logs/indexer.log | fixlog
	fi
	;;
esac

# rfcmixer.tcl
#    retrieves rfc-index.txt
#    generates bibxml.old/*, bibxml3/*, bibxml4/*, bibxml5/*
#    there are also other documents created as a side-affect
# see comments in rfcmixer.tcl for more details
# for bibxml.old/* (the RFC entries)
#    most of the information comes from rfc-index.txt
#    abstract and DOI comes from rfc-index.xml

case $SKIPMIXER in
    y ) echo "Skipping invocation of rfcmixer.tcl" ;;
    n )
	cp /dev/null logs/mixer.log

	./rfcmixer.tcl . unused mixer.rfc xml.resource.org logs/mixer.log 2>&1 | grep -v "package mime 1.5.1 failed"

	if grep "error" logs/mixer.log; then
	    echo " --- xml2rfc mixer.log --- "
	    grep -v "futuristic" logs/mixer.log | fixlog
	    #cat logs/mixer.log
	fi
	;;
esac
