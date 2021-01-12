#!/usr/bin/env python3

"""
Retrieve a resource in bibxml format.
Use the cached version if it is <24 hours old.
Use the remote resource if it is available, and update cache.
If the remote resource is NOT available and a cached version is available, use it anyway.
Else return an error.

This program retrieves DOI references. It uses the doilit program to do the heavy lifting.
     http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.$doi.xml
    http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.$doi.kramdown
as in:
    http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.10.1145/1355734.1355746.xml
"""

import sys
import os
import cgi
import subprocess
import re
import time

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

class doi_reference_printer(reference_printer):
    """
    Deal with a DOI reference.
    Everything specific to a DOI lives here.
    """

    def __init__(self, arg0, reference, replacement_anchor):
        self.reference = reference
        super().__init__(arg0, "/var/cache/bibxml-doi", "DOI", replacement_anchor)

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
        m = re.match(r'^/?reference.DOI[.](\d+[.][^/_]+)[/_]([^/]+)[.](xml|kramdown)$', self.reference)
        if m:
            self.doi_pt1 = m.group(1)
            self.doi_pt2 = m.group(2)
            reference_number = f"{self.doi_pt1}_{self.doi_pt2}"
            reference_type = m.group(3) # reference_type == "xml" or "kramdown"
            self.set_reference_info(reference_number, reference_type, f"reference.DOI_{reference_number}.{reference_type}")
            return True
        return False

    def generate_reference(self):
        """
        Generate the text for a reference, in this case by running doilit.
        """
        opt = 'x' if self.reference_type == 'xml' else 'h'

        out, err = subprocess.Popen(["doilit", f"-{opt}=DOI_{self.reference_number}", f"{self.doi_pt1}/{self.doi_pt2}"], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
        if err:
            print(f"{self.arg0}:\n{err}", file=sys.stderr)
        return out.decode()

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
