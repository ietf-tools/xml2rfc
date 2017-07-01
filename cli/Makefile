# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

#svnrev	:= $(shell svn info | grep ^Revision | awk '{print $$2}' )
datetime_regex = [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T_ ][0-9][0-9]:[0-9][0-9]:[0-9][0-9]
version_regex =  [Vv]ersion [2N]\(\.[0-9N]\+\)\+\(\.dev\)\?


rfcxml= \
	rfc6787.xml		\
	rfc7911.xml		\
#	rfc7754.edited.xml	\

rfcxmlfiles = $(addprefix tests/input/, $(rfcxml))
rfctxt      = $(addsuffix .txt, $(basename $(rfcxml)))
rfctest     = $(addsuffix .tests, $(basename $(rfcxml)))
rfctxtfiles = $(addprefix tests/out/, $(rfctxt))
rfctests    = $(addprefix tests/out/, $(rfctest))

pyfiles  = $(wildcard  xml2rfc/*.py) $(wildcard  xml2rfc/writers/*.py)


env/bin/python:
	echo "Install virtualenv in $$PWD/env/ in order to run tests locally."

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
	groff -ms -K$$type -T$$type tmp/$$doc.nroff | ./fix.pl | $$postnrofffix > tmp/$$doc.nroff.txt ;	\
	for type in .raw.txt .txt .nroff .html .exp.xml .v2v3.xml ; do					\
	  diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/$$doc$$type tmp/$$doc$$type || { echo "Diff failed for $$doc$$type output"; exit 1; } \
	done ; if [ $$type = ascii ]; then echo "Diff nroff output with xml2rfc output:";\
	diff -I '$(datetime_regex)' -I '$(version_regex)' tmp/$$doc.nroff.txt tmp/$$doc.txt || { echo 'Diff failed for .nroff.txt output'; exit 1; }; fi

# ----------------------------------------------------------------------
#
# Generic rules

%.tests: %.txt.test %.raw.txt.test %.nroff.test %.html.test %.exp.xml.test %.nroff.txt %.v2v3.xml.test
	@echo "Diffing .nroff.txt against "
	doc=$(basename $@); diff -I '$(datetime_regex)' -I '$(version_regex)' $$doc.nroff.txt $$doc.txt || { echo 'Diff failed for $$doc.nroff.txt output'; exit 1; }
	@echo checking v3 validity
	doc=$(basename $@); xmllint --noout --relaxng xml2rfc/data/v3.rng $$doc.v2v3.xml

tests/out/%.txt tests/out/%.raw.txt tests/out/%.nroff tests/out/%.html tests/out/%.txt tests/out/%.exp.xml tests/out/%.v2v3.xml: tests/input/%.xml install
	@ echo "\nProcessing $<"
	xml2rfc --cache tests/cache --no-network $< --base tests/out/ --raw --text --nroff --html --exp --v2v3

%.test: %
	@echo "Diffing $< against master"
	diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/$(notdir $<) $< || { echo "Diff failed for $< output"; exit 1; }

%.nroff.txt: %.nroff
	groff -ms -Kascii -Tascii $< | ./fix.pl > $@

# ----------------------------------------------------------------------

drafttest: cleantmp install
	@ xml2rfc --cache tests/cache --no-network tests/input/draft-template.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
	doc=draft-template ; postnrofffix="sed 1,2d" ; type=ascii; $(CHECKOUTPUT)

miektest: cleantmp install
	@ xml2rfc --cache tests/cache --no-network tests/input/draft-miek-test.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
	doc=draft-miek-test ; postnrofffix="sed 1,2d" ; type=ascii; $(CHECKOUTPUT)

cachetest: cleantmp install
	@ echo "Clearing cache ..."
	@ xml2rfc --cache .cache --clear-cache
	@ echo "Filling cache ..."
	@ xml2rfc --cache .cache tests/input/rfc6787.xml --base tmp/ --raw
	@ echo "Running without accessing network ..."
	@ xml2rfc --cache .cache tests/input/rfc6787.xml --no-network --base tmp/ --raw


rfctest: cleantmp env/bin/python install $(rfctests)

# rfctest: cleantmp env/bin/python install $(rfctests)
# 	@ xml2rfc --cache tests/cache --no-network tests/input/rfc6787.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
# 	doc=rfc6787 ; postnrofffix="cat" ; type=ascii; $(CHECKOUTPUT)
# 	@ xml2rfc --cache tests/cache --no-network tests/input/rfc7754.edited.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
# 	doc=rfc7754.edited ; postnrofffix="cat" ; type=ascii; $(CHECKOUTPUT)
# 	@ xml2rfc --cache tests/cache --no-network tests/input/rfc7911.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
# 	doc=rfc7911 ; postnrofffix="cat" ; type=ascii; $(CHECKOUTPUT)

unicodetest: cleantmp  env/bin/python install
	@ xml2rfc --cache tests/cache --no-network tests/input/unicode.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
	doc=unicode ; postnrofffix="sed 1,2d" ; type=ascii; $(CHECKOUTPUT)

utf8test: cleantmp  env/bin/python install
	@ xml2rfc --cache tests/cache --no-network --utf8 tests/input/utf8.xml --base tmp/ --raw --text --nroff --html --exp --v2v3
	doc=utf8 ; postnrofffix="cat" ; type=utf8; $(CHECKOUTPUT)

cleantmp:
	[ -d tmp ] || mkdir -p tmp
	[ -d tmp ] && rm -f tmp/*
	[ -d tests/out ] || mkdir -p tests/out
	[ -d tests/out ] && rm -f tests/out/* && cp xml2rfc/templates/rfc2629* tests/out/


tests: test regressiontests cachetest drafttest miektest

noflakestests: install pytests regressiontests

regressiontests: drafttest miektest rfctest

test2:	test
	@ xml2rfc --cache tests/cache --no-network tests/input/rfc6635.xml --text --out tmp/rfc6635.txt	&& diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6635.txt tmp/rfc6635.txt 

upload: install
	rst2html changelog > /dev/null	# verify that the changelog is valid rst
	python setup.py sdist upload --sign
	python setup.py install
	rsync dist/xml2rfc-$(shell xml2rfc --version).tar.gz /www/tools.ietf.org/tools/xml2rfc2/cli/ || true
	toolpush /www/tools.ietf.org/tools/xml2rfc2/cli/


changes:
	svn log -r HEAD:950 | sed -n -e 's/^/  * /' -e '1,/^  \* Set version info and settings back to development mode/p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | tac | sed 's/$$/\n/' | fold -s -w 76 | sed -r 's/^([^ ])/    \1/'
