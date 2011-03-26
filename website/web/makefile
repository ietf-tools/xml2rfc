DIR=web
PUB= $$HOME/public_html/$(DIR)
INS= experimental-debug.html experimental.html index.html stripe.png xml2rfcFAQ.html
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
DERIVATIVES= experimental-debug.html index-debug.html

all: $(DERIVATIVES)

experimental-debug.html: experimental.html
	sed < experimental.html -e '/start debug section/s/!-- tr/tr/' -e '/end debug section/s/ --//' > experimental-debug.html

index-debug.html: index.html
	sed < index.html -e '/start debug section/s/!-- tr/tr/' -e '/end debug section/s/ --//' > index-debug.html

install: all
	@for i in $(INS); do \
	    if [ $$i -nt $(WEB)/$$i ];then \
	        echo cp $$i $(WEB)/$$i; \
	        cp $$i $(WEB)/$$i; \
	    fi; \
	done

authoring-install:
	TMP1=/var/tmp/m1.$$$$ ; \
	TMP2=/var/tmp/m2.$$$$ ; \
	( cd $(WEB)/authoring && find . -print | fgrep -v '/.svn' | sort > $$TMP1 ) ; \
	cd authoring && find . -print | fgrep -v '/.svn' | sort > $$TMP2 ; \
	comm -13 $$TMP1 $$TMP2 | \
	cpio -pdmv $(WEB)/authoring

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
	rm -f $(DERIVATIVES)
