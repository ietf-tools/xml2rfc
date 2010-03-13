all:	format samples dtd

release=dev

format:	README.txt README.html \
	draft-mrose-writing-rfcs.txt draft-mrose-writing-rfcs.html \
	example.txt example.html \
	test.txt

.PHONY:	dist samples

samples:
	$(MAKE) -C samples
	

%.txt:	%.xml xml2rfc.tcl
	tclsh xml2rfc.tcl xml2rfc $< $@

%.html:	%.xml xml2rfc.tcl
	tclsh xml2rfc.tcl xml2rfc $< $@

dist:
	tools/mdist.sh $(release)

dtd:	rfc2629.rnc rfc2629.rng rfc2629.xsd

%.rng:	%.dtd
	$(MAKE) -C tools
	java -jar tools/trang.jar -I dtd -O rng $< $@

%.rnc:	%.dtd
	$(MAKE) -C tools
	java -jar tools/trang.jar -I dtd -O rnc $< $@

%.xsd:	%.dtd
	$(MAKE) -C tools
	java -jar tools/trang.jar -I dtd -O xsd $< $@
