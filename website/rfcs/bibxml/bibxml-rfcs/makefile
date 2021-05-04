DIR=bibxml/bibxml-rfcs
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

PROD_BIBXML_DIR = "/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-rfcs-new"
DEF_BIBXML_DIR = "bibxml-rfcs-new"

DEF_RFC_INDEX = "/home/ietf/rfc/rfc-index.xml"
PROD_RFC_INDEX = "/home/ietf/rfc/rfc-index.xml"

PROD_RFC_INDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"
DEF_RFC_INDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"

SHFILES=gen-bibxml-rfcs-all gen-bibxml-rfcs-via-rsync
PYFILES=gen-bibxml-rfcs-via-rfc-index
EXEFILES= $(SHFILES) $(PYFILES)
OTHERFILES=makefile


none:
	@echo make all -- build locally using rfc-index file and URL
	@echo make production using rfc-index URL
	@echo make install -- install local files into production
	@echo make clean -- clean local files into production
	@echo
	@echo Test targets:
	@echo make test -- unit test local files
	@echo make pylint -- run pylint on python scripts

all: all-local all-url

all-local:
	./gen-bibxml-rfcs-via-rfc-index -b $(DEF_BIBXML_DIR)-local -r $(DEF_RFC_INDEX) -w -v
all-url:
	./gen-bibxml-rfcs-via-rfc-index -b $(DEF_BIBXML_DIR)-url -u $(DEF_RFC_INDEX_URL) -w -v

production:
	./gen-bibxml-rfcs-via-rfc-index -b $(PROD_BIBXML_DIR) -r $(PROD_RFC_INDEX) -w -v

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
