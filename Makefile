all:	format samples

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
	mdist.sh $(release)
