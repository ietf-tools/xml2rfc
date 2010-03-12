all:	format samples

format:	README.txt README.html \
	draft-mrose-writing-rfcs.txt draft-mrose-writing-rfcs.html \
	example.txt example.html \
	test.txt

.PHONY:	samples
samples:
	$(MAKE) -C samples
	

%.txt:	%.xml xml2rfc.tcl
	tclsh xml2rfc.tcl xml2rfc $< $@

%.html:	%.xml xml2rfc.tcl
	tclsh xml2rfc.tcl xml2rfc $< $@
