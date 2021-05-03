#!/usr/bin/env python3

"""
    A set of functions that make it easy to create a bibxml xml and related files.
"""
#    Author: Tony Hansen

import datetime
import glob
import io
import os
import stat
import sys
import tempfile
import requests

months = [ "", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

monthnames = {
    1: "January", "Jan": "January", "January": "January",
    2: "February", "Feb": "February", "February": "February",
    3: "March", "Mar": "March", "March": "March",
    4: "April", "Apr": "April", "April": "April",
    5: "May", "May": "May",
    6: "June", "Jun": "June", "June": "June",
    7: "July", "Jul": "July", "July": "July",
    8: "August", "Aug": "August", "August": "August",
    9: "September", "Sep": "September", "Sept": "September", "September": "September",
    10: "October", "Oct": "October", "October": "October",
    11: "November", "Nov": "November", "November": "November",
    12: "December", "Dec": "December", "December": "December",
    }

revmonths = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12"
    }

revmonths0 = {
    "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
    "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12",
    1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06",
    7: "07", 8: "08", 9: "09", 10: "10", 11: "11", 12: "12"
    }


def escape(xstr):
    """ escape the &,<,>,",' characters within the string xstr with appropriate XML entities """
    return xstr.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"', "&quot;")


def escape_no_squote(xstr):
    """ escape the &,<,>," characters within the string xstr with appropriate XML entities. (No apos.) """
    return xstr.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def escape_no_quotes(xstr):
    """ escape the &,<,> characters within the string xstr with appropriate XML entities. (No apos or quot.) """
    return xstr.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gen_empty_ref_xml(typ):
    """ generate an empty ref dictionary to be used by gen_xml() """
    return {
        "date": { "year": "", "month": "", "day": "", "full": "" },
        "authors": [],
        "title": "",
        "rdftitle": "",
        "type": typ,
        "anchor": "",
        "abstract": "",
        "series_info": [ ],
        "format": [ ],
        "target": ""
        }


def gen_xml(ref, *, gen_empty_author=False):
    """ given a ref dictionary, create and print the xml for the RFC/I-D """

    xml = "<?xml version='1.0' encoding='UTF-8'?>\n\n"

    target = ref.get("target")
    target2 = ref.get("target2")
    xml += f"<reference anchor='{ref['anchor']}'"
    if target:
        xml += f" target='{target}'"
    if target2:
        xml += f" target2='{target2}'"
    xml += ">\n"

    xml += "<front>\n"
    xml += f"<title>{escape_no_squote(ref['title'])}</title>\n"

    for author in ref["authors"]:
        if author.get("role", "") != "":
            xml += f"<author initials='{escape(author['initials'])}' surname='{escape(author['surname'])}' fullname='{escape(author['fullname'])}' role='{escape(author['role'])}'>\n"
        elif author.get('initials', "") != '' or author.get('surname', "") != '' or author.get('fullname', "") != '' or gen_empty_author:
            xml += f"<author initials='{escape(author.get('initials',''))}' surname='{escape(author.get('surname',''))}' fullname='{escape(author.get('fullname',''))}'>\n"
        else:
            xml += "<author>\n"
        if author['org'] != "":
            xml += f"<organization>{escape_no_squote(author['org'])}</organization>\n"
        else:
            xml += "<organization />\n"
        xml += "</author>\n"

    date = ref["date"]
    year = date["year"]
    month = date.get("month")
    day = date.get("day")
    if year and month and day:
        xml += f"<date year='{year}' month='{month}' day='{day}' />\n"
    elif year and month:
        xml += f"<date year='{year}' month='{month}' />\n"
    elif year:
        xml += f"<date year='{year}' />\n"

    abstract = ref['abstract']
    while abstract.endswith("\n"):
        abstract = abstract[:-1]
    abstract = escape_no_squote(abstract).replace("\n\n", "</t><t>")
    if abstract != "":
        abstract = "<t>" + abstract + "</t>"

    if abstract != "":
        xml += f"<abstract>{abstract}</abstract>\n"
    xml += "</front>\n"

    for si in ref["series_info"]:
        xml += f"<seriesInfo name='{escape(si['name'])}' value='{escape(si['value'])}'/>\n"
    for fmt in ref["format"]:
        xml += f"<format type='{escape(fmt['type'])}' target='{escape(fmt['target'])}'/>\n"

    xml += "</reference>\n"
    return xml


def gen_rdf(ref):
    """ given a ref dictionary, create and print the rdf for the RFC/I-D """
    abstract = ref['abstract']
    while abstract.endswith("\n"):
        abstract = abstract[:-1]
    abstract = escape_no_quotes(abstract).replace("\n\n", " ")
    # print(f"ref[date]={ref['date']}")
    if not ref['date'].get('year'):
        prdate = ""
    else:
        if not ref['date'].get('month'):
            ref['date']['month'] = 1
        if not ref['date'].get('day'):
            ref['date']['day'] = 1
        prdate = f"{ref['date']['year']}-{revmonths0[ref['date']['month']]}-{int(ref['date']['day']):02d}T23:00:00-00:00"

    rdf = "\n".join([
            f"    <item rdf:about='{ref['url']}'>",
            f"        <link>{ref['url']}</link>",
            f"        <title>{escape_no_quotes(ref['rdftitle'])}</title>",
            f"        <dc:date>{prdate}</dc:date>",
            f"        <description>{abstract}</description>",
            "    </item>",
            ""
            ])
    return rdf


# pylint: disable=R0913
def verbose_print(args, val, msg, *, file=sys.stdout, end=None):
    """
    Print the message if args.verbose > val
    """
    if args.verbose > val:
        print(msg, file=file, end=end)

def checkfile(args, fname, newcontent, *, create_dirs=False, backup_fname=None, write_message=True):
    """
    Check to see if a file exists and contains "newcontent".
    If not, (re)create the file.
    """
    writefile = None

    if create_dirs:
        os.makedirs(os.path.dirname(fname), exist_ok=True)

    if not os.path.isfile(fname):
        verbose_print(args, 1, f"{fname} does not exist")
        writefile = "NEW"

    else:
        content = ""
        with open(fname, 'r') as fp:
            content = fp.read()
        if content == newcontent:
            verbose_print(args, 1, f"{fname} same contents")

        else:
            verbose_print(args, 1, f"{fname} contents differ")
            writefile = "UPD"
            # print(f"contents=\n{content}\n")
            # print(f"newcontents=\n{newcontent}\n")
            if backup_fname:
                checkfile(args, backup_fname, content, create_dirs=True, write_message=False)

    if writefile:
        if write_message:
            verbose_print(args, 0, f"{writefile} {fname}")
        if args.test:
            print(f"test mode: skipping writing to {fname}")
        else:
            with open(fname, 'w') as fp:
                print(newcontent, end="", file=fp)
    return writefile


def gen_index_rdf(rxdict):
    """ generate an index.xml file, based on a list of entries in the rxdict dict, sorted by the rxdict keys """
    now = datetime.datetime.now()
    index_rdf = "\n".join([
            "<?xml version='1.0' encoding='UTF-8'?>",
            "",
            "<rdf:RDF ",
            "  xmlns='http://purl.org/rss/1.0/'",
            "  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'",
            "  xmlns:dc='http://purl.org/dc/elements/1.1/'>",
            "",
            "    <channel rdf:about='http://xml.resource.org/public/rfc/bibxml/index.rdf'>",
            "        <title>Recent RFCs</title>",
            "        <link>http://xml.resource.org/public/rfc/bibxml/index.rdf</link>",
            "        <description>Automatically generated from rfc-index.xml</description>",
            "        <dc:language>en-us</dc:language>",
            f"        <dc:date>{now.year}-{now.month:02d}-{now.day:02d}T{now.hour:02d}:{now.minute:02d}:{now.second:02d}-00:00</dc:date>",
            "",
            "        <items><rdf:Seq>",
            ""
            ])

    for k in sorted(rxdict.keys()):
        if rxdict[k]:
            index_rdf += rxdict[k]
        else:
            print(f"rxdict[{k}] is {rxdict[k]}")

    index_rdf += "\n".join([
            "        </rdf:Seq></items>",
            "    </channel>",
            "</rdf:RDF>",
            ""
            ])

    return index_rdf


def get_file_contents(fname):
    """ return the contents of a file, None if it cannot be read """
    try:
        with open(fname) as fp:
            return fp.read()
    except Exception as e:
        print(f"Cannot read {fname}: {e}")
        return None


def gen_index_rdf_scan(ref_file, rdf_dir, rdf_prefix):
    """
    Scan the files in rdf_dir for files that
    1) have a name starting with rdf_prefix, and
    2) are newer than ref_file.

    Return a dictionary, indexed by the filenames, with the contents of those files.
    """
    ret = { }
    stat_ref_mtime = 0
    if ref_file is not None:
        try:
            stat_ref_mtime = os.stat(ref_file).st_mtime
        except Exception as e:
            pass

    preflen = len(f"{rdf_dir}/{rdf_prefix}")
    for fname in glob.glob(f"{rdf_dir}/{rdf_prefix}*.rdf"):
        try:
            stat_file = os.stat(fname)
            if stat.S_ISREG(stat_file.st_mode) and stat_file.st_mtime > stat_ref_mtime:
                nm  = fname[preflen:]
                c = get_file_contents(fname)
                if c:
                    ret[nm] = c
        except Exception as e:
            print(f"#4: Cannot stat {fname}: {e}")

    return ret


def gen_index_html(hxset):
    """ generate an index.html file, based on a list of entries in the set hxset """
    with io.StringIO() as outfp:
        for k in sorted(hxset):
            outfp.write(f"<a href='{escape(k)}'>{escape_no_quotes(k)}</a><br/>\n")
        return outfp.getvalue()
    return ""


def gen_index_html_set(html_dir, html_prefix):
    """
    Scan the files in html_dir for files that have a name starting with html_prefix.
    Return a set of the basename(filenames).
    """
    ret = set()
    preflen = len(f"{html_dir}/") -1
    for fname in glob.glob(f"{html_dir}/{html_prefix}*.xml"):
        nm  = fname[preflen:]
        ret.add(nm)

    return ret


def gen_index_xml(ixdict):
    """
    Generate an index.xml file. ixdict is a dictionary indexed by filenames and the contents of those files.
    """
    now = datetime.datetime.now()
    month = months[now.month]
    index_xml = "\n".join(["<?xml version='1.0' encoding='UTF-8'?>",
                         "<!DOCTYPE rfc SYSTEM 'rfc2629.dtd'>",
                         "",
                         "<?rfc private=' '?>",
                         "<?rfc symrefs='yes'?>",
                         "<?rfc topblock='no'?>",
                         "",
                         "<rfc>",
                         "<front>",
                         f"<title abbrev='The (unofficial) RFC Index'>The (unofficial) RFC Index (as of {month} {now.day}, {now.year})</title>",
                         "",
                         f"<date month='{month}' day='{now.day}' year='{now.year}' />",
                         "</front>",
                         "",
                         "<middle />",
                         "",
                         "<back>",
                         "<references title='rfc-index'>",
                         "",
                          ])

    for k in sorted(ixdict.keys()):
        index_xml += ixdict[k]

    index_xml += "\n".join([
            "</references>",
            "</back>",
            "</rfc>",
            "",
            ])

    return index_xml


def get_url_tempfile(url, *, exit_ok=False):
    """
    Send HTTP GET request to server and attempt to receive a response.
    Write to and return a temporary file. Optionally exit on error.
    """
    response = requests.get(url)
    # pylint: disable=R1732
    # R1732=Consider using 'with' for resource-allocating operations
    # Can't do that here because we're returning the value.
    local_file = tempfile.TemporaryFile()

    # If the HTTP GET request can be served
    if response.status_code == 200:
        # Write the file contents in the response to a file specified by local_file.path
        for chunk in response.iter_content(chunk_size=128):
            local_file.write(chunk)
        local_file.flush()
        local_file.seek(0)
        return local_file

    if exit_ok:
        sys.exit(f"Cannot retrieve {url}. Status_code={response.status_code}")

    return None


def get_url_to_file(url, fname, *, exit_ok=False):
    """
    Send HTTP GET request to server and attempt to receive a response.
    Write to the specified file. Return the status code. Optionally exit on error.
    """
    # Send HTTP GET request to server and attempt to receive a response
    response = requests.get(url)

    # If the HTTP GET request can be served
    if response.status_code == 200:
        # Write the file contents in the response to a file specified by local_file_path
        with open(fname, 'wb') as local_file:
            for chunk in response.iter_content(chunk_size=128):
                local_file.write(chunk)
        return response.status_code

    if exit_ok:
        sys.exit(f"Cannot retrieve {url}. Status_code={response.status_code}")
    return response.status_code


def get_xml_text(root, path):
    """
    Extract the text for the element at the given path.
    """
    for item in root.findall(path):
        return item.text.strip()
    return None


def get_xml_text_by_attribute(root, path, attribute, secondary_path):
    """
    For some reason an xpath './volume/article/articleinfo/date[datetype="OriginalPub"]/year'
    doesn't seem to be working. So get all
    """
    ret = {}
    for date in root.findall(path):
        k = date.attrib.get(attribute)
        v = get_xml_text(date, secondary_path)
        if k:
            ret[k] = v
    return ret


def get_xml_first_of(dsrch, knames):
    """
    Loop over the keys in knames, returning the first one in dsrch found.
    None if none present.
    """
    for k in knames:
        v = dsrch.get(k)
        if k:
            return v
    return None


def dump_xml(elroot, prefix, *, include_children=False):
    """ print info on an xml element """
    print(f"{prefix}elroot={elroot}")
    print(f"{prefix}elroot.tag={elroot.tag}")
    print(f"{prefix}dir(elroot)={dir(elroot)}")
    print(f"{prefix}elroot.attrib={elroot.attrib}")
    print(f"{prefix}elroot.getchildren()={list(elroot)}")
    if include_children:
        for ch in elroot:
            dump_xml(ch, f"    {prefix}")


def clean_dir(args, glob_pattern, file_dict):
    """
    Loop over a set of globbed filenames.
    Any that is not in the list gets removed.
    """
    for f in glob.iglob(glob_pattern):
        if file_dict.get(f):
            verbose_print(args, 1, f"found {f}", file=sys.stderr)
        else:
            if args.skip_clean:
                print(f"skipping REMOVING {f}", file=sys.stderr)
            else:
                print(f"REMOVING {f}", file=sys.stderr)
                os.unlink(f)


def generate_final_index_html_and_rdf(args):
    """
    Generate the index.html and index.rdf files based on what
    is found in the reference...xml and rdf/item...rdf files.
    """
    if args.bibxml_dir:
        # generate index.html file
        hx = gen_index_html_set(args.bibxml_dir, "reference.")
        index_html = gen_index_html(hx)
        checkfile(args, f"{args.bibxml_dir}/index.html", index_html)

        # generate index.rdf file
        rx = gen_index_rdf_scan(f"{args.bibxml_dir}/index.rdf", f"{args.bibxml_dir}/rdf", "item.")
        index_rdf = gen_index_rdf(rx)
        checkfile(args, f"{args.bibxml_dir}/index.rdf", index_rdf)


def create_bibxml_directories(args):
    """
    Create the needed directories under bibxml_dir.
    """
    if args.bibxml_dir:
        os.makedirs(args.bibxml_dir, exist_ok=True)
        os.makedirs(args.bibxml_dir + "/rdf", exist_ok=True)


def usage(parser, msg=None):
    """
    Print an appropriate usage message.
    """
    if msg:
        print(msg, file=sys.stderr)
    parser.print_help(sys.stderr)
    sys.exit(1)


def empty_run_unit_tests(args):
    """
    Print a message about there being no unit tests and exit.
    THIS FUNCTION SHOULD EVENTUALLY GO AWAY.
    """
    verbose_print(args, 0, "Testing ????()")

    print(f"NO TESTS DEFINED YET FOR {sys.argv[0]}")

    print("All tests passed")
    sys.exit()


def run_unit_tests(args):
    """
    Run some unit tests on some of the code modules.
    """
    verbose_print(args, 0, "Testing escape()")
    assert escape("ab&sup;<'\"def") == "ab&amp;sup;&lt;&apos;&quot;def"
    verbose_print(args, 0, "Testing escape_no_squote()")
    assert escape_no_squote("ab&sup;<'\"def") == "ab&amp;sup;&lt;'&quot;def"
    verbose_print(args, 0, "Testing escape_no_quotes()")
    assert escape_no_quotes("ab&sup;<'\"def") == "ab&amp;sup;&lt;'\"def"
    verbose_print(args, 0, "Testing gen_empty_ref_xml()")
    empty_ref = gen_empty_ref_xml("abc")
    assert empty_ref == {
        'date': {'year': '', 'month': '', 'day': '', 'full': ''},
        'authors': [], 'title': '', 'rdftitle': '', 'type': 'abc',
        'anchor': '', 'abstract': '', 'series_info': [], 'format': [], 'target': ''
        }
    verbose_print(args, 0, "Testing gen_xml()")
    empty_ref["title"] = "this is a title"
    empty_ref["target"] = "this is a target"
    empty_ref["url"] = "this is a url"
    empty_ref["date"]["year"] = 2021
    empty_ref["authors"].append({ "initials": "V.A.", "surname": "Cant", "org": "" })
    assert gen_xml(empty_ref) == """<?xml version='1.0' encoding='UTF-8'?>

<reference anchor='' target='this is a target'>
<front>
<title>this is a title</title>
<author initials='V.A.' surname='Cant' fullname=''>
<organization />
</author>
<date year='2021' />
</front>
</reference>
"""
    verbose_print(args, 0, "Testing gen_rdf()")
    assert gen_rdf(empty_ref) == """    <item rdf:about='this is a url'>
        <link>this is a url</link>
        <title></title>
        <dc:date>2021-01-01T23:00:00-00:00</dc:date>
        <description></description>
    </item>
"""

    # def checkfile(args, fname, newcontent, create_dirs=False, backup_fname=None): - filesystem
    # def gen_index_rdf(rxdict): - possible
    # def get_file_contents(fname): - filesystem
    # def gen_index_rdf_scan(ref_file, rdf_dir, rdf_prefix): - filesystem
    # def gen_index_html(hxset): - possible
    # def gen_index_html_set(html_dir, html_prefix): - possible
    # def gen_index_xml(ixdict): - possible
    # def get_url_tempfile(url, exit_ok=False): - filesystem
    # def get_xml_text(root, path): - possible, xml
    # def get_xml_text_by_attribute(root, path, attribute, secondary_path): - possible, xml
    # def get_xml_first_of(dsrch, knames): - possible, xml
    # def dump_xml(elroot, prefix, include_children=False): - filesystem
    # def clean_dir(args, glob_pattern, file_dict): - filesystem

    print("All tests passed")
    sys.exit()


def main():
    """ Do unit tests on the common functions. """
    # pylint: disable=c0415
    # c0414=Import outside toplevel -- we only need argparse for running unit tests.
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-T", "--unit-tests", help="Run unit tests", action="store_true", required=True)
    parser.add_argument("-v", "--verbose", help="Run unit tests", action="store_true")
    args = parser.parse_args()

    if args.unit_tests:
        run_unit_tests(args)


if __name__ == "__main__":
    main()
