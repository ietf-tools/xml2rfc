# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

#svnrev	:= $(shell svn info | grep ^Revision | awk '{print $$2}' )
datetime_regex = [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T_ ][0-9][0-9]:[0-9][0-9]:[0-9][0-9]
version_regex =  [Vv]ersion [2N]\(\.[0-9N]\+\)\+\(\.dev\)\?


bin/python:
	echo "Install virtualenv here ($$PWD) in order to run tests locally."

install:
	python --version
	python setup.py --quiet install --skip-build
	rm -rf xml2rfc.egg-info/

test:	install flaketests pytests

flaketests:
	pyflakes xml2rfc
	[ -d tests/failed/ ] && rm -f tests/failed/*

pytests:
	python test.py --verbose

CHECKOUTPUT=	\
	groff -ms -Tascii tmp/$$doc.nroff | ./fix.pl | $$postnrofffix > tmp/$$doc.nroff.txt ; \
	for type in .raw.txt .txt .nroff .html .exp.xml ; do \
	diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/$$doc$$type tmp/$$doc$$type || { echo "Diff failed for $$doc$$type output"; exit 1; } \
	done ; \
	diff -I '$(datetime_regex)' -I '$(version_regex)' tmp/$$doc.nroff.txt tmp/$$doc.txt || { echo 'Diff failed for .nroff.txt output'; exit 1; }

drafttest: cleantmp install
	@ xml2rfc --cache tests/cache --no-network tests/input/draft-template.xml --base tmp/ --raw --text --nroff --html --exp
	doc=draft-template ; postnrofffix="sed 1,2d" ; $(CHECKOUTPUT)

miektest: cleantmp install
	@ xml2rfc --cache tests/cache --no-network tests/input/draft-miek-test.xml --base tmp/ --raw --text --nroff --html --exp
	doc=draft-miek-test ; postnrofffix="sed 1,2d" ; $(CHECKOUTPUT)

cachetest: cleantmp install
	@ echo "Clearing cache ..."
	@ xml2rfc --cache .cache --clear-cache
	@ echo "Filling cache ..."
	@ xml2rfc --cache .cache tests/input/rfc6787.xml --base tmp/ --raw
	@ echo "Running without accessing network ..."
	@ xml2rfc --cache .cache tests/input/rfc6787.xml --no-network --base tmp/ --raw

rfctest: cleantmp bin/python install
	@ xml2rfc --cache tests/cache --no-network tests/input/rfc6787.xml --base tmp/ --raw --text --nroff --html --exp
	doc=rfc6787 ; postnrofffix="cat" ; $(CHECKOUTPUT)

unicodetest: cleantmp  bin/python install
	@ xml2rfc --cache tests/cache --no-network tests/input/unicode.xml --base tmp/ --raw --text --nroff --html --exp
	doc=unicode ; postnrofffix="sed 1,2d" ; $(CHECKOUTPUT)

cleantmp:
	[ -d tmp ] || mkdir -p tmp
	[ -d tmp ] && rm -f tmp/*

tests: test regressiontests cachetest

noflakestests: install pytests regressiontests

regressiontests: drafttest miektest rfctest

test2:	test
	@ xml2rfc --cache tests/cache --no-network tests/input/rfc6635.xml --text --out tmp/rfc6635.txt	&& diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6635.txt tmp/rfc6635.txt 

upload:
	rst2html changelog > /dev/null	# verify that the changelog is valid rst
	python setup.py sdist upload --sign
	python setup.py install
	rsync dist/xml2rfc-$(shell xml2rfc --version).tar.gz /www/tools.ietf.org/tools/xml2rfc2/cli/
	toolpush /www/tools.ietf.org/tools/xml2rfc2/cli/


changes:
	svn log -r HEAD:950 | sed -n -e 's/^/  * /' -e '1,/^  \* Set version info and settings back to development mode/p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | tac | sed 's/$$/\n/' | fold -s -w 76 | sed -r 's/^([^ ])/    \1/'
