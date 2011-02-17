DIR=web
PUB= $$HOME/public_html/$(DIR)
INS= experimental-debug.html experimental.html index.html stripe.png xml2rfcFAQ.html
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
DERIVATIVES= experimental-debug.html

all: $(DERIVATIVES)

experimental-debug.html: experimental.html
	sed < experimental.html -e '/start debug section/s/!-- tr/tr/' -e '/end debug section/s/ --//' > experimental-debug.html

install:
	@for i in $(INS); do \
	    if [ $$i -nt $(WEB)/$$i ];then \
	        echo cp $$i $(WEB)/$$i; \
	        cp $$i $(WEB)/$$i; \
	    fi; \
	done

diff-install:
	@for i in $(INS); do \
	        echo diff $$i $(WEB)/$$i; \
	        diff $$i $(WEB)/$$i; \
	done

test-install:
	@for i in $(INS); do \
	    if [ $$i -nt $(PUB)/$$i ];then \
	        echo cp $$i $(PUB)/$$i; \
	        cp $$i $(PUB)/$$i; \
	    fi; \
	done

clean:
      rm -f $(DERIVATIVES)
