#!/bin/bash

# Handle a missing bibxml3/bibxml-ids reference
# These come in two flavors:
# reference.I-D.draft-chen-rats-usecase-02.xml - version-specific
# reference.I-D.chen-rats-usecase.xml - generic, return the LATEST one
# convert to a reference to the datatracker 

B=$( basename "$0" )
# exec 2>/tmp/"$B".err
# echo "B=$B" 1>&2
# set -x

DTURLBASE=https://datatracker.ietf.org/doc/bibxml3
BIBDIR=/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc
CACHEDIR=/var/cache

badReference()
{
    case "$B" in
	nph-* ) echo "HTTP/1.0 404 Not Found";
    esac
    echo Content-Type: text/plain
    echo
    echo $( basename "$REDIRECT_URL" ) is a bad reference: "$@"
    echo $( basename "$REDIRECT_URL" ) is a bad reference: "$@" 1>&2
    exit
}

goodReference()
{
    file="$1"
    case "$B" in
	nph-* ) echo "HTTP/1.0 200 OK" ;;
    esac
    echo "Content-Type: application/xml; charset=utf-8"
    echo
    cat "$file"
}

echo "REDIRECT_URL=$REDIRECT_URL" 1>&2

case "$REDIRECT_URL" in
    */reference.I-D.*.xml ) ;;
    * ) badReference Malformed name ;;
esac

bref=$( basename "$REDIRECT_URL" )
noref=$( basename "$REDIRECT_URL" .xml | sed 's/^reference[.]I-D[.]//' )
bibdir=$( basename $( dirname "$REDIRECT_URL" ) )

# echo "BIBDIR=$BIBDIR bibdir=$bibdir bref=$bref noref=$noref" 1>&2

TMP=$(mktemp)
TMP2=$(mktemp)
trap 'rm -f "$TMP" "$TMP2"' 0 1 2 3 15

# echo CACHEDFILE= "$CACHEDIR/$bibdir/$bref" 1>&2

# check the cache first
if [ -f "$CACHEDIR/$bibdir/$bref" ]
then
    goodReference "$CACHEDIR/$bibdir/$bref"
    exit
fi

# try retrieving from datatracker
case "$noref" in
    draft-* )
	echo curl "$DTURLBASE/$noref/xml" 1>&2
	curl "$DTURLBASE/$noref/xml" > "$TMP" 2> "$TMP2"
	# cat "$TMP2" 1>&2
	;;
    * )
	echo curl "$DTURLBASE/draft-$noref/xml" 1>&2
	curl "$DTURLBASE/draft-$noref/xml" > "$TMP" 2> "$TMP2"
	# cat "$TMP2" 1>&2
	;;
esac

# check what was retrieved from datatracker
if [ -s "$TMP" ]
then
    if grep "<reference.*anchor" "$TMP" > /dev/null
    then
	goodReference "$TMP"
	# echo "using $BIBDIR/$bibdir" 1>&2
	case "$bibdir" in
	    bibxml* )
		if [ -d "$BIBDIR/$bibdir" ]
		then
		    cp "$TMP" "$CACHEDIR/$bibdir/$bref"
		else
		    echo "$BIBDIR/$bibdir" does not exist 1>&2
		fi
		;;
	esac
    else
	badReference $noref does not seem to exist on the datatracker
    fi
else
    badReference
fi
