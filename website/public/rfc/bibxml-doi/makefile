# This requires apache2 conf changes to be made to
# /etc/apache2/sites-available/xml2rfc.tools.ietf.org.conf
#	ScriptAlias /public/rfc/bibxml7  /www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml7/nph-index.cgi
#	ScriptAlias /public/rfc/bibxml-doi  /www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml7/nph-index.cgi
#	<Directory "/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/bibxml7/">
#		AllowOverride None
#		Options ExecCGI -MultiViews +SymLinksIfOwnerMatch
#		Order allow,deny
#		Allow from all
#	</Directory>
# sudo /etc/init.d/apache2 reload


DIR=web/public/rfc/bibxml-doi
PUB= $$HOME/public_html/$(DIR)
INS= nph-index.cgi README.md
WEB=/home/www/tools.ietf.org/tools/xml2rfc/$(DIR)
DERIVATIVES= index.cgi

all: $(DERIVATIVES)

index.cgi: nph-index.cgi
	sed 's/nph = 1;/nph = undef;/' < nph-index.cgi > index.cgi

install: all
	@for i in $(INS) $(DERIVATIVES); do \
	    case $$i in \
		ht* ) to=.$$i ;; \
		* ) to=$$i ;; \
	    esac; \
	    if [ ! -f  $(WEB)/$$to -o $$i -nt $(WEB)/$$to ];then \
	        echo cp $$i $(WEB)/$$to; \
	        cp $$i $(WEB)/$$to; \
	        chmod a+x $(WEB)/$$to; \
	    fi; \
	done

diff-install: all
	@for i in $(INS) $(DERIVATIVES); do \
	    case $$i in \
		ht* ) to=.$$i ;; \
		* ) to=$$i ;; \
	    esac; \
	        echo diff $$i $(WEB)/$$to; \
	        diff $$i $(WEB)/$$to; \
	done

test-install: all
	@for i in $(INS) $(DERIVATIVES); do \
	    case $$i in \
		ht* ) to=.$$i ;; \
		* ) to=$$i ;; \
	    esac; \
	    if [ $$i -nt $(PUB)/$$to ];then \
	        echo cp $$i $(PUB)/$$to; \
	        cp $$i $(PUB)/$$to; \
	    fi; \
	done

test:
	./index.cgi reference-DOI.10.1145/1355734.1355746.xml

clean:
	rm -f *~
