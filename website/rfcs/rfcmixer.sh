#!/bin/sh

DIR=/www/tools.ietf.org/tools/xml2rfc/rfcs/
SKIPINDEXER=n
SKIPMIXER=n

while getopts d:IM c
do
    case $c in
    d ) DIR="$OPTARG" ;;
    I ) SKIPINDEXER=y ;;
    M ) SKIPMIXER=y ;;
    ? ) usage ;;
    esac
done

cd $DIR

umask 0002

TCLLIBPATH=/www/tools.ietf.org/tools/xml2rfc/rfcs/scripts/
export TCLLIBPATH

function fixlog() {
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
    n )
	cp /dev/null logs/indexer.log

	./rfcindexer.tcl . logs/indexer.log 2>&1 | grep -v "package mime 1.5.1 failed"

	if [ `wc -l logs/indexer.log | awk '{print $1}'` -ne 2 ]; then
	    echo " --- xml2rfc indexer.log --- "
	    cat logs/indexer.log | fixlog
	fi
	;;
esac

# rfcmixer.tcl
#    retrieves rfc-index.txt
#    generates bibxml/*, bibxml3/*, bibxml4/*, bibxml5/*
#    there are also other documents created as a side-affect
# see comments in rfcmixer.tcl for more details
# for bibxml/* (the RFC entries)
#    most of the information comes from rfc-index.txt
#    abstract and DOI comes from rfc-index.xml

case $SKIPMIXER in
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
