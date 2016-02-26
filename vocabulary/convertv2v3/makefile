

all: 

clean:
	rm -f *.pyc *~

ETC=etc
CGI=cgi-bin
PUB= $$HOME/public_html/$(ETC)
INSETC= convertv2v3
INSCGI= convertv2v3.cgi
WEB=/home/www/tools.ietf.org/tools/xml2rfc/

install: all install_only

install_only:
	@for i in $(INSETC); do \
	    if [ $$i -nt $(WEB)/$(ETC)/$$i ];then \
	        echo cp $$i $(WEB)/$(ETC)/$$i; \
	        cp $$i $(WEB)/$(ETC)/$$i; \
	    fi; \
	done
	@for i in $(INSCGI); do \
	    if [ $$i -nt $(WEB)/$(CGI)/$$i ];then \
	        echo cp $$i $(WEB)/$(CGI)/$$i; \
	        cp $$i $(WEB)/$(CGI)/$$i; \
	    fi; \
	done

diff-install: all
	@for i in $(INSETC); do \
	        echo diff $$i $(WEB)/$(ETC)/$$i; \
	        diff $$i $(WEB)/$(ETC)/$$i; \
	done
	@for i in $(INSCGI); do \
	        echo diff $$i $(WEB)/$(CGI)/$$i; \
	        diff $$i $(WEB)/$(CGI)/$$i; \
	done

test-install: all
	@for i in $(INSETC); do \
	    if [ $$i -nt $(PUB)/$(ETC)/$$i ];then \
	        echo cp $$i $(PUB)/$(ETC)/$$i; \
	        cp $$i $(PUB)/$(ETC)/$$i; \
	    fi; \
	done
	@for i in $(INSCGI); do \
	    if [ $$i -nt $(PUB)/$(CGI)/$$i ];then \
	        echo cp $$i $(PUB)/$(CGI)/$$i; \
	        cp $$i $(PUB)/$(CGI)/$$i; \
	    fi; \
	done

