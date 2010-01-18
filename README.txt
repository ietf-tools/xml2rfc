


The README file                                                  M. Rose
                                            Dover Beach Consulting, Inc.
                                                               C. Levert
                                                         August 11, 2005


                             xml2rfc v1.30


Table of Contents

   1.      Introduction . . . . . . . . . . . . . . . . . . . . . . .  2
   2.      Requirements . . . . . . . . . . . . . . . . . . . . . . .  3
   3.      Testing  . . . . . . . . . . . . . . . . . . . . . . . . .  4
   3.1.    Testing under a windowing system . . . . . . . . . . . . .  4
   3.2.    Testing without a windowing system . . . . . . . . . . . .  4
   4.      Next steps . . . . . . . . . . . . . . . . . . . . . . . .  5
   4.1.    Processing Instructions  . . . . . . . . . . . . . . . . .  5
   4.1.1.  Option Settings  . . . . . . . . . . . . . . . . . . . . .  5
   4.1.2.  Include Files  . . . . . . . . . . . . . . . . . . . . . .  8
   5.      The Page Model . . . . . . . . . . . . . . . . . . . . . .  9
   6.      Additions to RFC 2629  . . . . . . . . . . . . . . . . . . 10
   7.      Limitations of xml2rfc . . . . . . . . . . . . . . . . . . 12
   8.      References . . . . . . . . . . . . . . . . . . . . . . . . 12
   A.      MacOS 9 Installation (courtesy of Ned Freed) . . . . . . . 13
   B.      rfc2629.xslt (courtesy of Julian Reschke)  . . . . . . . . 14
   C.      MS-Windows XP/Cygwin Installation (courtesy of Joe
           Touch) . . . . . . . . . . . . . . . . . . . . . . . . . . 15
   D.      A Special Thanks . . . . . . . . . . . . . . . . . . . . . 16
   E.      Copyrights . . . . . . . . . . . . . . . . . . . . . . . . 17
           Authors' Addresses . . . . . . . . . . . . . . . . . . . . 18




















Rose & Levert                                                   [Page 1]

README                        xml2rfc v1.30                  August 2005


1.  Introduction

   This is a package to convert memos written in XML to the RFC format.

   If you don't want to install any software, you can use the web-based
   service [2].













































Rose & Levert                                                   [Page 2]

README                        xml2rfc v1.30                  August 2005


2.  Requirements

   You need to have Tcl/Tk version 8 running on your system.  Tcl is a
   scripting language, Tk is Tcl with support for your windowing system.

   To get a source or binary distribution for your system, go to the Tcl
   Developer Xchange website [3] and install it.  If you get the binary
   distribution, this is pretty simple.

   Of course, you may already have Tcl version 8.  To find out, try
   typing this command from the shell (or the "MS-DOS Prompt"):

       % tclsh

   If the program launches, you're good to go with Tcl version 8.

   If you are running under a windowing system (e.g., X or MS-Windows),
   you can also try:

       % wish

   If a new window comes up along with a "Console" window, then you're
   good to go with Tk version 8.

   Finally, you may notice a file called "xml2sgml.tcl" in the
   distribution.  It contains some extra functionality for a few special
   users -- so, if you don't know what it is, don't worry about it...
























Rose & Levert                                                   [Page 3]

README                        xml2rfc v1.30                  August 2005


3.  Testing

   Now test your installation.

3.1.  Testing under a windowing system

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

3.2.  Testing without a windowing system

   Type this command from the shell:

       % tclsh

   If the program launches, type this command to it:

       % source xml2rfc.tcl

   and you should see these four lines:

       invoke as "xml2rfc   inputfile outputfile"
              or "xml2txt   inputfile"
              or "xml2html  inputfile"
              or "xml2nroff inputfile"










Rose & Levert                                                   [Page 4]

README                        xml2rfc v1.30                  August 2005


4.  Next steps

   Read the 2629bis [4] document.  In particular, Section 3 has some
   good information.

4.1.  Processing Instructions

   A _processing instruction_ contains directives to an XML application.
   If you want to give directives to *xml2rfc*, the processing
   instructions (PIs) look like this:

       <?rfc keyword='value'?>

   Of course, if you like the default behavior, you don't need any
   behavior-modifying directives in your input file!  Although *xml2rfc*
   supports putting several attribute-like directives in one PI, be
   warned that rfc2629.xslt (Appendix B) does not support it and that
   there are issues in doing this for a non-include-file directive
   following an include-file directive (Section 4.1.2).  It is good
   practice to always surround the value with either single or double
   quotes.

4.1.1.  Option Settings

                      The list of valid keywords are:

   +-------------+-----------+-----------------------------------------+
   |     keyword |  default  | meaning                                 |
   +-------------+-----------+-----------------------------------------+
   |  autobreaks |    yes    | automatically force page breaks to      |
   |             |           | avoid widows and orphans (not perfect)  |
   |             |           |                                         |
   |  background |     ""    | when producing a html file, use this    |
   |             |           | image                                   |
   |             |           |                                         |
   |  colonspace |     no    | put two spaces instead of one after     |
   |             |           | each colon (":") in txt or nroff files  |
   |             |           |                                         |
   |    comments |     no    | render <cref> information               |
   |             |           |                                         |
   |     compact |     no    | when producing a txt/nroff file, try to |
   |             |           | conserve vertical whitespace            |
   |             |           |                                         |
   |     editing |     no    | insert editing marks for ease of        |
   |             |           | discussing draft versions               |
   |             |           |                                         |





Rose & Levert                                                   [Page 5]

README                        xml2rfc v1.30                  August 2005


   |  emoticonic |     no    | automatically replaces input sequences  |
   |             |           | such as "|*text|" by, e.g.,             |
   |             |           | "<strong>text</strong;>" in html output |
   |             |           |                                         |
   |      footer |     ""    | override the center footer string       |
   |             |           |                                         |
   |      header |     ""    | override the leftmost header string     |
   |             |           |                                         |
   |     include |    n/a    | see Section 4.1.2                       |
   |             |           |                                         |
   |      inline |     no    | if comments is "yes", then render       |
   |             |           | comments inline; otherwise render them  |
   |             |           | in an "Editorial Comments" section      |
   |             |           |                                         |
   | iprnotified |     no    | include boilerplate from                |
   |             |           | Section 10.4(d) of [1]                  |
   |             |           |                                         |
   |  linkmailto |    yes    | generate mailto: URL, as appropriate    |
   |             |           |                                         |
   |    linefile |    n/a    | a string like "35:file.xml" or just     |
   |             |           | "35" (file name then defaults to the    |
   |             |           | containing file's real name or to the   |
   |             |           | latest linefile specification that      |
   |             |           | changed it) that will be used to        |
   |             |           | override *xml2rfc*'s reckoning of the   |
   |             |           | current input position (right after     |
   |             |           | this PI) for warning and error          |
   |             |           | reporting purposes (line numbers are    |
   |             |           | 1-based)                                |
   |             |           |                                         |
   |   needLines |    n/a    | an integer hint indicating how many     |
   |             |           | contiguous lines are needed at this     |
   |             |           | point in the output                     |
   |             |           |                                         |
   |     private |     ""    | produce a private memo rather than an   |
   |             |           | RFC or Internet-Draft                   |
   |             |           |                                         |
   |      slides |     no    | when producing a html file, produce     |
   |             |           | multiple files for a slide show         |
   |             |           |                                         |
   |    sortrefs |     no    | sort references                         |
   |             |           |                                         |
   |      strict |     no    | try to enforce the ID-nits conventions  |
   |             |           | and DTD validity                        |
   |             |           |                                         |






Rose & Levert                                                   [Page 6]

README                        xml2rfc v1.30                  August 2005


   |  subcompact | (compact) | if compact is "yes", then you can make  |
   |             |           | things a little less compact by setting |
   |             |           | this to "no" (the default value is the  |
   |             |           | current value of the compact PI)        |
   |             |           |                                         |
   |     symrefs |     no    | use anchors rather than numbers for     |
   |             |           | references                              |
   |             |           |                                         |
   |         toc |     no    | generate a table-of-contents            |
   |             |           |                                         |
   | tocappendix |    yes    | control whether the word "Appendix"     |
   |             |           | appears in the table-of-content         |
   |             |           |                                         |
   |    tocdepth |     3     | if toc is "yes", then this determines   |
   |             |           | the depth of the table-of-contents      |
   |             |           |                                         |
   |   tocindent |    yes    | if toc is "yes", then setting this to   |
   |             |           | "yes" will indent subsections in the    |
   |             |           | table-of-contents                       |
   |             |           |                                         |
   |   tocompact |    yes    | if toc is "yes", then setting this to   |
   |             |           | "no" will make it a little less compact |
   |             |           |                                         |
   |   tocnarrow |    yes    | affects horizontal spacing in the       |
   |             |           | table-of-content                        |
   |             |           |                                         |
   |    topblock |    yes    | put the famous header block on the      |
   |             |           | first page                              |
   |             |           |                                         |
   |     typeout |    n/a    | during processing pass 2, print the     |
   |             |           | value to standard output at that point  |
   |             |           | in processing                           |
   |             |           |                                         |
   |   useobject |     no    | when producing a html file, use the     |
   |             |           | "<object>" html element with inner      |
   |             |           | replacement content instead of the      |
   |             |           | "<img>" html element, when a source xml |
   |             |           | element includes an "src" attribute     |
   +-------------+-----------+-----------------------------------------+

    Remember that, as with everything else in XML, keywords and values
                            are case-sensitive.

   With the exception of the "needLines", "typeout", and "include"
   directives, you normally put all of these processing instructions at
   the beginning of the document (right after the XML declaration).





Rose & Levert                                                   [Page 7]

README                        xml2rfc v1.30                  August 2005


4.1.2.  Include Files

   *xml2rfc* has an include-file facility, e.g.,

       <?rfc include='file'?>

   *xml2rfc* will consult the "XML_LIBRARY" environment variable for a
   search path of where to look for files.  (If this environment
   variable isn't set, the directory containing the file that contains
   the include-file directive is used.)  The file's contents are
   inserted right after the PI.  Putting non-include-file directives
   (especially needLines ones) after an include-file one in the same PI
   may not work as expected because of this.  Remember that file names
   are generally case-sensitive and that an input file that is
   distributed to the outside world may be processed on a different
   operating system than that used by its author.

   You can also have *xml2rfc* set the "XML_LIBRARY" environment
   variable directly, by creating a file called ".xml2rfc.rc" in the
   directory where your main file is, e.g.,

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
   so on) on the *xml2rfc* homepage [2].





Rose & Levert                                                   [Page 8]

README                        xml2rfc v1.30                  August 2005


5.  The Page Model

   The *html* rendering engine does not need to have a tightly defined
   page model.

   The *txt* and *nr* rendering engines assume the following page model.

   Each line has at most 72 columns from the left edge, including any
   left margin, but excluding the line terminator.  Every output
   character is from the ASCII repertoire and the only control character
   used is the line-feed (LF); the character-tabulation (HT) character
   is never used.

   Each page has the following lines (in 1-based numbering, as reported
   to the user, but contrary to *xml2rfc*'s internal 0-based numbering):

       1: header line (blank line on first page)

       2: blank line

       3: blank line

       4: 1st line of content

      ...

      51: 48th line of content

      52: blank line

      53: blank line

      54: blank line

      55: footer line

      56: form-feed character (followed by line terminator)

   Once processed through *nroff* and the "fix.sh" script (from
   2-nroff.template [5]), the *nr* output differs from this in two ways.
   It has three extra blank lines (that could be numbered -2, -1, and 0,
   for a total of six) at the very beginning of the document (so the
   first page is that much longer).  It also has no line terminator
   following the very last form-feed character of the file.  These
   differences originate in the design of the "fix.sh" script.

   Header and footer lines each have three parts: left, center, and
   right.



Rose & Levert                                                   [Page 9]

README                        xml2rfc v1.30                  August 2005


6.  Additions to RFC 2629

   A few additions have been made to the format originally defined in
   RFC 2629.  In particular, Appendix C of the 2629bis document
   enumerates the additions.

   In addition, *xml2rfc* recognizes the undocumented "src", "alt",
   "width", and "height" attributes in the "figure" and "artwork"
   elements, but only if HTML is being generated.  Here are two
   examples, one for each case.

   Here, the attributes are added to the "artwork" element.

             <figure>
                 <preamble>This is the preamble.</preamble>
                 <artwork src='layers.png'
                          alt='[picture of layers only]'>
             .-----------.
             | ASCII art |
             `-----------'
             </artwork>
                 <postamble>This is the postamble.</postamble>
             </figure>

   In this case, the "preamble" and "postamble" elements are kept and an
   "img" tag is placed in the HTML output to replace the whole "artwork"
   element and its textual drawing, which are ignored.

   Here, the attributes are added to the "figure" element.

             <figure src='layers.png'
                     alt='[picture of layers and explanation]'>
                 <preamble>This is the preamble.</preamble>
                 <artwork>
             .-----------.
             | ASCII art |
             `-----------'
             </artwork>
                 <postamble>This is the postamble.</postamble>
             </figure>

   In this case, an "img" tag is placed in the HTML output to replace
   the whole contents of the "figure" element (the "preamble",
   "artwork", and "postamble" inner elements and the textual drawing
   itself) which are ignored.

   *xml2rfc* also recognizes an undocumented "align" attribute (with
   possible values "left", "center", or "right") in the "figure" and



Rose & Levert                                                  [Page 10]

README                        xml2rfc v1.30                  August 2005


   "artwork" elements.  It affects the whole content of the targeted
   element for all types of generated output.  Its default is inherited
   from the parent of its element.
















































Rose & Levert                                                  [Page 11]

README                        xml2rfc v1.30                  August 2005


7.  Limitations of xml2rfc

   o  The "figure" element's "title" attribute is ignored, except when
      generating HTML.

   o  The "xref" element's "pageno" attribute is ignored.


8.  References

   [1]  Bradner, S., "The Internet Standards Process -- Revision 3",
        BCP 9, RFC 2026, October 1996.

   [2]  <http://xml.resource.org/>

   [3]  <http://www.tcl.tk/software/tcltk/8.4.html>

   [4]  <draft-mrose-writing-rfcs.html>

   [5]  <ftp://ftp.rfc-editor.org/in-notes/rfc-editor/2-nroff.template>

   [6]  <http://greenbytes.de/tech/webdav/>

   [7]  <http://greenbytes.de/tech/webdav/rfc2629xslt/rfc2629xslt.html>

   [8]  <http://www.cygwin.com/>

   [9]  <http://wiki.tcl.tk/2?cygwin>























Rose & Levert                                                  [Page 12]

README                        xml2rfc v1.30                  August 2005


Appendix A.  MacOS 9 Installation (courtesy of Ned Freed)

   1.  Install Tcl/Tk 8.3.4

   2.  When you performed Step 1, a folder in your "Extensions" folder
       called "Tool Command Language" was created.  Create a new folder
       under "Extensions", with any name you like.

   3.  Drag the file "xml2rfc.tcl" onto the "Drag & Drop Tclets"
       application that was installed in Step 1.

   4.  When asked for an appropriate "wish" stub, select "Wish 8.3.4".

   5.  The "Drag & Drop Tclets" application will write out an executable
       version of *xml2rfc*.




































Rose & Levert                                                  [Page 13]

README                        xml2rfc v1.30                  August 2005


Appendix B.  rfc2629.xslt (courtesy of Julian Reschke)

   The file "rfc2629.xslt" can be used with an XSLT-capable formatter
   (e.g., Saxon, Xalan, xsltproc, or MSIE6) to produce HTML.  A word of
   warning though: the XSLT script only supports a limited subset of the
   processing instruction directives discussed earlier (Section 4.1) and
   each attribute-like directive must be in its own PI (i.e., "<?rfc
   keyword='value'?>").  The latest version can be downloaded from the
   original site [6] which also hosts its documentation [7].










































Rose & Levert                                                  [Page 14]

README                        xml2rfc v1.30                  August 2005


Appendix C.  MS-Windows XP/Cygwin Installation (courtesy of Joe Touch)

   1.  install Cygwin: follow instructions at the Cygwin website [8]
       (also visit the Cygwin pages on the Tcl Wiki [9]), make sure to
       select "tcltk" in "Libs"

   2.  place a copy of xml2rfc files on a local drive, e.g., in
       "C:\xml2rfc" NOTE: for xml2rfc-1.26 and earlier, see NOTE below.

   3.  place a copy of bibxml* files on a local drive, e.g., in
       "C:\xmlbib\"

   4.  edit ".xml2rfc.rc" to indicate the "bibxml*" library path, e.g.,
       as per Step 3, change "~/rfca/bibxml/*" to "/cygdrive/c/xmlbib/*"

   5.  run xml2rfc as follows: "tclsh /cygdrive/c/xml2rfc/xml2rfc.tcl"

   NOTE: for xml2rfc-1.26 and earlier ONLY, add an additional
   modification in Step 3:

      Patch ".xml2rfc.rc" (xml2rfc-1.26 and earlier).  The purpose of
      the patch is to append library names in a format compatible with
      the OS; on MS-Windows XP, this replaces the Cygwin's "/" with MS-
      Windows' "\".


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














Rose & Levert                                                  [Page 15]

README                        xml2rfc v1.30                  August 2005


Appendix D.  A Special Thanks

   A special thanks to Charles Levert for the v1.29 release, which
   includes many internal improvements made to the rendering engines.















































Rose & Levert                                                  [Page 16]

README                        xml2rfc v1.30                  August 2005


Appendix E.  Copyrights

   Copyright (C) 2003-2005 Marshall T. Rose

   Hold harmless the author, and any lawful use is allowed.














































Rose & Levert                                                  [Page 17]

README                        xml2rfc v1.30                  August 2005


Authors' Addresses

   Marshall T. Rose
   Dover Beach Consulting, Inc.
   POB 255268
   Sacramento, CA  95865-5268
   US

   Phone: +1 916 483 8878
   Email: mrose@dbc.mtview.ca.us


   Charles Levert
   Montreal, Qc
   Canada

   Email: charles.levert@gmail.com


































Rose & Levert                                                  [Page 18]

