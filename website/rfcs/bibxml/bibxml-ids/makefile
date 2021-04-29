DIR=bibxml/bibxml-ids
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

EXEFILES=gen-bibxml-ids-all gen-bibxml-ids
OTHERFILES=makefile

PROD_BIBXML_DIR = "/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-ids-new"
DEF_BIBXML_DIR = "bibxml-ids-new"

PROD_IDINDEX = "/home/ietf/internet-drafts/1id-abstracts.txt"
DEF_IDINDEX2 = "/home/ietf/internet-drafts/1id-index.txt"
DEF_IDINDEX= 1id-subset
DEF_IDINDEX = "/home/ietf/internet-drafts/1id-abstracts.txt"

none:
	@echo make all
	@echo make production
	@echo make install -- install all files into production

all:
	./gen-bibxml-ids -v -B -b $(DEF_BIBXML_DIR) -i $(DEF_IDINDEX)

production:
	./gen-bibxml-ids -v -B -b $(PROD_BIBXML_DIR) -i $(PROD_IDINDEX)

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
