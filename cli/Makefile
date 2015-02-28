# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

#svnrev	:= $(shell svn info | grep ^Revision | awk '{print $$2}' )
datetime_regex = [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T_ ][0-9][0-9]:[0-9][0-9]:[0-9][0-9]
version_regex =  [Vv]ersion [2N]\(\.[0-9N]\+\)\+\(\.dev\)\?


bin/python:
	echo "Install virtualenv here ($$PWD) in order to run tests locally."

install:
	python --version
	python setup.py --quiet install

test:	install flaketests pytests

flaketests:
	pyflakes xml2rfc
	[ -d tests/failed/ ] && rm -f tests/failed/*

pytests:
	python test.py --verbose

drafttest: install
	[ -d tmp ] || mkdir -p tmp
	[ -d tmp ] && rm -f tmp/*
	@PYTHONPATH=$$PWD python scripts/xml2rfc --cache tests/cache tests/input/draft-template.xml --base tmp/ --raw --text --nroff --html --exp
	@groff -ms -Tascii tmp/draft-template.nroff | ./fix.pl | sed 1,2d > tmp/draft-template.nroff.txt
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-template.raw.txt	tmp/draft-template.raw.txt	|| { echo 'Diff failed for .raw.txt output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-template.txt	tmp/draft-template.txt		|| { echo 'Diff failed for .txt output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-template.nroff	tmp/draft-template.nroff 	|| { echo 'Diff failed for .nroff output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-template.html	tmp/draft-template.html 	|| { echo 'Diff failed for .html output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-template.exp.xml	tmp/draft-template.exp.xml	|| { echo 'Diff failed for .exp.xml output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tmp/draft-template.nroff.txt tmp/draft-template.txt	|| { echo 'Diff failed for .nroff.txt output'; exit 1; }

miektest: install
	[ -d tmp ] || mkdir -p tmp
	[ -d tmp ] && rm -f tmp/*
	@ PYTHONPATH=$$PWD python scripts/xml2rfc --cache tests/cache tests/input/draft-miek-test.xml --base tmp/ --raw --text --nroff --html --exp
	@groff -ms -Tascii tmp/draft-miek-test.nroff | ./fix.pl | sed 1,2d > tmp/draft-miek-test.nroff.txt
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-miek-test.raw.txt	tmp/draft-miek-test.raw.txt	|| { echo 'Diff failed for .raw.txt output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-miek-test.txt	tmp/draft-miek-test.txt		|| { echo 'Diff failed for .txt output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-miek-test.nroff	tmp/draft-miek-test.nroff 	|| { echo 'Diff failed for .nroff output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-miek-test.html	tmp/draft-miek-test.html 	|| { echo 'Diff failed for .html output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/draft-miek-test.exp.xml	tmp/draft-miek-test.exp.xml	|| { echo 'Diff failed for .exp.xml output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tmp/draft-miek-test.nroff.txt tmp/draft-miek-test.txt	|| { echo 'Diff failed for .nroff.txt output'; exit 1; }

rfctest:  bin/python install
	[ -d tmp ] || mkdir -p tmp
	[ -d tmp ] && rm -f tmp/*
	@ PYTHONPATH=$$PWD python scripts/xml2rfc --cache tests/cache tests/input/rfc6787.xml --base tmp/ --raw --text --nroff --html --exp
	@groff -ms -Tascii tmp/rfc6787.nroff | ./fix.pl > tmp/rfc6787.nroff.txt
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6787.raw.txt	tmp/rfc6787.raw.txt	|| { echo 'Diff failed for .raw.txt output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6787.txt	tmp/rfc6787.txt 	|| { echo 'Diff failed for .txt output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6787.nroff	tmp/rfc6787.nroff 	|| { echo 'Diff failed for .nroff output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6787.html	tmp/rfc6787.html 	|| { echo 'Diff failed for .html output'; exit 1; }
	@ diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6787.exp.xml	tmp/rfc6787.exp.xml 	|| { echo 'Diff failed for .exp.xml output'; exit 1; }
	@diff -I '$(datetime_regex)' -I '$(version_regex)' tmp/rfc6787.nroff.txt tmp/rfc6787.txt	|| { echo 'Diff failed for .nroff.txt output'; exit 1; }

tests: test regressiontests

noflakestests: install pytests regressiontests

regressiontests: drafttest miektest rfctest

test2:	test
	@ PYTHONPATH=$$PWD python scripts/xml2rfc --cache tests/cache tests/input/rfc6635.xml --text --out tmp/rfc6635.txt	&& diff -I '$(datetime_regex)' -I '$(version_regex)' tests/valid/rfc6635.txt tmp/rfc6635.txt 

upload:
	rst2html changelog > /dev/null	# verify that the changelog is valid rst
	python setup.py sdist upload --sign
	rsync dist/xml2rfc-$(shell PYTHONPATH=$$PWD python scripts/xml2rfc --version).tar.gz /www/tools.ietf.org/tools/xml2rfc2/cli/
	toolpush /www/tools.ietf.org/tools/xml2rfc2/cli/


changes:
	svn log -r HEAD:950 | sed -n -e 's/^/  * /' -e '1,/^  \* Set version info and settings back to development mode/p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | tac | sed 's/$$/\n/' | fold -s -w 76 | sed -r 's/^([^ ])/    \1/'
