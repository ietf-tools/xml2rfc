all:	format

format:	sample.ipr.id.noDerivativesTrust200902.200909.txt sample.ipr.id.noDerivativesTrust200902.200909.xml2rfc.html \
	sample.ipr.id.noModification3978.200606.txt sample.ipr.id.noModification3978.200606.xml2rfc.html \
	sample.ipr.id.noModificationTrust200902.200909.txt sample.ipr.id.noModificationTrust200902.200909.xml2rfc.html \
	sample.ipr.id.pre5378Trust200902.200909.txt sample.ipr.id.pre5378Trust200902.200909.xml2rfc.html\
	sample.ipr.id.pre5378Trust200902.200912.txt sample.ipr.id.pre5378Trust200902.200912.xml2rfc.html\
	sample.ipr.id.trust200902.200909.txt sample.ipr.id.trust200902.200909.xml2rfc.html \
	sample.ipr.id.trust200902.200911.txt sample.ipr.id.trust200902.200911.xml2rfc.html \
	sample.ipr.id.trust200902.200912.txt sample.ipr.id.trust200902.200912.xml2rfc.html \
	sample.ipr.rfc.200201.txt sample.ipr.rfc.200201.xml2rfc.html \
	sample.ipr.rfc.200609.txt sample.ipr.rfc.200609.xml2rfc.html \
	sample.ipr.rfc.200808.txt sample.ipr.rfc.200808.xml2rfc.html \
	sample.ipr.rfc.200812.txt sample.ipr.rfc.200812.xml2rfc.html \
	sample.ipr.rfc.200906.txt sample.ipr.rfc.200906.xml2rfc.html \
	sample.ipr.rfc.200907.txt sample.ipr.rfc.200907.xml2rfc.html \
	sample.ipr.rfc.200909.txt sample.ipr.rfc.200909.xml2rfc.html \
	sample.ipr.rfc.200912.txt sample.ipr.rfc.200912.xml2rfc.html \
	sample.ipr.rfc.201001.iab.hist.txt sample.ipr.rfc.201001.iab.hist.xml2rfc.html \
	sample.ipr.rfc.201001.iab.inf.txt sample.ipr.rfc.201001.iab.inf.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.bcp.c.txt sample.ipr.rfc.201001.ietf.bcp.c.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.exp.c.txt sample.ipr.rfc.201001.ietf.exp.c.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.exp.nc.txt sample.ipr.rfc.201001.ietf.exp.nc.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.hist.c.txt sample.ipr.rfc.201001.ietf.hist.c.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.hist.nc.txt sample.ipr.rfc.201001.ietf.hist.nc.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.inf.c.txt sample.ipr.rfc.201001.ietf.inf.c.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.inf.nc.txt sample.ipr.rfc.201001.ietf.inf.nc.xml2rfc.html \
	sample.ipr.rfc.201001.ietf.std.c.txt sample.ipr.rfc.201001.ietf.std.c.xml2rfc.html \
	sample.ipr.rfc.201001.ind.exp.txt sample.ipr.rfc.201001.ind.exp.xml2rfc.html \
	sample.ipr.rfc.201001.ind.hist.txt sample.ipr.rfc.201001.ind.hist.xml2rfc.html \
	sample.ipr.rfc.201001.ind.inf.txt sample.ipr.rfc.201001.ind.inf.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.exp.c.txt sample.ipr.rfc.201001.irtf.exp.c.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.exp.nc.txt sample.ipr.rfc.201001.irtf.exp.nc.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.exp.norg.txt sample.ipr.rfc.201001.irtf.exp.norg.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.hist.c.txt sample.ipr.rfc.201001.irtf.hist.c.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.hist.nc.txt sample.ipr.rfc.201001.irtf.hist.nc.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.hist.norg.txt sample.ipr.rfc.201001.irtf.hist.norg.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.inf.c.txt sample.ipr.rfc.201001.irtf.inf.c.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.inf.nc.txt sample.ipr.rfc.201001.irtf.inf.nc.xml2rfc.html \
	sample.ipr.rfc.201001.irtf.inf.norg.txt sample.ipr.rfc.201001.irtf.inf.norg.xml2rfc.html \
	sample.ipr.id.trust200902.201006.txt sample.ipr.id.trust200902.201006.xml2rfc.html \
	sample.ipr.id.trust200902.201006.ietf.txt sample.ipr.id.trust200902.201006.ietf.xml2rfc.html \
	sample.ipr.id.trust200902.201006.ind.txt sample.ipr.id.trust200902.201006.ind.xml2rfc.html \
	sample.ipr.id.trust200902.201006.iab.txt sample.ipr.id.trust200902.201006.iab.xml2rfc.html \
	sample.ipr.id.trust200902.201006.irtf.txt sample.ipr.id.trust200902.201006.irtf.xml2rfc.html \
	sample.ipr.rfc.pre5378Trust200902.200912.txt sample.ipr.rfc.pre5378Trust200902.200912.xml2rfc.html \
	sample.ref.annotation.txt sample.ref.annotation.xml2rfc.html

%.txt:	%.xml ../xml2rfc.tcl
	tclsh ../xml2rfc.tcl xml2rfc $< $@

%.xml2rfc.html:	%.xml ../xml2rfc.tcl
	tclsh ../xml2rfc.tcl xml2rfc $< $@
