# Copyright (c) 1998 Zveno Pty Ltd
# http://www.zveno.com/

# tcl/Makefile --
#
# Builds the Tcl interface to expat

CFLAGS            =
TCLEXPAT_VERSION  = 1.1


## Site specific - defaults
# These settings are set in Tcl's lib/tclConfig.sh file.
# So invoking this makefile after sourcing tclConfig.sh should
# set everything correctly for your site , e.g:
#     . /usr/local/tcl/lib/tclConfig.sh ; make -e
# will override  whatever is set below

TCL_SHLIB_SUFFIX  = .so
TCL_OBJS          = tclexpat.o
TCL_PREFIX        = /usr/pkg
TCL_EXEC_PREFIX   = /usr/pkg
TCL_SHLIB_CFLAGS  = -fPIC
TCL_SHLIB_LD      = gcc -shared
TCL_CC            = gcc
TCL_PACKAGE_PATH  = /usr/pkg/lib/tcl



## Architecture specific overrides
# uncomment to overide generic defaults

# Linux 2.x

#TCL_DEFS=  -DHAVE_GETCWD=1 -DHAVE_UNISTD_H=1 -DUSE_TERMIOS=1 -DHAVE_SYS_TIME_H=1 -DTIME_WITH_SYS_TIME=1 -DHAVE_TZNAME=1 -DHAVE_TIMEZONE_VAR=1 -DHAVE_ST_BLKSIZE=1 -DSTDC_HEADERS=1 -DHAVE_SIGNED_CHAR=1 -DHAVE_SYS_IOCTL_H=1
#TCL_SHLIB_CFLAGS=-fPIC
#TCL_SHLIB_LD=gcc -shared
#TCL_SHLIB_SUFFIX=.so

# Solaris 2.5.1

#TCL_DEFS= -DTCL_THREADS=1 -DHAVE_GETCWD=1 -DHAVE_OPENDIR=1 -DHAVE_STRSTR=1 -DHAVE_STRTOL=1 -DHAVE_TMPNAM=1 -DHAVE_WAITPID=1 -DHAVE_UNISTD_H=1 -DUSE_TERMIOS=1 -DHAVE_SYS_TIME_H=1 -DTIME_WITH_SYS_TIME=1 -DHAVE_TZNAME=1 -DHAVE_TIMEZONE_VAR=1 -DHAVE_ST_BLKSIZE=1 -Dstrtod=fixstrtod -DSTDC_HEADERS=1 -DNO_UNION_WAIT=1 -DNEED_MATHERR=1 -Dvfork=fork -DHAVE_SIGNED_CHAR=1 -DHAVE_SYS_IOCTL_H=1 -DHAVE_SYS_FILIO_H=1 
#TCL_SHLIB_LD=/usr/ccs/bin/ld -G -z text
#TCL_SHLIB_SUFFIX=.so

# HPUX 10.10

#TCL_DEFS= -DHAVE_GETCWD=1 -DHAVE_OPENDIR=1 -DHAVE_STRSTR=1 -DHAVE_STRTOL=1 -DHAVE_TMPNAM=1 -DHAVE_WAITPID=1 -DNO_DLFCN_H=1 -DHAVE_UNISTD_H=1 -DUSE_TERMIOS=1 -DHAVE_SYS_TIME_H=1 -DTIME_WITH_SYS_TIME=1 -DHAVE_TZNAME=1 -DHAVE_TIMEZONE_VAR=1 -DHAVE_ST_BLKSIZE=1 -DSTDC_HEADERS=1 -DNO_UNION_WAIT=1 -DNEED_MATHERR=1 -DHAVE_SIGNED_CHAR=1 -DHAVE_SYS_IOCTL_H=1 
#TCL_SHLIB_CFLAGS=-fPIC
#TCL_SHLIB_LD=ld -b
#TCL_SHLIB_SUFFIX=.sl


#---------------------------------------------------------------------------
 
# The following settings are from expat's own Makefile

# Use one of the next two lines; unixfilemap is better if it works.
FILEMAP_OBJ=expat/xmlwf/unixfilemap.o
#FILEMAP_OBJ=expat/xmlwf/readfilemap.o


#----------------------------------------------------------------------------
# You shouldnt have to edit anything below here
#----------------------------------------------------------------------------

CC=  $(TCL_CC)
LIB= libtclexpat$(TCL_SHLIB_SUFFIX)


OBJS=expat/xmltok/xmltok.o \
  expat/xmltok/xmlrole.o \
  expat/xmlwf/xmlwf.o \
  expat/xmlwf/codepage.o \
  expat/xmlparse/xmlparse.o \
  expat/xmlparse/hashtable.o \
  $(FILEMAP_OBJ)


all:		$(LIB)


$(LIB):		tclexpat.o ${OBJS}
	$(TCL_SHLIB_LD) -o $(LIB) $(OBJS) tclexpat.o

${OBJS}:
	cd expat ; make CC="${CC}" SHLIB_CFLAGS="${TCL_SHLIB_CFLAGS}"

tclexpat.o:	tclexpat.c
	$(TCL_CC) $(CFLAGS) -c $(TCL_DEFS) $(TCL_SHLIB_CFLAGS) -I$(TCL_PREFIX)/include -Iexpat/xmlparse tclexpat.c

install:	$(LIB)
	instdir=`echo $(TCL_PACKAGE_PATH) | cut -f 1 -d :` ; \
	mkdir $$instdir/TclExpat-$(TCLEXPAT_VERSION) ; \
	cp $(LIB) pkgIndex.tcl $$instdir/TclExpat-$(TCLEXPAT_VERSION) ;\
	ln -s $$instdir/TclExpat-$(TCLEXPAT_VERSION)/$(LIB) $$instdir/$(LIB) ;\
	cp expat/xmlparse/xmlparse.h $$instdir/../include/

clean:
	@cd expat; make clean
	rm -f *~ *.o 
	@if [ ! -z $(TCL_SHLIB_SUFFIX) ] ; then \
	    echo "rm -f *$(TCL_SHLIB_SUFFIX)" ;\
	    rm -f *$(TCL_SHLIB_SUFFIX) ;\
	fi




