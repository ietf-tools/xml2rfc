all:	format

format:	README.txt README.html \
	draft-mrose-writing-rfcs.txt draft-mrose-writing-rfcs.html \
	example.txt example.html \
	test.txt

%.txt:	%.xml xml2rfc.tcl
	tclsh xml2rfc.tcl xml2rfc $< $@

%.html:	%.xml xml2rfc.tcl
	tclsh xml2rfc.tcl xml2rfc $< $@
