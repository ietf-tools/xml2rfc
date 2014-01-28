all: \
	draft-reschke-xml2rfc-latest.html \
	draft-reschke-xml2rfc-latest.txt

TOOLS=../../tools/

include xml2rfcvoc.mk

%.html:	%.xml $(TOOLS)/rfc2629.xslt $(TOOLS)/clean-for-DTD.xslt
	saxon -l $< $(TOOLS)/rfc2629.xslt > $@

%.txt:	%.xml xml2rfc.tcl $(TOOLS)/clean-for-DTD.xslt $(TOOLS)/rfc2629.xslt
	saxon $< $(TOOLS)/clean-for-DTD.xslt > $@.tmp
	tclsh xml2rfc.tcl xml2rfc $@.tmp $@
	rm -f $@.tmp
