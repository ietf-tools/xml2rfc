DIR=bibxml/bibxml-nist
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

EXEFILES=gen-bibxml-nist-all gen-bibxml-nist
OTHERFILES=makefile

none:
	@echo make all
	@echo make production
	@echo make install
	@echo
	@echo Test targets:
	@echo make getxls
	@echo make geturl
	@echo make dumpjson
	@echo make check-removals
	@echo make do-removals
	@echo make gen-xmls

URL= https://pages.nist.gov/NIST-Tech-Pubs/NIST_Tech_Pubs_all.xlsx
DEFDIR=bibxml-nist-new
PRODDIR="/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-nist-new"

# download the spreadsheet and then process it
all:
	./gen-bibxml-nist -u $(URL) -f /tmp/x.xlsx -b $(DEFDIR) -c
production:
	./gen-bibxml-nist -v -u $(URL) -b $(PRODDIR) -c

install:
	@for i in $(EXEFILES); do \
	    if [ $$i -nt $(WEB)/$$i -o ! -f $(WEB)/$$i ];then \
	        echo cp -p $$i $(WEB)/$$i; \
	        chmod a+rx $$i && cp -p $$i $(WEB)/$$i ; \
	    fi; \
	done
	@for i in $(OTHERFILES); do \
	    if [ $$i -nt $(WEB)/$$i -o ! -f $(WEB)/$$i ];then \
	        echo cp -p $$i $(WEB)/$$i; \
	        chmod a+r,a-x $$i && cp -p $$i $(WEB)/$$i ; \
	    fi; \
	done

clean:
	rm -f *~

# TESTS

all-but-xlsx:
	./gen-bibxml-nist -u $(URL) -b $(DEFDIR) -c -v -j /tmp/x.json

# download the spreadsheet
geturl:
	./gen-bibxml-nist -u $(URL) -f /tmp/x.xlsx

# convert the spreadsheet to a readable json file
dumpjson:
	./gen-bibxml-nist -f /tmp/x.xlsx -j /tmp/x.json

# convert the spreadsheet to a readable yaml file
dumpyaml:
	./gen-bibxml-nist -f /tmp/x.xlsx -y /tmp/x.yaml

# convert the spreadsheet to a readable csv file
dumpcsv:
	./gen-bibxml-nist -f /tmp/x.xlsx -C /tmp/x.csv

# show which files would be removed, when not in the spreadsheet
check_removals:
	./gen-bibxml-nist -f /tmp/x.xlsx -c -s -b $(DEFDIR) -S

# remove any files not in the spreadsheet
do_removals:
	./gen-bibxml-nist -f /tmp/x.xlsx -c -s -b $(DEFDIR)

# update the bibxml-nist directory based on the spreadsheet
gen-xmls:
	./gen-bibxml-nist -v -f /tmp/x.xlsx -b $(DEFDIR) -c

# same as above, adding -v
gen-xmls-v:
	./gen-bibxml-nist -f /tmp/x.xlsx -b $(DEFDIR) -c -v
