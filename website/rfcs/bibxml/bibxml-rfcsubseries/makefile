DIR=bibxml/bibxml-rfcsubseries
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

SHFILES=gen-bibxml-rfcsubseries-all
PYFILES=gen-bibxml-rfcsubseries
EXEFILES= $(SHFILES) $(PYFILES)
OTHERFILES=makefile

PROD_BIBXML_DIR = "/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-rfcsubseries-new"
DEF_BIBXML_DIR = "/home/tonyh/b/bibxml-subseries/bibxml-rfcsubseries-new"

# where to grab the XML information for specific RFCs
REF_BIBXML_DIR = "/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml"

PROD_RFCINDEX = "/home/ietf/rfc/rfc-index.xml"
DEF_RFCINDEX = "/home/ietf/rfc/rfc-index.xml"

PROD_RFCINDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"
DEF_RFCINDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"

none:
	@echo make all
	@echo make production
	@echo make install
	@echo
	@echo Test targets:
	@echo make test
	@echo make pylint
	@echo
	@echo make all-local
	@echo make all-url

all: all-local all-url

all-local:
	./gen-bibxml-rfcsubseries -b $(DEF_BIBXML_DIR)-local -R $(REF_BIBXML_DIR) -r $(DEF_RFCINDEX)
all-url:
	./gen-bibxml-rfcsubseries -b $(DEF_BIBXML_DIR)-url -R $(REF_BIBXML_DIR) -u $(DEF_RFCINDEX_URL)

production:
	./gen-bibxml-rfcsubseries -b $(PROD_BIBXML_DIR) -R $(REF_BIBXML_DIR) -u $(PROD_RFCINDEX_URL)

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
