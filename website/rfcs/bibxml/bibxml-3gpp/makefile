DIR=bibxml/bibxml-3gpp
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

SHFILES=gen-bibxml-3gpp-all
PYFILES=gen-bibxml-3gpp
EXEFILES= $(SHFILES) $(PYFILES)
OTHERFILES=makefile

none:
	@echo make all
	@echo make production
	@echo make install
	@echo
	@echo Test targets:
	@echo make test
	@echo make pylint
	@echo
	@echo make geturl
	@echo make dumpjson
	@echo make check-removals
	@echo make do-removals
	@echo make gen-xmls

# URL was https://www.3gpp.org/ftp/Specs/html-info/2003-04-10_webexp11a_status-report_special_select.txt, 
# which currently redirects to https://www.3gpp.org/DynaReport/2003-04-10_webexp11a_status-report_special_select.txt
# but gives a 404. Found the file at this location:
# ftp://www.3gpp.org/Specs/html-info/2003-04-10_webexp11a_status-report_special_select.txt
# TODO - figure out how to deal with standards updates since 2013.

URL= ftp://www.3gpp.org/Specs/html-info/2003-04-10_webexp11a_status-report_special_select.txt
DEFDIR=bibxml-3gpp-new
PRODDIR="/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-3gpp-new"

# download the spreadsheet and then process it
all:
	./gen-bibxml-3gpp -v -f /tmp/3g.txt -b $(DEFDIR) -c
	# ./gen-bibxml-3gpp -v -u $(URL) -f /tmp/3g.txt -b $(DEFDIR) -c

production:
	./gen-bibxml-3gpp -v -u $(URL) -b $(PRODDIR) -c

test:
	for i in $(PYFILES); do "./$$i" --unit-tests; done
	for i in $(SHFILES); do bash -n "$$i"; done
	for i in $(PYFILES); do "./$$i" --help; done

pylint:
	PYTHONPATH=../bibxml_common pylint --rcfile=../.pylintrc $(PYFILES)

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

################ test targets ################

# download the spreadsheet
geturl:
	./gen-bibxml-3gpp -u $(URL) -f /tmp/3g.txt

# show which files would be removed, when not in the spreadsheet
check_removals:
	./gen-bibxml-3gpp -f /tmp/3g.txt -c -s -b $(DEFDIR) -S

# remove any files not in the text file
do_removals:
	./gen-bibxml-3gpp -f /tmp/3g.txt -c -s -b $(DEFDIR)

# update the bibxml-3gpp directory based on the text file
gen-xmls:
	./gen-bibxml-3gpp -v -f /tmp/3g.txt -b $(DEFDIR) -c

# same as above, adding -v
gen-xmls-v:
	./gen-bibxml-3gpp -f /tmp/3g.txt -b $(DEFDIR) -c -v

