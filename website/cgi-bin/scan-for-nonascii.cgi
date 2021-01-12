#!/usr/bin/env python3

"""
This is a small web tool that will scan a given file for
non-ASCII and non-printable characters.
All such characters will be highlighted.
Tooltips or inline annotations will be presented with information
about each such character, along with optional line numbers.
Optionally, ONLY the errant lines will be shown.
"""

import cgi
import html
import io
import os
import cgitb

HEXC = "0123456789ABCDEF"
ESCAPE = {
    '"': "&quot;",
    "&": "&amp;",
    "'": "&apos;",
    "<": "&lt;",
    ">": "&gt;",
}

def hexdump(ln, start=0, end=None, by=16):
    """ 
    Convert a bytearray into hexdump format:
    00000000:  00 09 0a 0b 0c 0d 0e 0f 40 49 4a 4b 4c 4d 4e 4f  ........@IJKLMNO
    00000010:  00 09 0a 0b 0c 0d 0e 0f 40 49 4a 4b 4c 4d 4e 4f  ........@IJKLMNO
    
    Start the dump at the given starting offset, through the specified end point.
    Generate {by} bytes per line.
    Return the output as a string.
    """
    ret = io.StringIO()
    if end is None:
        end = len(ln)
    if not isinstance(by, int) or by <= 0:
        raise ValueError("by value must be a positive integer: {by}")
    for i in range(start, end, by):
        curend = i + by
        extra = 0
        if curend > end:
            extra = curend - end
            curend = end
        ret.write(f"{i:08x}: ")
        for j in range(i, curend):
            b = ln[j]
            ret.write(f" {HEXC[b//16]}{HEXC[b%16]}")
        for j in range(extra):
            ret.write("   ")
        ret.write("  ")
        for j in range(i, curend):
            b = ln[j]
            if b > 0x20 and b < 0x7f:
                ret.write(chr(b))
            else:
                ret.write(".")
        for j in range(extra):
            ret.write(" ")
        ret.write("\n")
    return ret.getvalue()

def prToolTip(ret, an):
    """ write an annotation as a tooltip class """
    ret.write("<span class='ttt'>")
    ret.write(an)
    ret.write("</span>")
    

def prCharAsHex(ret, b, cl, an, annotate):
    """ 
    Print a character (in the proper CSS class) as the hex equivalent, along with an annotation
    """
    ret.write(f"<div class='{cl}'>")
    prToolTip(ret, an)
    ret.write("<span class='sup'>")
    ret.write(HEXC[b//16])
    ret.write("</span><span class='sub'>")
    ret.write(HEXC[b%16])
    ret.write("</span>")
    ret.write("</div>")
    if annotate:
        ret.write(f"<span class='an'>{an}</span>")

def expandChar(ret, b, asBytes=False, scanOnly=False, annotate=False, escape=False):
    """
    Look at a character and treat it for scanString.
    Optionally, write an expanded version of the text to ret.
    While expanding, also optionally:
    *) annotate=True: Add inline annotations with the highlighted characters.
    *) escape=True: Convert HTML-special characters into their equivalent &-format.
    """
    foundNonPrintable = False
    foundMeta = False
    # ret.write(f"b={b}\n")
    if b in [0x09, 0x0a, 0x0d]: # printable control characters
        if not scanOnly:
            if escape and b == 0x0a:
                ret.write("<br/>\n")
            else:
                ret.write(chr(b))
        else:
            pass

    elif b < 32: # control characters
        if not scanOnly:
            an = f" 0x{HEXC[b//16]}{HEXC[b%16]}/Control-{chr(0x40 + b)} "
            prCharAsHex(ret, b, 'ct tt', an, annotate)
        foundNonPrintable = True

    elif b > 0x7f:	# "meta" and "unicode" characters
        if not scanOnly:
            if asBytes:	# "meta"
                an = f" 0x{HEXC[b//16]}{HEXC[b%16]}/non-ASCII "
                prCharAsHex(ret, b, 'na tt', an, annotate)
            else:	# "unicode"
                an = " Unicode character "
                ret.write("<span class='uni tt'>")
                prToolTip(ret, an)
                ret.write(chr(b))
                ret.write("</span>")
                if annotate:
                    ret.write(f"<span class='an'>{an}</span>")
        foundMeta = True

    else:		# "normal" characters
        if not scanOnly:
            if escape and b in [0x22, 0x26, 0x27, 0x3c, 0x3e]: # "&'<>
                ret.write(ESCAPE[chr(b)])
            else:
                ret.write(chr(b))

    return foundNonPrintable, foundMeta

def scanString(s, asBytes=False, scanOnly=False, annotate=False, escape=False):
    """
    Scan a string for non-printables and characters > 127.
    If scanOnly is True, do not fill in the output string.
    Return a tuple:
        foundNonPrintable, foundMeta, expandedString
    """
    ret = io.StringIO()
    foundNonPrintable = False
    foundMeta = False
    if asBytes:
        for b in s:
            fnp, fm = expandChar(ret, b, asBytes, scanOnly, annotate, escape)
            foundNonPrintable |= fnp
            foundMeta |= fm
    else:
        for b in s:
            fnp, fm = expandChar(ret, ord(b), asBytes, scanOnly, annotate, escape)
            foundNonPrintable |= fnp
            foundMeta |= fm

    return foundNonPrintable, foundMeta, ret.getvalue()

def esc(s):
    """
    Escape a string for HTML using html.escape(s, quote=True)
    and changing newlines to <br/>s
    """
    return html.escape(s, quote=True).replace("\n", "<br/>")

def process(fn, f, addAnnotations, onlyShowNonAscii, showLineNumbers):
    """ Read a file and highlight all non-ascii characters """
    if fn is None:
        fn = "unnamed"
    print(f"<h2>Scanning {esc(fn)}</h2>")

    fullfile = f.read()
    try:
        # try processing the file as ASCII
        asAscii = fullfile.decode('us-ascii')
        findNonPrintable, findMeta, _ = scanString(asAscii, scanOnly=True)
        # print(f"findNonPrintable={findNonPrintable}, findMeta={findMeta}")
        if findNonPrintable:
            print(f"The file is ASCII, with non-printables<br/>")
        else:
            print(f"The file is ASCII<br/>")
        # print("<hr>")
        # _, _, expanded1 = scanString(asAscii, scanOnly=False, annotate=addAnnotations, escape=True)
        # print(expanded1)

    except UnicodeDecodeError as e1:
        # try processing the file as UTF-8
        # print(f"Exception: {type(e1)}, {e1}<br/>")
        try:
            asUtf8 = fullfile.decode('utf-8')
            findNonPrintable, findMeta, _ = scanString(asUtf8, scanOnly=True)
            # print(f"findNonPrintable={findNonPrintable}, findMeta={findMeta}")
            if findNonPrintable:
                print(f"The file is UTF-8, with non-printables<br/>")
            else:
                print(f"The file is UTF-8<br/>")

            # print("<hr>")
            # _, _, expanded2 = scanString(asUtf8, scanOnly=False, annotate=addAnnotations, escape=True)
            # print(expanded2)

        except UnicodeDecodeError as e2:
            # Those didn't work, so process a line at a time.
            # print(f"Exception2: {type(e2)}, {e2}<br/>")
            print(f"The file has non-UTF-8 data. In the following, a line with both UTF-8 and non-UTF-8 will mark all as 'non-ASCII'<br/>")

    except Exception as e99:
        print(f"Something happened while converting or printing:<br/>{e99}<br/>")

    print("<hr>")
    with io.BytesIO(fullfile) as fp:
        for num, ln in enumerate(fp):
            np1 = num + 1
            # print(f"type(ln)={type(ln)}")
            # print(f"len(ln)={len(ln)}")
            try:
                lnasUtf8 = ln.decode('utf-8')
                findNonPrintable, findMeta, expanded3 = scanString(lnasUtf8, asBytes=False, scanOnly=False, annotate=addAnnotations, escape=True)
                if findNonPrintable or findMeta or (not onlyShowNonAscii):
                    if showLineNumbers:
                        print(f"{np1}: ", end="")
                    print(expanded3)
            except UnicodeDecodeError as e3:
                # print(f"Exception3: {type(e3)}, {e3}<br/>")
                try:
                    # print(f"len(ln)={len(ln)}")
                    findNonPrintable, findMeta, expanded4 = scanString(ln, asBytes=True, scanOnly=False, annotate=addAnnotations, escape=True)
                    if findNonPrintable or findMeta or (not onlyShowNonAscii):
                        if showLineNumbers:
                            print(f"{np1}: ", end="")
                        print(expanded4)
                except Exception as e4:
                    # print(f"Exception4: {type(e4)}, {e4}<br/>")
                    print(f"<span class='err'>", end="")
                    if showLineNumbers:
                        print(f"{np1}: ", end="")
                    print("Something went wrong while processing this line:<br/><span class='mo'>")
                    print(esc(hexdump(ln)).replace(" ", "&nbsp;"))
                    print("</span></span>")


def main():
    """ the executable """
    print("Content-Type: text/html")
    print()

    cgitb.enable() # display=0, logdir="/tmp/")

    testMode = False
    if "REQUEST_URI" in os.environ:
        request_uri = os.environ["REQUEST_URI"]
    else:
        request_uri = "unknown-script"
        testMode = True

    form = cgi.FieldStorage()
    # print(f"form.getvalue('use_inline_annotation={form.getvalue('use_inline_annotations')}")
    useInlineAnnotationsChecked = "checked='checked'" if form.getvalue('use_inline_annotations') is not None else ""
    # print(f"form.getvalue('only_show_nonasci={form.getvalue('only_show_nonascii')}")
    onlyShowNonAsciiChecked = "checked='checked'" if form.getvalue('only_show_nonascii') is not None else ""
    # print(f"form.getvalue('show_line_number={form.getvalue('show_line_numbers')}")
    showLineNumbersChecked = "checked='checked'" if form.getvalue('show_line_numbers') is not None else ""

    if not testMode:
        print(f"""<! DOCTYPE html>
        <head>
        <meta charset="UTF-8">
        <title>Scan for non-ASCII characters</title>
        </head>
        <style>
        /* tooltip information comes from https://www.w3schools.com/howto/howto_css_tooltip.asp */
        .uni {{
            background-color: lightgreen;
        }}
        .na {{
            background-color: lightsalmon;
        }}
        .ct {{
            background-color: pink;
        }}
        .err {{
            background-color: lightsalmon;
        }}
        .mo {{
            font-family: monospace;
        }}
        .tt {{
            position: relative;
            display: inline-block;
            /* border-bottom: 1px dotted black; */ /* If you want dots under the hoverable text */
        }}
        .an {{
            background-color: lightblue;
        }}

        /* Tooltip text */
        .ttt {{
              visibility: hidden;
              width: 120px;
              background-color: lightblue; /* #555; */
              color: black; /* #fff; */
              text-align: center;
              padding: 5px 0;
              border-radius: 6px;

              /* Position the tooltip text */
              position: absolute;
              z-index: 1;
              bottom: 125%;
              left: 50%;
              margin-left: -10px; /* -60px; */

              /* Fade in tooltip */
              opacity: 0;
              transition: opacity 0.3s;

        }}

        /* Tooltip arrow */
        .tt .ttt::after {{
          content: "";
          position: absolute;
          top: 100%;
          left: 10px; /* 50%; */
          margin-left: -5px;
          border-width: 5px;
          border-style: solid;
          border-color: lightblue transparent transparent transparent; /* #555 */
        }}

        /* Show the tooltip text when you mouse over the tooltip container */
        .tt:hover .ttt {{
            visibility: visible;
            opacity: 1;
        }}

        .sup {{ vertical-align: super; font-size: xx-small; }}
        .sub {{ vertical-align: align; font-size: xx-small; }}
        </style>
        <body>
        <h1>Scan for non-ASCII characters</h1>
        {__doc__}
        <br/><br/>
        <form action='{request_uri}' method='POST' enctype='multipart/form-data'>
        <label for='scanfile'>
        Select a file to upload:
        </label>
        <input type='file'/ id='scanfile' name='scanfile'>
        <br/>
        <label for='use_inline_annotations'>
        Show inline annotations about each non-ASCII/non-printable character?
        </label>
        <input type='checkbox' name='use_inline_annotations' id='use_inline_annotations' value='yes' {useInlineAnnotationsChecked}/>
        <br/>
        <label for='only_show_nonascii'>
        Only show lines with a non-ASCII/non-printable character?
        </label>
        <input type='checkbox' name='only_show_nonascii' id='only_show_nonascii' value='yes' {onlyShowNonAsciiChecked}/>
        <br/>
        <label for='show_line_numbers'>
        Show line numbers?
        </label>
        <input type='checkbox' name='show_line_numbers' id='show_line_numbers' value='yes' {showLineNumbersChecked}/>
        <br/>
        <input type='submit' value='Scan File'/>
        </form>
        Key:
        <ul>
        <li><span class='ct'>control character</span></li>
        <li><span class='uni'>Unicode character</span></li>
        <li><span class='na'>non-ASCII/non-Unicode character</span></li>
        </ul>
    """.replace("        ",""))

    print("<hr/>")

    if testMode:
        print(hexdump(b"abcdef\nghij"))
        print(hexdump(b"abc\xe2\x80\x9cdef\nghij\xf5klmn\nopqr"))
        print(hexdump(b"abcdef\ngh\"ijabc\xe2\x80\x9cdef\nghij\xf5klmn\nopqr"))

        process("testinput ascii", io.BytesIO(b"abcdef\nghij"), True, False, False)
        process("testinput ctrl", io.BytesIO(b"abc\05def\nghij"), True, False, False)
        process("testinput uni", io.BytesIO(b"abc\xe2\x80\x9cdef\nghij"), True, False, False)
        process("testinput non", io.BytesIO(b"abc\xf5def\nghij"), True, False, False)
        process("testinput non+uni", io.BytesIO(b"abc\xe2\x80\x9cdef\nghij\xf5klmn\nopqr"), True, False, False)

        process("all,nums non+uni", io.BytesIO(b"abc\xe2\x80\x9cdef\nghij\xf5klmn\nopqr"), True, False, True)
        process("limit non+uni", io.BytesIO(b"abc\xe2\x80\x9cdef\nghij\xf5klmn\nopqr"), True, True, False)
        process("limit,nums non+uni", io.BytesIO(b"abc\xe2\x80\x9cdef\nghij\xf5klmn\nopqr"), True, True, True)

    elif "scanfile" in form:
        fileitem = form["scanfile"]
        if fileitem.file:
            process(fileitem.filename, fileitem.file,
                    form.getvalue('use_inline_annotations'),
                    form.getvalue('only_show_nonascii'),
                    form.getvalue('show_line_numbers'))

    print("<hr/>")

    # cgi.test()

    print("</body>")

if __name__ == '__main__':
    main()
