all: \
	draft-reschke-xml2rfc-latest.html \
	draft-reschke-xml2rfc-latest.txt

include xml2rfcvoc.mk

%.html:	%.xml ../../tools/rfc2629.xslt ../../tools/clean-for-DTD.xslt
	saxon $< ../../tools/clean-for-DTD.xslt > $@.check
	rm -f $@.check
	saxon -l $< ../../tools/rfc2629.xslt > $@

%.txt:	%.xml xml2rfc.tcl clean-for-DTD.xslt rfc2629.xslt
	saxon $< ../../tools/clean-for-DTD.xslt > $@.tmp
	tclsh xml2rfc.tcl xml2rfc $@.tmp $@
	rm -f $@.tmp

