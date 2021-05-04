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

SHFILES=gen-bibxml-all
PYFILES=
EXEFILES= $(SHFILES) $(PYFILES)
OTHERFILES=README.txt makefile


none:
	@echo Global targets:
	@echo make all-all -- cd to each directory and make all
	@echo make production-all -- cd to each directory and make production
	@echo make install-all -- cd to each directory and make install
	@echo make clean-all -- cd to each directory and make clean
	@echo make pylint-all -- cd to each directory and make pylint
	@echo make pylint-together -- run pylint on all python programs together
	@echo
	@echo Local targets:
	@echo make install -- install local files into production
	@echo make clean -- clean local files into production
	@echo
	@echo Test targets:
	@echo make test-all -- cd to each directory and make test
	@echo make test -- unit test local files

test:
	chmod a+rx $(PYFILES) $(SHFILES)
	for i in $(PYFILES); do "./$$i" --unit-tests; done
	for i in $(SHFILES); do bash -n "$$i"; done
	for i in $(PYFILES); do "./$$i" --help; done

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

all-all:
	for dir in $(DEVDIRS); do ( cd $$dir && $(MAKE) all ) done

production-all:
	for dir in $(PRODDIRS); do ( cd $$dir && $(MAKE) production ) done

pylint-all:
	for dir in bibxml_common $(PRODDIRS); do ( cd $$dir && $(MAKE) pylint ) done

pylint-together: clean
	pylint `grep -l '#!.*python3' b*/[!#]*[!~] 2>/dev/null`

test-all: test
	ret=0; \
	for dir in bibxml_common $(PRODDIRS); do \
	    ( cd $$dir && $(MAKE) test ) || ret=1; \
	done; \
	exit $$ret

install-all: test-all install
	ret=0; \
	for dir in bibxml_common $(PRODDIRS); do \
	    ( cd $$dir && $(MAKE) install ) || ret=1; \
	done; \
	exit $$ret

clean-all: clean
	for dir in $(DEVDIRS); do ( cd $$dir && $(MAKE) clean ) done
