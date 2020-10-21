#!/usr/bin/env python3

"""
Retrieve a resource in bibxml format.
Use the cached version if it is <24 hours old.
Use the remote resource if it is available, and update cache.
If the remote resource is NOT available and a cached version is available, use it anyway.
Else return an error.

This program generated IANA references in bibxml format. It uses iana.org to do the heavy lifting.
e.g. http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.service-names-port-numbers.xml

http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.$iana.xml
http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.$iana.kramdown
"""

import sys
import os
import cgi
import subprocess
import re
import time
import requests

class reference_printer(object):
    """
    Deal with a reference and its cached file.
    """

    def __init__(self, arg0, cachedir, identifier, replacement_anchor):
        """
        Create a cacheable reference
        """
        self.arg0 = arg0
        self.cachedir = cachedir
        self.identifier = identifier
        self.replacement_anchor = self.munge_anchor(replacement_anchor)
        self.nph = arg0.endswith("/nph-index.cgi") or arg0 == "nph-index.cgi"

    def munge_anchor(self, anchor):
        """ Make sure that an anchor is "safe" by changing to uppercase and remove non-[A-Z0-9_-]. """
        if anchor:
            anchor = re.sub(r"[^-A-Z0-9_]]", "", anchor.upper())
        return anchor

    def set_reference_info(self, reference_number, reference_type, reference_filename):
        """ save the reference information """
        self.reference_number = reference_number
        self.reference_type = reference_type
        self.reference_filename = reference_filename

    def cache_file(self):
        """ return the name of the cached file """
        return f"{self.cachedir}/{self.reference_filename}"

    def check_isrecent(self, statinfo):
        """ check if the timestamp is <24 hours old """
        if statinfo:
            ret = time.time() - statinfo.st_mtime < 24 * 60 * 60
            return ret
        return None

    def print_not_found(self):
        """ print a message indicating that the reference was not found """
        if self.nph:
            print("HTTP/1.0 404 NOT FOUND")
        print("Content-type: text/plain")
        print("")
        print(f"invalid {self.identifier} or type")

    def print_text(self, txt):
        """ Print the reference text. """
        if self.nph:
            print("HTTP/1.0 200 OK")
        print(f"Content-type: text/{self.reference_type}; charset=UTF-8")
        print("")
        txt = self.replace_anchor(txt)
        print(txt, end="")

    def replace_anchor(self, txt):
        """ If there is a replacement anchor, update the embedded anchor within the text. """
        if self.replacement_anchor:
            if self.reference_type == 'xml':
                txt = re.sub(r"anchor='[^']*'", f"anchor='{self.replacement_anchor}", txt)
                txt = re.sub(r'anchor="[^"]*"', f"anchor='{self.replacement_anchor}'", txt)
            else:
                txt = re.sub(r'^  [^:]*:', f'  {self.replacement_anchor}:', txt)
        return txt

    def get_file_contents(self, fn):
        """ get the contents of a file """
        ret = None
        try:
            with open(fn, "r") as fd:
                ret = fd.read()
        except Exception as e:
            print(f"{self.arg0}: Cannot open {fn}: {e}", file=sys.stderr)

        return ret

    def update_cache(self, txt):
        """ update the cache file with the new text """
        print("updating cache", file=sys.stderr)
        cf = self.cache_file()
        try:
            with open(cf, "w") as fd:
                fd.write(txt)
        except Exception as e:
            print(f"{self.arg0}: Error writing to cache file {cf}: {e}", file=sys.stderr)

    def print_reference(self):
        """
        Check the cache for a recent file.
        Try regenerating if no recent file is present.
        If regeneration fails and an old file is present:
            return the file.
        If no file or regeneration fails:
            print NOT FOUND
        """
        if not self.extract_reference_info():
            return self.print_not_found()

        try:
            cf = self.cache_file()
            statinfo = os.stat(cf)
            isrecent = self.check_isrecent(statinfo)
            print(f"statinfo={statinfo}, isrecent={isrecent}", file=sys.stderr)
            txt = self.get_file_contents(cf)

        except FileNotFoundError:
            statinfo = None
            isrecent = None
            txt = None

        if statinfo and isrecent and txt:
            print("found a recent cache file", file=sys.stderr)
            self.print_text(txt)

        else:
            ntxt = self.generate_reference()
            if not ntxt and txt:
                print("could not regenerate -- using old text", file=sys.stderr)
                self.print_text(txt)
            elif ntxt:
                print("have new text", file=sys.stderr)
                self.update_cache(ntxt)
                self.print_text(ntxt)
            else:
                self.print_not_found()

class iana_reference_printer(reference_printer):
    """
    Deal with a IANA reference.
    Everything specific to a IANA lives here.
    """

    def __init__(self, arg0, reference, replacement_anchor):
        self.reference = reference
        super().__init__(arg0, "/var/cache/bibxml-iana", "IANA", replacement_anchor)

    def extract_reference_info(self):
        """
        From a reference, extract the pertinent info from it.

        In particular, extract
            self.reference_number
            self.reference_type
            self.reference_filename
        Other values may also be extracted.

        :return Return True if values could be extracted.
        """
        m = re.match(r'^/?reference.IANA[.]([^/]+)[.](xml|kramdown)$', self.reference)
        if m:
            reference_number = m.group(1)
            reference_type = m.group(2) # reference_type == "xml" or "kramdown"
            self.set_reference_info(reference_number, reference_type, f"reference.IANA_{reference_number}.{reference_type}")
            return True
        return False

    def generate_reference(self):
        """
        Generate the text for a reference, in this case by running doilit.
        """
        print(f'requests.get(f"http://www.iana.org/assignments/{self.reference_number}/"', file=sys.stderr)
        resp = requests.get(f"http://www.iana.org/assignments/{self.reference_number}/")
        if resp.status_code >= 400:
            print(f"{self.arg0}:\n{resp.content}", file=sys.stderr)
            return None
        
        m = re.search(r"<title>([^<]*)</title>", resp.content)
        if not m:
            print(f"{self.arg0}: NO TITLE:\n{resp.content}", file=sys.stderr)
            return None
        
        title = m.group(1)
        if re.search(r"page not found", resp.content, re.IGNORE_CASE):
            print(f"{self.arg0}: title=page not found\n{resp.content}", file=sys.stderr)
            return None

        return "\n".join([f"<reference anchor='{self.reference_number.upper()}'",
                          f" target='http://www.iana.org/assignments/{self.reference_number}'>\n",
                          "<front>\n",
                          f"<title>{title}</title>\n",
                          "<author><organization>IANA</organization></author>\n",
                          "<date/>\n",
                          "</front>\n",
                          "</reference>\n"])

def main():
    """
    Do all the processing of the references.
    """

    if os.environ.get("PATH_INFO"):
        ref = os.environ["PATH_INFO"]
    else:
        sys.exit("No PATH_INFO found")

    cgi_arguments = cgi.FieldStorage() # uses sys.argv[1:]
    cgi_anchor = None
    if "anchor" in cgi_arguments.keys():
        cgi_anchor = cgi_arguments["anchor"].value
    print(f"{sys.argv[0]}: cgi_anchor={cgi_anchor}", file=sys.stderr)
    print(f"{sys.argv[0]}: ref={ref}", file=sys.stderr)

    rp = doi_reference_printer(sys.argv[0], ref, cgi_anchor)
    rp.print_reference()

if __name__ == '__main__':
    main()
