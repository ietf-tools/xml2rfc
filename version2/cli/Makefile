# Simple makefile which mostly encapsulates setup.py invocations.  Useful as
# much as documentation as it is for invocation.

#svnrev	:= $(shell svn info | grep ^Revision | awk '{print $$2}' )


test:
	python test.py

upload:
	python setup.py sdist upload --sign

changes:
	svn log -r HEAD | sed -n -e 's/^/  * /' -e '1,400p' | egrep -v -- '^  \* (----------|r[0-9]+ |$$)' | head -n -1 | fold -sbw76 | sed -r 's/^([^ ].*)$$/    &/'
