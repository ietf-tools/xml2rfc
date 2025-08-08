# -*- indent-with-tabs: 1 -*-
# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

# Regarding PDF testing: This is mainly done when running test.py, which not
# only generates a test PDF file, but deconstructs it and looks at some of
# the content.  Generating PDF files for each input file and just making
# binary comparisons is prone to false negatives, so in general there's no
# PDF file generation below.

SHELL := /bin/bash

export PYTHONHASHSEED = 0

IETF_TEST_CACHE_PATH = tests/cache
export IETF_TEST_CACHE_PATH

datetime_regex = [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T_ ][0-9][0-9]:[0-9][0-9]:[0-9][0-9]
version_regex =  [Vv]ersion [23N]\(\.[0-9N]\+\)\+\(\.dev\)\?
date_regex = \([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\|\([0-9]\([0-9]\)\? \)\?[ADFJMOS][a-u]\* [12][0-9][0-9][0-9]\)
legacydate_regex = [ADFJMOS][a-u]* [123]*[0-9], [12][0-9][0-9][0-9]$$
expire_regex = This Internet-Draft will expire on.*$
generator_regex = name="generator"
libversion_regex = \(pyflakes\|PyYAML\|requests\|setuptools\|six\|Weasyprint\) [0-9]\+\(\.[0-9]\+\)*

rfcxml= \
	rfc7911.xml		\
	rfc99999.xml	\

rfcxmlfiles = $(addprefix tests/input/, $(rfcxml))
rfctxt      = $(addsuffix .txt, $(basename $(rfcxml)))
rfctest     = $(addsuffix .tests, $(basename $(rfcxml)))
rfctxtfiles = $(addprefix tests/out/, $(rfctxt))
rfctests    = $(addprefix tests/out/, $(rfctest))

draftxml = \
	draft-template.xml		\
	draft-miek-test.xml		\
#

draftxmlfiles = $(addprefix tests/input/, $(draftxml))
drafttxt      = $(addsuffix .txt, $(basename $(draftxml)))
drafttest     = $(addsuffix .tests, $(basename $(draftxml)))
drafttxtfiles = $(addprefix tests/out/, $(drafttxt))
drafttests    = $(addprefix tests/out/, $(drafttest))

pyfiles  = $(wildcard  xml2rfc/*.py) $(wildcard  xml2rfc/writers/*.py)

.PHONY: clear-cache configtest install installtestdeps flaketest pytests tests tests-no-network yes yestests

# All tests
tests: minify tests-no-network cachetest

# Tests that can run without network access
tests-no-network: test flaketest drafttest old-drafttest rfctest utf8test v3featuretest elementstest indextest sourcecodetest notoctest bomtest wiptest mantest

# Clear the cache
clear-cache: install
	@echo -e "\n Clearing cache ..."
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --cache \"$${IETF_TEST_CACHE_PATH}\" --clear-cache"

env/bin/python:
	echo "Install virtualenv in $$PWD/env/ in order to run tests locally."

install:
	python3 --version
	python3 -m pip install . --quiet
	rm -rf xml2rfc.egg-info/

installtestdeps:
	python3 --version
	python3 -m pip install .[tests] --quiet
	rm -rf xml2rfc.egg-info/

test: installtestdeps flaketest xml2rfc/data/v3.rng configtest pytests

flaketest:
	pyflakes xml2rfc
	@[ -d tests/failed/ ] && rm -f tests/failed/*

configtest:
	python3 configtest.py

pytests: installtestdeps
	python3 test.py --verbose

CHECKOUTPUT=	\
	groff -ms -K$$type -T$$type tmp/$$doc.nroff | ./fix.pl | $$postnrofffix > tmp/$$doc.nroff.txt ;	\
	for type in .raw.txt .txt .nroff .html .exp.xml .v2v3.xml .prepped.xml ; do					\
	  diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(libversion_regex)' -I '$(date_regex)' tests/valid/$$doc$$type tmp/$$doc$$type || { echo "Diff failed for tmp/$$doc$$type output (1)"; read $(READARGS) -p "Copy [y/n]? " REPLY; if [ $$? -gt 0 -o "$$REPLY" = "y" ]; then cp -v tmp/$$doc$$type tests/valid/; else exit 1; fi; } \
	done ; if [ $$type = ascii ]; then echo "Diff nroff output with xml2rfc output:";\
	diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(libversion_regex)' -I '$(date_regex)' tmp/$$doc.nroff.txt tmp/$$doc.txt || { echo 'Diff failed for .nroff.txt output'; exit 1; }; fi

# ----------------------------------------------------------------------
#
# Generic rules

%.rng: %.rnc
	trang $< $@

%.tests: %.txt.test %.html.test %.exp.xml.test %.v2v3.xml.test %.v3add-xinclude.xml.test %.v3add-xinclude-w-revision.xml.test %.text.test %.pages.text.test %.v3.html.test %.prepped.xml.test %.plain.text
	@echo " Checking v3 validity"
	@doc=$(basename $@); printf ' '; xmllint --noout --relaxng xml2rfc/data/v3.rng $$doc.prepped.xml
	@echo " Diffing .plain.text against regular .text"
	@doc=$(basename $@); diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(libversion_regex)' -I '$(date_regex)' $$doc.plain.text $$doc.text || { echo 'Diff failed for $$doc.plain.text output'; exit 1; }

# keep this ahead of the tests/out/%.html rule so it takes precedence for pre-3.82 GNU make, which used
# the first matching rule instead of the shortest stem
tests/out/%.canonical.html: tests/input/%.canonical.xml install
	@echo " Checking generation of .html from canonical prepped .xml"
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out $(basename $@).html --html --external-css --external-js --legacy-date-format --no-inline-version $<" 2> /dev/null || { err=$$?; echo "Error output when generating .html from canonical prepped .xml"; exit $$err; }

tests/out/%.txt tests/out/%.raw.txt tests/out/%.nroff tests/out/%.html tests/out/%.txt : tests/input/%.xml install
	@echo -e "\n Processing $<"
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --base tests/out/ --text --html --strict $<"

tests/out/%.v2v3.xml: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --v2v3 --strict --legacy-date-format $< --out $@"
	@doc=$(basename $@); printf ' '; xmllint --noout --xinclude --relaxng xml2rfc/data/v3.rng $$doc.xml
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --v2v3 --strict --legacy-date-format --add-xinclude $< --out $@"

tests/out/%.v3add-xinclude.xml: tests/input/draft-miek-test-v3.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --v2v3 --add-xinclude $< --out $@"

tests/out/%.v3add-xinclude-w-revision.xml: tests/input/draft-template.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --v2v3 --add-xinclude --draft-revisions $< --out $@"

tests/out/%.prepped.xml: tests/input/%.xml tests/out/%.v3.html tests/out/%.text install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out $@ --prep $<"
	@echo " Checking generation of .html from prepped .xml"
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out $(basename $@).html --html --external-css --external-js --legacy-date-format --no-inline-version $@" 2> /dev/null || { err=$$?; echo "Error output when generating .html from prepped .xml"; exit $$err; }
	@diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(date_regex)' -I '$(legacydate_regex)' -I '$(expire_regex)' -I '$(generator_regex)' -I 'rel="alternate"' tests/out/$(notdir $(basename $(basename $@))).v3.html $(basename $@).html || { echo "Diff failed for $(basename $@).html output (2)"; exit 1; }
	@echo " Checking generation of .text from prepped .xml"
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out $(basename $@).text --text --no-pagination --external-css --external-js --legacy-date-format $@" 2> /dev/null || { err=$$?; echo "Error output when generating .text from prepped .xml"; exit $$err; }
	@diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(date_regex)' -I '$(legacydate_regex)' -I '$(expire_regex)' -I '$(generator_regex)' -I 'rel="alternate"' tests/out/$(notdir $(basename $(basename $@))).text $(basename $@).text || { echo "Diff failed for $(basename $@).text output (3)"; exit 1; }

tests/out/docfile.xml:
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --doc --out $@"

tests/out/docfile.html: tests/out/docfile.xml
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --html --external-css --external-js --no-inline-version --out $@ $<"

tests/out/manpage.txt:
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --man > $@"

tests/out/%.text: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --text --v3 --strict --no-pagination --legacy-date-format $< --out $@"

tests/out/%.pages.text: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --text --v3 --strict --legacy-date-format $< --out $@"

tests/out/%.bom.text: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --text --v3 --strict --bom $< --out $@"

tests/out/%.wip.text: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --text --v3 --strict --id-is-work-in-progress $< --out $@"

tests/out/%.v3.html: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --html --v3 --external-css --external-js --strict --legacy-date-format --rfc-reference-base-url https://rfc-editor.org/rfc --id-reference-base-url https://datatracker.ietf.org/doc/html/ --no-inline-version $< --out $@"

tests/out/%.pdf: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --pdf --v3 --legacy-date-format --rfc-reference-base-url https://rfc-editor.org/rfc --id-reference-base-url https://datatracker.ietf.org/doc/html/ $< --out $@"

tests/out/%.plain.xml: tests/out/%.prepped.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --unprep --v3 --legacy-date-format --rfc-reference-base-url https://rfc-editor.org/rfc --id-reference-base-url https://datatracker.ietf.org/doc/html/ $< --out $@"

tests/out/%.plain.text: tests/out/%.plain.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --text --v3 --strict --no-pagination --legacy-date-format $< --out $@  --silence='The document date'"

tests/out/%.exp.xml: tests/input/%.xml install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out $@ --exp $<"

%.prepped.xml: %.v2v3.xml
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out $@ --prep $<"

%.v2v3.text: %.v2v3.xml
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --utf8 --out $@ --text --v3 $<"

%.nroff.txt: %.nroff
	@echo " Creating $@ from $<"
	@if [ "$(findstring /rfc,$<)" = "/rfc" ]; then groff -ms -Kascii -Tascii $< | ./fix.pl > $@; else groff -ms -Kascii -Tascii $< | ./fix.pl | sed 1,2d > $@; fi

%.test: %
	@echo " Diffing $< against previously generated and merged output"
	@diff -u -I '$(date_regex)' -I '$(legacydate_regex)' -I '$(datetime_regex)' -I '$(version_regex)' -I '$(libversion_regex)' -I '$(generator_regex)' tests/valid/$(notdir $<) $< || { echo "Diff failed for $< output (5)"; read $(READARGS) -p "Copy [y/n]? " REPLY; if [ $$? -gt 0 -o "$$REPLY" = "y" ]; then cp -v $< tests/valid/; else exit 1; fi; }

%.min.js: %.js
	bin/uglifycall $<

.PRECIOUS: tests/out/%.txt tests/out/%.raw.txt tests/out/%.nroff tests/out/%.nroff.txt tests/out/%.html tests/out/%.txt tests/out/%.exp.xml tests/out/%.v2v3.xml tests/out/%.prepped.xml tests/out/%.text tests/out/%.v3.html %.prepped.xml %.nroff.txt tests/out/%.plain.txt

# ----------------------------------------------------------------------

old-drafttest: cleantmp install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --base tmp/ --raw --legacy --text --nroff --html --exp --v2v3 tests/input/draft-template-old.xml"
	@PS4=" " /bin/bash -cx "cp  tests/input/ietf.svg tmp/"
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out tmp/draft-template-old.prepped.xml --prep tmp/draft-template-old.v2v3.xml "
	doc=draft-template-old ; postnrofffix="sed 1,2d" ; type=ascii; $(CHECKOUTPUT)

miektest: cleantmp install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --base tmp/ --raw --legacy --text --nroff --html --exp --v2v3 tests/input/draft-miek-test.xml"
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --out tmp/draft-miek-test.prepped.xml --prep tmp/draft-miek-test.v2v3.xml"
	doc=draft-miek-test ; postnrofffix="sed 1,2d" ; type=ascii; $(CHECKOUTPUT)

cachetest: cleantmp install
	@echo -e "\n Clearing cache ..."
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache .cache --clear-cache"
	@echo " Filling cache ..."
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache .cache tests/input/draft-template.xml --base tmp/"
	@echo " Running without accessing network ..."
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache .cache tests/input/draft-template.xml --no-network --base tmp/"


rfctest: cleantmp env/bin/python install $(rfctests) tests/out/rfc9001.canonical.html.test

rfcregressiontest: cleantmp install
	@echo -e "\n Running RFC regression test ..."
	@echo -e "\n Gathering RFC XML files ..."
	mkdir -p tests/rfc/out
	@PS4=" " /bin/bash -cx "rsync -avz --delete --include='rfc[0-9][0-9][0-9][0-9].xml' --exclude='*' rsync.ietf.org::rfc tests/rfc/"
	@echo -e "\n Generating text ..."
	for rfc in tests/rfc/*.xml; do xml2rfc --skip-config --allow-local-file-access --cache "$${IETF_TEST_CACHE_PATH}" --path tests/rfc/out/ --text $$rfc; done
	@echo -e "\n Generating html ..."
	for rfc in tests/rfc/*.xml; do xml2rfc --skip-config --allow-local-file-access --cache "$${IETF_TEST_CACHE_PATH}" --path tests/rfc/out/ --html $$rfc; done
	@echo -e "\n Generating pdf ..."
	for rfc in tests/rfc/*.xml; do xml2rfc --skip-config --allow-local-file-access --cache "$${IETF_TEST_CACHE_PATH}" --path tests/rfc/out/ --pdf $$rfc; done

drafttest: cleantmp env/bin/python install $(drafttests) dateshifttest

# rfctest: cleantmp env/bin/python install $(rfctests)
# 	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --utf8tests/input/rfc6787.xml --base tmp/ --raw --legacy --text --nroff --html --exp --v2v3 --prep"
# 	doc=rfc6787 ; postnrofffix="cat" ; type=ascii; $(CHECKOUTPUT)
# 	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --utf8tests/input/rfc7754.edited.xml --base tmp/ --raw --legacy --text --nroff --html --exp --v2v3 --prep"
# 	doc=rfc7754.edited ; postnrofffix="cat" ; type=ascii; $(CHECKOUTPUT)
# 	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --utf8tests/input/rfc7911.xml --base tmp/ --raw --legacy --text --nroff --html --exp --v2v3 --prep"
# 	doc=rfc7911 ; postnrofffix="cat" ; type=ascii; $(CHECKOUTPUT)

unicodetest: cleantmp  env/bin/python install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --base tmp/ --raw --legacy --text --nroff --html --no-inline-version --exp --v2v3 --prep tests/input/unicode.xml "
	doc=unicode ; postnrofffix="sed 1,2d" ; type=ascii; $(CHECKOUTPUT)

utf8test: cleantmp  env/bin/python install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --base tmp/ --raw --legacy --text --nroff --html --no-inline-version --exp --v2v3 --prep -q tests/input/utf8.xml"
	@doc=utf8 ; postnrofffix="cat" ; type=utf8; $(CHECKOUTPUT)

v3featuretest: tests/out/draft-v3-features.prepped.xml.test tests/out/draft-v3-features.text.test tests/out/draft-v3-features.v3.html.test

dateshifttest: cleantmp install
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --date 2013-02-01 --legacy --out tmp/draft-miek-test.dateshift.txt --text tests/input/draft-miek-test.xml"
	@diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(date_regex)' tests/valid/draft-miek-test.dateshift.txt tmp/draft-miek-test.dateshift.txt || { echo "Diff failed for draft-miek-test.dateshift.txt output"; exit 1; } 

elementstest: install tests/out/elements.prepped.xml.test tests/out/elements.text.test tests/out/elements.pages.text.test tests/out/elements.v3.html.test

indextest: install tests/out/indexes.prepped.xml.test tests/out/indexes.text.test tests/out/indexes.pages.text.test tests/out/indexes.v3.html.test

sourcecodetest: install tests/out/sourcecode.prepped.xml.test tests/out/sourcecode.text.test tests/out/sourcecode.pages.text.test tests/out/sourcecode.v3.html.test

notoctest: install tests/out/no-toc.prepped.xml.test tests/out/no-toc.text.test tests/out/no-toc.pages.text.test tests/out/no-toc.v3.html.test

bomtest: tests/out/elements.bom.text.test

wiptest: tests/out/elements.wip.text.test

mantest: install cleantmp tests/out/manpage.txt.test tests/out/docfile.html.test
	@fgrep -q '***' tests/out/manpage.txt; res="$$?"; if [ "$$res" = "1" ]; then true; else echo "Missing documentation in manpage"; exit 1; fi

manupdate: yes mantest

cleantmp:
	@[ -d tmp ] || mkdir -p tmp
	@[ -d tmp ] && rm -f tmp/*
	@[ -d tests/out ] || mkdir -p tests/out
	@[ -d tests/out ] && rm -f tests/out/* && cp xml2rfc/templates/rfc2629* tests/out/


yes:
	$(eval READARGS=-t1)

yestests: yes tests

noflakestests: install pytests regressiontests

regressiontests: drafttest rfctest

minify: xml2rfc/data/metadata.min.js



test2:	test
	@PS4=" " /bin/bash -cx "xml2rfc --skip-config --allow-local-file-access --cache \"$${IETF_TEST_CACHE_PATH}\" --no-network --utf8 tests/input/rfc6635.xml --legacy --text --out tmp/rfc6635.txt	&& diff -u -I '$(datetime_regex)' -I '$(version_regex)' -I '$(date_regex)' tests/valid/rfc6635.txt tmp/rfc6635.txt "

upload: install
	rst2html changelog > /dev/null	# verify that the changelog is valid rst
	python setup.py sdist upload --sign
	python setup.py install
	rsync dist/xml2rfc-$(shell xml2rfc --skip-config --version).tar.gz /www/tools.ietf.org/tools/xml2rfc2/cli/ || true
	toolpush /www/tools.ietf.org/tools/xml2rfc2/cli/


changes:
	svn log -r HEAD:950 | sed -n -e 's/^/  * /' -e '1,/^  \* Set version info and settings back to development mode/p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | tac | sed 's/$$/\n/' | fold -s -w 76 | sed -r 's/^([^ ])/    \1/'
