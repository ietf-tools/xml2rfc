DIR=bibxml/bibxml-rfcs
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

PROD_BIBXML_DIR = "/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-rfcs-new"
DEF_BIBXML_DIR = "bibxml-rfcs-new"

DEF_RFC_INDEX = "/home/ietf/rfc/rfc-index.xml"
PROD_RFC_INDEX = "/home/ietf/rfc/rfc-index.xml"

PROD_RFC_INDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"
DEF_RFC_INDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"

EXEFILES=gen-bibxml-rfcs-all gen-bibxml-rfcs-via-rfc-index gen-bibxml-rfcs-via-rsync
OTHERFILES=makefile


none:
	@echo make all -- build locally using rfc-index file and URL
	@echo make production using rfc-index URL
	@echo make install -- install all files into production

all: all-local all-url

all-local:
	./gen-bibxml-rfcs-via-rfc-index -b $(DEF_BIBXML_DIR)-local -r $(DEF_RFC_INDEX) -w -v
all-url:
	./gen-bibxml-rfcs-via-rfc-index -b $(DEF_BIBXML_DIR)-url -u $(DEF_RFC_INDEX_URL) -w -v

production:
	./gen-bibxml-rfcs-via-rfc-index -b $(PROD_BIBXML_DIR) -r $(PROD_RFC_INDEX) -w -v

test:
	@for i in $(EXEFILES); do \
	    case `file $$` in *Python* ) "$$i" --help ;; *shell* ) bash -n "$$i" ;; esac; \
	done

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
