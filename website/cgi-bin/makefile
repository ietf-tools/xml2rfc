DIR=cgi-bin
PUB= $$HOME/public_html/$(DIR)
NOCGI=  xml2rfc-dev.cgi xml2rfc-old.cgi xml2rfc-version check-svg.cgi kramdown-version.cgi \
	nph-reanchor.cgi id2xml-version.cgi \
	github2text.cgi github2html.cgi \
	tee-xml2rfc.cgi tee-xml2rfc-dev.cgi
INS=$(NOCGI) cat.cgi xml2rfc.cgi kramdown.cgi id2xml.cgi
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
DERIVATIVES= 

all: $(DERIVATIVES)

install: all
	@for i in $(INS); do \
	    if [ $$i -nt $(WEB)/$$i -o ! -f $(WEB)/$$i ];then \
	        echo cp $$i $(WEB)/$$i; \
	        chmod a+x $$i && cp $$i $(WEB)/$$i ; \
	    fi; \
	done
	@for i in $(NOCGI); do \
	    b=`basename $$i .cgi`; \
	    if [ $$i -nt $(WEB)/$$b -o ! -f $(WEB)/$$b ];then \
	        echo cp $$i $(WEB)/$$b; \
	        chmod a+x $$i && cp $$i $(WEB)/$$b ; \
	    fi; \
	done

diff-install: all
	@for i in $(INS); do \
	        echo diff $$i $(WEB)/$$i; \
	        diff $$i $(WEB)/$$i; \
	done

test-install: all
	@for i in $(INS); do \
	    if [ $$i -nt $(PUB)/$$i ];then \
	        echo cp $$i $(PUB)/$$i; \
	        chmod a+x $$i && cp $$i $(PUB)/$$i; \
	    fi; \
	done

clean:
