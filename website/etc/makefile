DIR=etc
PUB= $$HOME/public_html/$(DIR)
INS= xml2rfc.tcl xml2rfc-dev.tcl xml2rfc-html2epub-viaxslt \
	wkhtmltopdf-i386 xercesImpl.jar xercesSamples.jar \
	xml2rfc2
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
DERIVATIVES= 

all: $(DERIVATIVES)

install: all
	@for i in $(INS); do \
	    if [ $$i -nt $(WEB)/$$i ];then \
	        echo cp $$i $(WEB)/$$i; \
	        cp $$i $(WEB)/$$i; \
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
	        cp $$i $(PUB)/$$i; \
	    fi; \
	done

clean:
	rm -f *~
