

The README file                                                  M. Rose
                                            Dover Beach Consulting, Inc.
                                                           March 2, 2002


                             xml2rfc v1.11


Table of Contents

   1.    Introduction . . . . . . . . . . . . . . . . . . . . . . . .  2
   2.    Requirements . . . . . . . . . . . . . . . . . . . . . . . .  3
   3.    Testing  . . . . . . . . . . . . . . . . . . . . . . . . . .  4
   3.1   Testing under a windowing system . . . . . . . . . . . . . .  4
   3.2   Testing without a windowing system . . . . . . . . . . . . .  4
   4.    Next steps . . . . . . . . . . . . . . . . . . . . . . . . .  5
   4.1   Processing Instructions  . . . . . . . . . . . . . . . . . .  5
   4.1.1 Option Settings  . . . . . . . . . . . . . . . . . . . . . .  5
   4.1.2 Include Files  . . . . . . . . . . . . . . . . . . . . . . .  6
   5.    Additions to RFC 2629  . . . . . . . . . . . . . . . . . . .  7
   6.    Limitations  . . . . . . . . . . . . . . . . . . . . . . . .  8
         Author's Address . . . . . . . . . . . . . . . . . . . . . .  9
   A.    MacOS 9 Installation (courtesy of Ned Freed) . . . . . . . . 10





























Rose                                                            [Page 1]

README                        xml2rfc v1.11                   March 2002


1. Introduction

   This is a package to convert memos written in XML to the RFC format.

   If you don't want to install any software, you can use the web-based
   service [1].













































Rose                                                            [Page 2]

README                        xml2rfc v1.11                   March 2002


2. Requirements

   You need to have Tcl/Tk version 8 running on your system.  Tcl is a
   scripting language, Tk is Tcl with support for your windowing system.

   To get a source or binary distribution for your system, go to the
   Scriptics website [2] and install it.  If you get the binary
   distribution, this is pretty simple.

   Of course, you may already have Tcl version 8.  To find out, try
   typing this command from the shell (including the "MS-DOS Prompt"):

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

README                        xml2rfc v1.11                   March 2002


3. Testing

   Now test your installation.

3.1 Testing under a windowing system

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

3.2 Testing without a windowing system

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

README                        xml2rfc v1.11                   March 2002


4. Next steps

   Read the 2629bis [3] document.  In particular, Section 3 has some
   good information.

4.1 Processing Instructions

   A *processing instruction* is a directive to an XML application.  If
   you want to give directives to 'xml2rfc', the PIs look like this:

       <?rfc keyword='value'?>


4.1.1 Option Settings

   The list of valid keywords are:

       keyword     default     meaning
       =======     =======     =======
       compact     no          when producing a .txt file, try to
                               conserve vertical whitespace

       subcompact  compact     if compact is "yes", then setting
                               this to "no" will make things a
                               little less compact

       toc         no          generate a table-of-contents

       tocompact   yes         if toc is "yes", then setting this to
                               "no" will make it a little less compact

       editing     no          insert editing marks for ease of
                               discussing draft versions

       private     ""          produce a private memo rather than
                               an RFC or Internet-Draft.

       header      ""          override the leftmost header string

       footer      ""          override the center footer string

       slides      no          when producing an .html file, produce
                               multiple files for a slide show

       sortrefs    no          sort references

       symrefs     no          use anchors rather than numbers for
                               references



Rose                                                            [Page 5]

README                        xml2rfc v1.11                   March 2002


       background  ""          when producing an .html file, use this
                               image

   Remember, that as with everything else in XML, keywords and values
   are case-sensitive.

4.1.2 Include Files

   'xml2rfc' has an include-file facility, e.g.,

       <?rfc include='file'?>

   'xml2rfc' will consult the $XML_LIBRARY environment variable for a
   search path of where to look for files.  (If this envariable isn't
   set, the directory containing the file that contains the include-file
   directive is used.)

   You can also have 'xml2rfc' set this envariable directly, by
   including a file called ".xml2rfc.rc" in the directory where your
   main file is, e.g.,

   global env

   if {![info exists env(XML_LIBRARY)]} {
       set env(XML_LIBRARY) \
           ";\\home\\rfcs\\include;\\home\\rfcs\\bibxml"
   }
   set nativeD [file nativename $inputD]
   if {[lsearch [split $env(XML_LIBRARY) ";"] $nativeD] < 0} {
       set env(XML_LIBRARY) "$nativeD;$env(XML_LIBRARY)"
   }

   which, on Windows, sets the envariable to a default value, and then
   inserts, at the front, the directory where your main file is.

   There are links to various bibliographic databases (RFCs, I-Ds, and
   so on) on the 'xml2rfc' homepage [4].














Rose                                                            [Page 6]

README                        xml2rfc v1.11                   March 2002


5. Additions to RFC 2629

   o  The 'artwork' element has an undocumented 'src' attribute that is
      consulted only if slides are being generated, e.g.,

          <figure><artwork src='layers.gif' /></figure>

   o  The 'artwork' element has optional 'name' and 'type' attributes.

   o  The 'references' element may occur more than once in the 'back'
      element (e.g., for normative and non-normative references).
      Further, the element has an optional 'title' attribute.

   o  The value of the 'list' element's 'style' attribute can start with
      "format ".

   o  If the 'style' attribute of the 'list' element has either of the
      values "hanging" or "format", then a second, optional attribute,
      called 'hangIndent' is consulted.

   For more information on these last two additions, see Section 2.3.1.2
   of the 2629bis document for the details.





























Rose                                                            [Page 7]

README                        xml2rfc v1.11                   March 2002


6. Limitations

   o  The 'figure' element's 'title' attribute is ignored, except when
      generating HTML.

   o  The 'xref' element's 'pageno' attribute is ignored.













































Rose                                                            [Page 8]

README                        xml2rfc v1.11                   March 2002


URIs

   [1]  <http://xml.resource.org/>

   [2]  <http://www.scriptics.com/software/tcltk/8.4.html>

   [3]  <draft-mrose-writing-rfcs.html>

   [4]  <http://xml.resource.org/>


Author's Address

   Marshall T. Rose
   Dover Beach Consulting, Inc.
   POB 255268
   Sacramento, CA  95865-5268
   US

   Phone: +1 916 483 8878
   EMail: mrose@dbc.mtview.ca.us






























Rose                                                            [Page 9]

README                        xml2rfc v1.11                   March 2002


Appendix A. MacOS 9 Installation (courtesy of Ned Freed)

   1.  Install Tcl/Tk 8.3.4

   2.  When you performed Step 1, a folder in your "Extensions" folder
       called "Tool Command Language" was created.  Create a new folder
       under "Extensions", with any name you like.

   3.  Drag the file "xml2rfc.tcl" onto the "Drag & Drop Tclets"
       application that was installed in Step 1.

   4.  When asked for an appropriate "wish" stub, select "Wish 8.3.4".

   5.  The "Drap & Drop Tclets" application will write out an executable
       version of 'xml2rfc'.




































Rose                                                           [Page 10]

