all: \
	draft-hoffman-xml2rfc-latest.html \
	draft-hoffman-xml2rfc-latest.redxml \
	draft-hoffman-xml2rfc-latest.unpg.txt \
	draft-hoffman-xml2rfc-latest.txt

TOOLS=../../tools

include xml2rfcvoc.mk

%.html:	%.xml $(TOOLS)/rfc2629.xslt myxml2rfc.xslt
	saxon -l $< myxml2rfc.xslt > $@

%.redxml:	%.xml $(TOOLS)/clean-for-DTD.xslt
	saxon -l $< $(TOOLS)/clean-for-DTD.xslt > $@

%.txt:	%.redxml
	tclsh xml2rfc.tcl xml2rfc $< $@

%.unpg.txt:	%.redxml
	tclsh xml2rfc.tcl xml2rfc $< $@.unpg
	mv $@.unpg $@
