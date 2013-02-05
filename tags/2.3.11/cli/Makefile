# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

#svnrev	:= $(shell svn info | grep ^Revision | awk '{print $$2}' )
datetime_regex = [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T_ ][0-9][0-9]:[0-9][0-9]:[0-9][0-9]

test:
	[ -d tmp ] || mkdir -p tmp
	[ -d tests/failed/ ] && rm -f tests/failed/*
	python test.py
	xml2rfc tests/input/rfc6787.xml --raw --out tmp/rfc6787.raw	&& diff -I "$(datetime_regex)" tests/valid/rfc6787.raw tmp/rfc6787.raw
	xml2rfc tests/input/rfc6787.xml --text --out tmp/rfc6787.txt	&& diff -I "$(datetime_regex)" tests/valid/rfc6787.txt tmp/rfc6787.txt 
	xml2rfc tests/input/rfc6787.xml --nroff --out tmp/rfc6787.nroff	&& diff -I "$(datetime_regex)" tests/valid/rfc6787.nroff tmp/rfc6787.nroff 
	xml2rfc tests/input/rfc6787.xml --html --out tmp/rfc6787.html	&& diff -I "$(datetime_regex)" tests/valid/rfc6787.html tmp/rfc6787.html 
	xml2rfc tests/input/rfc6787.xml --exp --out tmp/rfc6787.xml	&& diff -I "$(datetime_regex)" tests/valid/rfc6787.xml tmp/rfc6787.xml 

upload:
	python setup.py sdist upload --sign

changes:
	svn log -r HEAD:1 | sed -n -e 's/^/  * /' -e '1,400p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | fold -sbw76 | sed -r 's/^([^ ].*)$$/    &/'
