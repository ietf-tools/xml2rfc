


The README file                                                  M. Rose
                                            Dover Beach Consulting, Inc.
                                                        January 16, 2005


                             xml2rfc v1.28


Table of Contents

   1.    Introduction . . . . . . . . . . . . . . . . . . . . . . . .  2
   2.    Requirements . . . . . . . . . . . . . . . . . . . . . . . .  3
   3.    Testing  . . . . . . . . . . . . . . . . . . . . . . . . . .  4
   3.1   Testing under a windowing system . . . . . . . . . . . . . .  4
   3.2   Testing without a windowing system . . . . . . . . . . . . .  4
   4.    Next steps . . . . . . . . . . . . . . . . . . . . . . . . .  5
   4.1   Processing Instructions  . . . . . . . . . . . . . . . . . .  5
   4.1.1 Option Settings  . . . . . . . . . . . . . . . . . . . . . .  6
   4.1.2 Include Files  . . . . . . . . . . . . . . . . . . . . . . .  7
   5.    Additions to RFC 2629  . . . . . . . . . . . . . . . . . . .  9
   6.    Limitations of xml2rfc . . . . . . . . . . . . . . . . . . . 10
   7.    References . . . . . . . . . . . . . . . . . . . . . . . . . 10
         Author's Address . . . . . . . . . . . . . . . . . . . . . . 10
   A.    MacOS 9 Installation (courtesy of Ned Freed) . . . . . . . . 11
   B.    rfc2629.xslt (courtesy of Julian Reschke)  . . . . . . . . . 12
   C.    Windows XP/Cygwin Installation (courtesy of Joe Touch) . . . 13
   D.    Copyrights . . . . . . . . . . . . . . . . . . . . . . . . . 14
























Rose                                                            [Page 1]

README                        xml2rfc v1.28                 January 2005


1.  Introduction

   This is a package to convert memos written in XML to the RFC format.

   If you don't want to install any software, you can use the web-based
   service [2].













































Rose                                                            [Page 2]

README                        xml2rfc v1.28                 January 2005


2.  Requirements

   You need to have Tcl/Tk version 8 running on your system.  Tcl is a
   scripting language, Tk is Tcl with support for your windowing system.

   To get a source or binary distribution for your system, go to the
   Scriptics website [3] and install it.  If you get the binary
   distribution, this is pretty simple.

   Of course, you may already have Tcl version 8.  To find out, try
   typing this command from the shell (or the "MS-DOS Prompt"):

       % tclsh

   If the program launches, you're good to go with Tcl version 8.

   If you are running under a windowing system (e.g., X or Windows), you
   can also try:

       % wish

   If a new window comes up along with a "Console" window, then you're
   good to go with Tk version 8.

   Finally, you may notice a file called "xml2sgml.tcl" in the
   distribution.  It contains some extra functionality for a few special
   users -- so, if you don't know what it is, don't worry about it...
























Rose                                                            [Page 3]

README                        xml2rfc v1.28                 January 2005


3.  Testing

   Now test your installation.

3.1  Testing under a windowing system

   Type this command from the shell:

       % xml2rfc.tcl

   A new window should come up that looks like this:

       +------------------------------------------------------------+
       |                     Convert XML to RFC                     |
       |                                                            |
       |  Select input file: ____________________________  [Browse] |
       |                                                            |
       | Select output file: ____________________________  [Browse] |
       |                                                            |
       |               [Convert]               [Quit]               |
       |                                                            |
       +------------------------------------------------------------+

   Fill-in the blanks and click on [Convert].

3.2  Testing without a windowing system

   Type this command from the shell:

       % tclsh

   If the program launches, type this command to it:

       % source xml2rfc.tcl

   and you should see these four lines:

       invoke as "xml2rfc   inputfile outputfile"
              or "xml2txt   inputfile"
              or "xml2html  inputfile"
              or "xml2nroff inputfile"










Rose                                                            [Page 4]

README                        xml2rfc v1.28                 January 2005


4.  Next steps

   Read the 2629bis [4] document.  In particular, Section 3 has some
   good information.

4.1  Processing Instructions

   A _processing instruction_ is a directive to an XML application.  If
   you want to give directives to *xml2rfc*, the processing instructions
   (PIs) look like this:

       <?rfc keyword='value'?>

   Of course, if you like the default behavior, you don't need any PIs
   in your input file!




































Rose                                                            [Page 5]

README                        xml2rfc v1.28                 January 2005


4.1.1  Option Settings

   The list of valid keywords are:

   +--------------+--------------+-------------------------------------+
   |      keyword |    default   | meaning                             |
   +--------------+--------------+-------------------------------------+
   |   autobreaks |      yes     | automatically force page breaks to  |
   |              |              | avoid widows and orphans (not       |
   |              |              | perfect)                            |
   |              |              |                                     |
   |     comments |      no      | render <cref> information           |
   |              |              |                                     |
   |       inline |      no      | if comments is "yes", then render   |
   |              |              | comments inline; otherwise render   |
   |              |              | them in an "Editorial Comments"     |
   |              |              | section                             |
   |              |              |                                     |
   |       strict |      no      | try to enforce the ID-nits          |
   |              |              | conventions and DTD validity        |
   |              |              |                                     |
   |  iprnotified |      no      | include boilerplate from Section    |
   |              |              | 10.4(d) of [1]                      |
   |              |              |                                     |
   |   linkmailto |      yes     | generate mailto: URL, as            |
   |              |              | appropriate                         |
   |              |              |                                     |
   |      compact |      no      | when producing a txt/nroff file,    |
   |              |              | try to conserve vertical whitespace |
   |              |              |                                     |
   |   subcompact |    compact   | if compact is "yes", then you can   |
   |              |              | make things a little less compact   |
   |              |              | by setting this to "no"             |
   |              |              |                                     |
   |          toc |      no      | generate a table-of-contents        |
   |              |              |                                     |
   |    tocompact |      yes     | if toc is "yes", then setting this  |
   |              |              | to "no" will make it a little less  |
   |              |              | compact                             |
   |              |              |                                     |
   |     tocdepth |       3      | if toc is "yes", then this          |
   |              |              | determines the depth of the         |
   |              |              | table-of-contents                   |
   |              |              |                                     |
   |    tocindent |      no      | if toc is "yes", then setting this  |
   |              |              | to "yes" will indent subsections in |
   |              |              | the table-of-contents               |
   |              |              |                                     |



Rose                                                            [Page 6]

README                        xml2rfc v1.28                 January 2005


   |      editing |      no      | insert editing marks for ease of    |
   |              |              | discussing draft versions           |
   |              |              |                                     |
   |      private |      ""      | produce a private memo rather than  |
   |              |              | an RFC or Internet-Draft.           |
   |              |              |                                     |
   |       header |      ""      | override the leftmost header string |
   |              |              |                                     |
   |       footer |      ""      | override the center footer string   |
   |              |              |                                     |
   |       slides |      no      | when producing an html file,        |
   |              |              | produce multiple files for a slide  |
   |              |              | show                                |
   |              |              |                                     |
   |     sortrefs |      no      | sort references                     |
   |              |              |                                     |
   |      symrefs |      no      | use anchors rather than numbers for |
   |              |              | references                          |
   |              |              |                                     |
   |     topblock |      yes     | put the famous header block on the  |
   |              |              | first page                          |
   |              |              |                                     |
   |   background |      ""      | when producing an html file, use    |
   |              |              | this image                          |
   |              |              |                                     |
   |    needLines |      n/a     | an integer hint indicating how many |
   |              |              | contiguous lines are needed at this |
   |              |              | point in the output                 |
   +--------------+--------------+-------------------------------------+

   Remember, that as with everything else in XML, keywords and values
   are case-sensitive.

   With the exception of the *needLines* PI, you normally put all of
   these processing instructions at the beginning of the document (right
   after the XML declartion).

4.1.2  Include Files

   *xml2rfc* has an include-file facility, e.g.,

       <?rfc include='file'?>

   *xml2rfc* will consult the $XML_LIBRARY environment variable for a
   search path of where to look for files.  (If this envariable isn't
   set, the directory containing the file that contains the include-file
   directive is used.)




Rose                                                            [Page 7]

README                        xml2rfc v1.28                 January 2005


   You can also have *xml2rfc* set this envariable directly, by creating
   a file called ".xml2rfc.rc" in the directory where your main file is,
   e.g.,

   global env tcl_platform

   if {![string compare $tcl_platform(platform) windows]} {
       set sep ";"
   } else {
       set sep ":"
   }

   if {[catch { set env(XML_LIBRARY) } library]} {
       set library ""
       foreach bibxmlD [lsort -dictionary \
                              [glob -nocomplain $HOME/rfcs/bibxml/*]] {
           append library $sep$bibxmlD
       }
   }

   set nativeD [file nativename $inputD]
   if {[lsearch [split $library $sep] $nativeD] < 0} {
       set library "$nativeD$sep$library"
   }

   set env(XML_LIBRARY) $library

   There are links to various bibliographic databases (RFCs, I-Ds, and
   so on) on the *xml2rfc*homepage [5].






















Rose                                                            [Page 8]

README                        xml2rfc v1.28                 January 2005


5.  Additions to RFC 2629

   A few additions have been made to the format originally defined in
   RFC 2629.  In particular, Appendix C of the 2629bis document
   enumerates the additions.

   In addition, *xml2rfc* recognizes an undocumented *src* attribute in
   the *artwork* element, but only if HTML is being generated, e.g.,

          <figure><artwork src='layers.gif' /></figure>

   In this case, an *img* tag is placed in the HTML output, and the
   textual contents of the *artwork*, *preamble*, and *postamble*
   elements are ignored.





































Rose                                                            [Page 9]

README                        xml2rfc v1.28                 January 2005


6.  Limitations of xml2rfc

   o  The *figure* element's *title* attribute is ignored, except when
      generating HTML.

   o  The *xref* element's *pageno* attribute is ignored.


7.  References

   [1]  Bradner, S., "The Internet Standards Process -- Revision 3",
        BCP 9, RFC 2026, October 1996.

   [2]  <http://xml.resource.org/>

   [3]  <http://www.scriptics.com/software/tcltk/8.4.html>

   [4]  <draft-mrose-writing-rfcs.html>

   [5]  <http://xml.resource.org/>


Author's Address

   Marshall T. Rose
   Dover Beach Consulting, Inc.
   POB 255268
   Sacramento, CA  95865-5268
   US

   Phone: +1 916 483 8878
   Email: mrose@dbc.mtview.ca.us



















Rose                                                           [Page 10]

README                        xml2rfc v1.28                 January 2005


Appendix A.  MacOS 9 Installation (courtesy of Ned Freed)

   1.  Install Tcl/Tk 8.3.4

   2.  When you performed Step 1, a folder in your "Extensions" folder
       called "Tool Command Language" was created.  Create a new folder
       under "Extensions", with any name you like.

   3.  Drag the file "xml2rfc.tcl" onto the "Drag & Drop Tclets"
       application that was installed in Step 1.

   4.  When asked for an appropriate "wish" stub, select "Wish 8.3.4".

   5.  The "Drap & Drop Tclets" application will write out an executable
       version of *xml2rfc*.




































Rose                                                           [Page 11]

README                        xml2rfc v1.28                 January 2005


Appendix B.  rfc2629.xslt (courtesy of Julian Reschke)

   The file "rfc2629.xslt" can be used with an XSLT-capable formatter
   (i.e., IE6) to produce HTML.  A word of warning though: the XSLT
   script doesn't support the processing instructions discussed earlier
   (Section 4.1).













































Rose                                                           [Page 12]

README                        xml2rfc v1.28                 January 2005


Appendix C.  Windows XP/Cygwin Installation (courtesy of Joe Touch)

   1.  install Cygwin: follow instructions at cygwin.org,  make sure to
       select "tcltk" in "Libs"

   2.  place a copy of xml2rfc files on a local drive,  e.g., in
       "C:\xml2rfc" NOTE: for xml2rfc-1.26 and earlier, see NOTE below.

   3.  place a copy of bibxml* files on a local drive, e.g., in
       "C:\xmlbib\"

   4.  edit ".xml2rfc.rc" to indicate the "bibxml*" library path, e.g.,
       as per step #3, change "~/rfca/bibxml/*" to
       "/cygdrive/c/xmlbib/*"

   5.  run xml2rfc as follows: "tclsh /cygdrive/c/xml2rfc/xml2rfc.tcl"

   NOTE: for xml2rfc-1.26 and earlier ONLY, add an additional
   modification in step #3:

      Patch .xml2rfc.rc (xml2rfc-1.26 and earlier).  The purpose of the
      patch is to append library names in a format compatible with the
      OS; on Windows XP, this replaces the Cygwin's "/" with Windows'
      "\".


   --- .xml2rfc.rc.orig    Thu Jul 24 13:58:00 2003
   +++ .xml2rfc.rc    Wed Oct 20 10:59:02 2004
   @@ -9,7 +9,8 @@
    if {[catch { set env(XML_LIBRARY) } library]} {
        set library ""
        foreach bibxmlD [lsort -dictionary [glob -nocomplain ~/rfcs/bibxml/*]] {
   -        append library $sep$bibxmlD
   +        set natbibD [file nativename $bibxmlD]
   +        append library $sep$natbibD
        }
    }














Rose                                                           [Page 13]

README                        xml2rfc v1.28                 January 2005


Appendix D.  Copyrights

   (c) 2003-2005 Marshall T.  Rose

   Hold harmless the author, and any lawful use is allowed.














































Rose                                                           [Page 14]

