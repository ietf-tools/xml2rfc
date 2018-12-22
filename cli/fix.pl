#! /usr/bin/env perl

# fix.pl  17-Nov-93  Craig Milo Rogers at USC/ISI
#
#       The style guide for RFCs calls for pages to be delimited by the
# sequence <last-non-blank-line><formfeed-line><first-non-blank-line>.
# Unfortunately, NROFF is reluctant to produce output that conforms to
# this convention.  This script fixes RFC-style documents by searching
# for the token "FORMFEED[Page", replacing "FORMFEED" with spaces,
# appending a formfeed line, and deleting white space up to the next
# non-white space character.
#
#       There is one difference between this script's output and that of
# the "fix.sh" and "pg" programs it replaces:  this script includes a
# newline after the formfeed after the last page in a file, whereas the
# earlier programs left a bare formfeed as the last character in the
# file.  To obtain bare formfeeds, uncomment the second substitution
# command below.  To strip the final formfeed, uncomment the third
# substitution command below.
#
#       This script is intended to run as a filter, as in:
#
# nroff -ms input-file | fix.pl > output-file
#
#       When porting this script, please observe the following points:
#
# 1)    ISI keeps perl in "/local/bin/perl";  your system may keep it
#       elsewhere.
# 2)    On systems with a CRLF end-of-line convention, the "\n"s below
#       may have to be replaced with "\r\n"s.

#$* = 1;                                 # Enable multiline patterns.
undef $/;                               # Read whole files in a single
                                        # gulp.

while (<>) {                            # Read the entire input file.
    s/FORMFEED(\[Page\s+\d+\])\s+/        \1\n\f\n/gm;
                                        # Rewrite the end-of-pages.
#    s/\f\n$/\f/;                       # Want bare formfeed at end?
    s/\f\n$//m;                         # Want no formfeed at end?
    print;                              # Print the resultant file.
}

