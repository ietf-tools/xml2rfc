all: \
	draft-iab-xml2rfcv2-latest.html \
	draft-iab-xml2rfcv2-latest.unpg.txt \
	draft-iab-xml2rfcv2-latest.txt \
	xml2rfcv2-annotated.rng

TOOLS=../../tools

include xml2rfcvoc.mk

%.html:	%.xml $(TOOLS)/rfc2629.xslt
	saxon -l $< $(TOOLS)/rfc2629.xslt > $@

%.redxml:	%.xml $(TOOLS)/clean-for-DTD.xslt
	saxon -l $< $(TOOLS)/clean-for-DTD.xslt > $@

%.txt:	%.redxml
	tclsh xml2rfc.tcl xml2rfc $< $@

%.unpg.txt:	%.redxml
	tclsh xml2rfc.tcl xml2rfc $< $@.unpg
	mv $@.unpg $@
