

The README file                                                  M. Rose
                                            Dover Beach Consulting, Inc.
                                                           December 2001


                             xml2rfc v1.10


Table of Contents

   1.    Introduction . . . . . . . . . . . . . . . . . . . . . . . .  2
   2.    Requirements . . . . . . . . . . . . . . . . . . . . . . . .  2
   2.1   Tcl/Tk version 8 . . . . . . . . . . . . . . . . . . . . . .  2
   2.2   TclXML version 1.1.1 . . . . . . . . . . . . . . . . . . . .  3
   3.    Testing  . . . . . . . . . . . . . . . . . . . . . . . . . .  3
   3.1   Testing under a windowing system . . . . . . . . . . . . . .  3
   3.2   Testing without a windowing system . . . . . . . . . . . . .  4
   4.    Next steps . . . . . . . . . . . . . . . . . . . . . . . . .  4
   4.1   Processing Instructions  . . . . . . . . . . . . . . . . . .  4
   4.1.1 Option Settings  . . . . . . . . . . . . . . . . . . . . . .  5
   4.1.2 Include Files  . . . . . . . . . . . . . . . . . . . . . . .  6
   5.    Additions to RFC 2629  . . . . . . . . . . . . . . . . . . .  6
   6.    Limitations  . . . . . . . . . . . . . . . . . . . . . . . .  7
         References . . . . . . . . . . . . . . . . . . . . . . . . .  8
         Author's Address . . . . . . . . . . . . . . . . . . . . . .  8
   A.    MacOS 9 Installation (courtesy of Ned Freed) . . . . . . . .  8


























Rose                                                            [Page 1]

README                        xml2rfc v1.10                December 2001


1. Introduction

   This is a package to convert memos written in XML to the RFC format.

   If you don't want to install any software, you can use the web-based
   service [2].

2. Requirements

2.1 Tcl/Tk version 8

   You need to have Tcl/Tk version 8 running on your system.  Tcl is a
   scripting language, Tk is Tcl with support for your windowing system.

   To get a source or binary distribution for your system, go to the
   Scriptics website [3] and install it.  If you get the binary
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



















Rose                                                            [Page 2]

README                        xml2rfc v1.10                December 2001


2.2 TclXML version 1.1.1

   You need to also have TclXML version 1.1.1 running on your system.
   TclXML is a Tcl package that parses XML.

   We've included a copy of TclXML in this release, you can also look in
   the TclXML site [4].

   For example, on Unix, you'd probably put the files somewhere under

       /usr/local/lib/tcl8.4/TclXML-1.1

   or

       C:\Program Files\Tcl\lib\tcl8.4\TclXML-1.1\

   depending on whether you're on UNIX or Windows.

   To find out where you should put the directory, type this command:

       % tclsh
       tclsh> set auto_path

   This will print a list containing the directories where Tcl looks for
   libraries.  You should put the "TclXML-1.1" directory in exactly one
   of these directories.

3. Testing

   Now test your installation.

3.1 Testing under a windowing system

   Type this command from the shell:

       % xml2rfc.tcl















Rose                                                            [Page 3]

README                        xml2rfc v1.10                December 2001


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


4. Next steps

   Read either rfc2629.txt [1] or rfc2629.html.  In particular, Section
   3 has some good information.

4.1 Processing Instructions

   A *processing instruction* is a directive to an XML application.  If
   you want to give directives to 'xml2rfc', the PIs look like this:

       <?rfc keyword='value'?>







Rose                                                            [Page 4]

README                        xml2rfc v1.10                December 2001


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

       background  ""          when producing an .html file, use this
                               image

   Remember, that as with everything else in XML, keywords and values
   are case-sensitive.










Rose                                                            [Page 5]

README                        xml2rfc v1.10                December 2001


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
   so on) on the 'xml2rfc' homepage [5].

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




Rose                                                            [Page 6]

README                        xml2rfc v1.10                December 2001


   o  If the 'style' attribute of the 'list' element has either of the
      values "hanging" or "format", then a second, optional attribute,
      called 'hangIndent' is consulted.

   For more information on these last two additions, see Section 2.3.1.2
   of the html or text [6] versions of the 2629bis document for the
   details.

6. Limitations

   o  The 'figure' element's 'title' attribute is ignored, except when
      generating HTML.

   o  The 'artwork' element's 'name' and 'type' attributes are ignored.

   o  The 'xref' element's 'pageno' attribute is ignored.



































Rose                                                            [Page 7]

README                        xml2rfc v1.10                December 2001


References

   [1]  Rose, M., "Writing I-Ds and RFCs using XML", RFC 2629, June
        1999.

   [2]  <http://xml.resource.org/>

   [3]  <http://www.scriptics.com/software/tcltk/8.4.html>

   [4]  <http://www.zveno.com/zm.cgi/in-tclxml/>

   [5]  <http://xml.resource.org/>

   [6]  <draft-mrose-writing-rfcs.txt>


Author's Address

   Marshall T. Rose
   Dover Beach Consulting, Inc.
   POB 255268
   Sacramento, CA  95865-5268
   US

   Phone: +1 916 483 8878
   EMail: mrose@dbc.mtview.ca.us

Appendix A. MacOS 9 Installation (courtesy of Ned Freed)

   1.  Install Tcl/Tk 8.3.4

   2.  When you performed Step 1, a folder in your "Extensions" folder
       called "Tool Command Language" was created.  Create a new folder
       under "Extensions", with any name you like.

   3.  From the TclXML 1.1.1 distribution, move the files
       "pkgIndex.tcl", "sgml.tcl", and "xml.tcl" to this new folder.

   4.  Drag the file "xml2rfc.tcl" onto the "Drag & Drop Tclets"
       application that was installed in Step 1.

   5.  When asked for an appropriate "wish" stub, select "Wish 8.3.4".

   6.  The "Drap & Drop Tclets" application will write out an executable
       version of 'xml2rfc'.






Rose                                                            [Page 8]

