DIR=bibxml
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)


# DIRS= 
# bibxml-rfcs - working
# bibxml-rfcsubseries - working - 
# bibxml-ids - working - cumulative
# bibxml-ieee - working - uses cached directory - uses auto-clean
# bibxml-nist - working - uses URL - uses auto-clean
# bibxml-w3c - partially working
# bibxml-doi - automatic
# bibxml-iana - automatic
# bibxml-3gpp - working - uses auto-clean - changed the URL

DEVDIRS= bibxml-rfcs bibxml-rfcsubseries bibxml-ids \
	bibxml-ieee bibxml-nist bibxml-w3c bibxml-3gpp

PRODDIRS= bibxml-rfcs bibxml-rfcsubseries bibxml-ids \
	bibxml-ieee bibxml-nist bibxml-w3c bibxml-3gpp

EXEFILES=gen-bibxml-all
OTHERFILES=README.txt makefile


none:
	@echo make all -- cd to each directory and make all
	@echo make production -- cd to each directory and make production
	@echo make install -- install all files into production
	@echo make install-local -- install local files into production

test:
	for dir in $(PRODDIRS) bibxml_common; do \
	    ( cd $$dir && $(MAKE) test ) \
	done

install: test install-local
	for dir in $(PRODDIRS) bibxml_common; do \
	    ( cd $$dir && $(MAKE) install ) \
	done

install-local:
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
	for dir in $(DEVDIRS); do ( cd $$dir && $(MAKE) clean ) done
	rm -f *~

all:
	for dir in $(DEVDIRS); do ( cd $$dir && $(MAKE) all ) done

production:
	for dir in $(PRODDIRS); do ( cd $$dir && $(MAKE) production ) done

