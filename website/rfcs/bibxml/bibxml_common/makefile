DIR=bibxml/bibxml_common
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

SHFILES=generate-tarball-zipfile
PYFILES=gen-rdf-from-resource-xml bibxml_common.py
EXEFILES= $(SHFILES) $(PYFILES)
OTHERFILES=makefile

none:
	@echo make install -- install all files into production

test:
	chmod a+rx $(PYFILES) $(SHFILES)
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

test-all:
	cd .. && $(MAKE) test
clean-all:
	cd .. && $(MAKE) clean
install-all:
	cd .. && $(MAKE) install
