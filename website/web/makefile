DIR=web
PUB= $$HOME/public_html/$(DIR)
CSS= xml2rfc.css xml2rfc-experimental.css xml2rfc-old.css
PNG= blue-stripe.png stripe.png
HTML= experimental.html index.html old.html xml2rfcFAQ.html rfc7749.html
INS= $(HTML) $(PNG) $(CSS)
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
DERIVATIVES= experimental-debug.html index-debug.html old-debug.html \
	experimental-new.html experimental-new-debug.html \
	experimental-tee.html experimental-tee-debug.html \

all: $(DERIVATIVES)

experimental-debug.html: experimental.html
	sed < experimental.html -e '/start debug section/s/!-- ! tr/tr/' -e '/end debug section/s/ --//' > experimental-debug.html

experimental-new.html: experimental.html
	sed 's/xml2rfc-dev.cgi/xml2rfc-new.cgi/' < experimental.html > experimental-new.html

experimental-new-debug.html: experimental-debug.html
	sed 's/xml2rfc-dev.cgi/xml2rfc-new.cgi/' < experimental-debug.html > experimental-new-debug.html

experimental-tee.html: experimental.html
	sed 's/xml2rfc-dev.cgi/xml2rfc-tee.cgi/' < experimental.html > experimental-tee.html

experimental-tee-debug.html: experimental-debug.html
	sed 's/xml2rfc-dev.cgi/xml2rfc-tee.cgi/' < experimental-debug.html > experimental-tee-debug.html

index-debug.html: index.html
	sed < index.html -e '/start debug section/s/!-- ! //' -e '/end debug section/s/ --//' > index-debug.html

old-debug.html: old.html
	sed < old.html -e '/start debug section/s/!-- ! //' -e '/end debug section/s/ --//' > old-debug.html

install: all
	@XML2RFC2VERSION=`/usr/local/bin/xml2rfc --version`; \
	for i in $(INS) $(DERIVATIVES); do \
	    if [ $$i -nt $(WEB)/$$i ];then \
	        : echo cp $$i $(WEB)/$$i; \
	        echo sed "s/XML2RFC2VERSION/$$XML2RFC2VERSION/g" '<' $$i '>' $(WEB)/$$i; \
	        sed "s/XML2RFC2VERSION/$$XML2RFC2VERSION/g" < $$i > $(WEB)/$$i; \
	    fi; \
	done
	( cd ../.. && svn log ) > $(WEB)/authoring/xml2rfc2-dev.log

install-dev: all
	cp experimental.html $(WEB)/experimental-dev.html
	cp experimental-debug.html $(WEB)/experimental-dev-debug.html

authoring-install:
	cd authoring && find . -print | fgrep -v '/.svn' | cpio -pdmv $(WEB)/authoring

diff-install: all
	@for i in $(INS) $(DERIVATIVES); do \
	        echo diff $$i $(WEB)/$$i; \
	        diff $$i $(WEB)/$$i; \
	done

test-install: all
	@for i in $(INS) $(DERIVATIVES); do \
	    if [ $$i -nt $(PUB)/$$i ];then \
	        echo cp $$i $(PUB)/$$i; \
	        sed 's/cgi-bin/..\/cgi-bin/g' < $$i > $(PUB)/$$i; \
	    fi; \
	done

clean:
	rm -f $(DERIVATIVES)
