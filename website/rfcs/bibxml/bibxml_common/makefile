DIR=bibxml/bibxml_common
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

EXEFILES=generate-tarball-zipfile gen-rdf-from-resource-xml
OTHERFILES=bibxml_common.py makefile

none:
	@echo make install -- install all files into production

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
