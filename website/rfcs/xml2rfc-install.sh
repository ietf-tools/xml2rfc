#!/bin/sh

SRC="$1"
if [ -z "$SRC" ]; then
    echo "usage: xml2rfc-install.sh source directory" 2>&1
    exit 1
fi
if [ ! -d "$SRC" ]; then
    echo "$SRC: not a directory" 2>&1
    exit 1
fi
if [ ! -f "$SRC/xml2rfc.tcl" ]; then
    echo "$SRC: doesn't contain xml2rfc.tcl" 2>&1
    exit 1
fi

VRSN="`basename $SRC | awk -F- '{print $2;}'`"
MAX="`echo $VRSN | awk -F. '{print $1;}'`"
MIN="`echo $VRSN | awk -F. '{print $2;}'`"
if [ -z "$MAX" -o -z "$MIN" ]; then
    echo "$SRC: unable to derive version information" 2>&1
    exit 1
fi
echo "processing xml2rfc: version ${MAX}.${MIN}"

DST="$2"
if [ -z "$DST" ]; then
    DST="`pwd`"
fi
if [ ! -d "$DST" ]; then
    echo "$DST: not a directory" 2>&1
    exit 1
fi
if [ ! -f "$DST/xml2rfc.tgz" ]; then
    echo "$DST: doesn't contain xml2rfc.tgz" 2>&1
    exit 1
fi

ETC="`(cd $SRC ; cd ../../../etc; pwd)`"
if [ ! -d "$ETC" ]; then
    echo "$ETC: not a directory" 2>&1
    exit 1
fi
if [ ! -f "$ETC/mkindex.tcl" ]; then
    echo "$ETC: doesn't contain mkindex.tcl" 2>&1
    exit 1
fi


(
cd $SRC;
cp README.html draft-mrose-writing-rfcs.html sample.xml rfc2629.dtd \
   rfc2629-*.ent rfc2629xslt.zip $DST;
cp xml2rfc.tcl rfc2629.dtd $ETC;

cd ..;
SD="`basename $SRC`"
rm -f $DST/xml2rfc-${MAX}_${MIN}.zip
zip $DST/xml2rfc-${MAX}_${MIN}.zip `find $SD -type f`
)

(
cd $DST;
rm xml2rfc.tgz; ln xml2rfc-${MAX}.${MIN}.tgz xml2rfc.tgz;
rm xml2rfc.zip; ln xml2rfc-${MAX}_${MIN}.zip xml2rfc.zip
)


(
cd $DST;
rm README-dev.html; ln README.html README-dev.html;
rm xml2rfc-dev.tgz; ln xml2rfc.tgz xml2rfc-dev.tgz;
rm xml2rfc-dev.zip; ln xml2rfc.zip xml2rfc-dev.zip
)

(
cd $ETC;
rm xml2rfc-dev.tcl; ln xml2rfc.tcl xml2rfc-dev.tcl
)

echo "now update index.html and experimental.html..."
