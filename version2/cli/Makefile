# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

#svnrev	:= $(shell svn info | grep ^Revision | awk '{print $$2}' )
datetime_regex = [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T_ ][0-9][0-9]:[0-9][0-9]:[0-9][0-9]
version_regex =  "[Vv]ersion.2\.[0-9]"


bin/python:
	echo "Install virtualenv here ($$PWD) in order to run tests locally."
	
install:
	bin/python setup.py --quiet install

test:	bin/python install
	[ -d tmp ] || mkdir -p tmp
	[ -d tests/failed/ ] && rm -f tests/failed/*
	bin/python test.py
	#
	@ PYTHONPATH=$$PWD bin/python scripts/xml2rfc tests/input/rfc6787.xml --base tmp/ --raw --text --nroff --html --exp
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/rfc6787.raw.txt	tmp/rfc6787.raw.txt
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/rfc6787.txt	tmp/rfc6787.txt 
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/rfc6787.nroff	tmp/rfc6787.nroff 
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/rfc6787.html	tmp/rfc6787.html 
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/rfc6787.exp.xml	tmp/rfc6787.exp.xml 
	#
	@ PYTHONPATH=$$PWD bin/python scripts/xml2rfc tests/input/draft-template.xml --base tmp/ --raw --text --nroff --html --exp
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/draft-template.raw.txt	tmp/draft-template.raw.txt
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/draft-template.txt	tmp/draft-template.txt 
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/draft-template.nroff	tmp/draft-template.nroff 
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/draft-template.html	tmp/draft-template.html 
	@ diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/draft-template.exp.xml	tmp/draft-template.exp.xml 

test2:	test
	@ PYTHONPATH=$$PWD bin/python scripts/xml2rfc tests/input/rfc6635.xml --text --out tmp/rfc6635.txt	&& diff -I "$(datetime_regex)" -I "$(version_regex)" tests/valid/rfc6635.txt tmp/rfc6635.txt 

upload:
	python setup.py sdist upload --sign
	rsync dist/xml2rfc-$(PYTHONPATH=$$PWD bin/python scripts/xml2rfc --version).* /www/tools.ietf.org/tools/xml2rfc2/
	toolpush /www/tools.ietf.org/tools/xml2rfc2/


changes:
	svn log -r HEAD:1 | sed -n -e 's/^/  * /' -e '1,400p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | fold -sbw76 | sed -r 's/^([^ ].*)$$/    &/'
