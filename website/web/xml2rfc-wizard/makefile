DIR=web/xml2rfc-wizard
PUB= $$HOME/public_html/$(DIR)
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
GIF= info.gif x.gif
JS=  prototype.js  xml2rfc-wizard.js
CSS= xml2rfc-wizard.css
HTML= xml2rfc-wizard.html
INS= $(HTML) $(CSS) $(JS) $(GIF)

all:

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
	        sed 's/cgi-bin/..\/cgi-bin/g' < $$i > $(PUB)/$$i; \
	    fi; \
	done

clean:
	rm -f *~

