all: \
	draft-hoffman-rfcexamples-latest.html \
	draft-hoffman-rfcexamples-latest.txt

TOOLS=../../tools

%.html:	%.xml $(TOOLS)/rfc2629.xslt
	saxon -l $< $(TOOLS)/rfc2629.xslt > $@

%.txt:	%.xml $(TOOLS)/rfc2629.xslt
	tclsh xml2rfc.tcl $< $@
