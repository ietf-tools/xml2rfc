DIR=bibxml/bibxml-ieee
WEB=/home/www/tools.ietf.org/tools/xml2rfc/rfcs/$(DIR)

EXEFILES=gen-bibxml-ieee-all gen-bibxml-ieee-apply-update gen-bibxml-ieee-gen-bibxml gen-bibxml-ieee-get-update
OTHERFILES=makefile

none:
	@echo make all
	@echo make production
	@echo make install
	@echo
	@echo Test targets:
	@echo make get-cache - do not use
	@echo make get-update
	@echo make apply-update - not done yet
	@echo make gen-bibxml

DEFDIR=bibxml-ieee-new
UPDATES=ieee/updates.$$(date +%Y%m%d)
CACHE=ieee/cache
CACHESTD=$(CACHE)/IEEEstd

PRODBASE=/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml-ieee-new
PRODDIR=$(PRODBASE)/bibxml-ieee-new
PRODUPDATES=$(PRODBASE)/ieee/updates.$$(date +%Y%m%d)
PRODCACHE=$(PRODBASE)/ieee/cache
PRODCACHESTD=$(PRODCACHE)/IEEEstd

# NOTE get-cache will no longer work because the site was taken down
get-cache-do-not-use:
	. ~/.bibxml.pswd; \
	./gen-bibxml-ieee-get-update -d ieee-cache -H 'pubftpnew.ieee.org' -U 'guest2' -P '4UpNorth' -v

all: get-update apply-update gen-bibxml-dev
production: get-update-prod apply-update-prod gen-bibxml-prod

get-update:
	. ~/.bibxml.pswd; \
	./gen-bibxml-ieee-get-update -d $(UPDATES) -H "$$IEEEHOST" -U "$$IEEEUSER" -P "$IEEEPSWD"
get-update-prod:
	. ~/.bibxml.pswd; \
	./gen-bibxml-ieee-get-update -d $(PRODUPDATES) -H "$$IEEEHOST" -U "$$IEEEUSER" -P "$IEEEPSWD"

apply-update:
	./gen-bibxml-ieee-apply-update -t -i $(CACHE) -d $(UPDATES)
apply-update-prod:
	./gen-bibxml-ieee-apply-update -t -i $(PRODCACHE) -d $(PRODUPDATES)

gen-bibxml-dev:
	./gen-bibxml-ieee-gen-bibxml -b $(DEFDIR) -i $(CACHESTD) -x
gen-bibxml-prod:
	./gen-bibxml-ieee-gen-bibxml -b $(PRODDIR) -i $(PRODCACHESTD) -x

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
