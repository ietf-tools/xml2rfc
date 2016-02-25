#!/usr/bin/env python3

# Thu, 24 Sep 15 (NZST)
# Sat,  7 Jun 14 (NZST)
#
# check-svg.py:  ./check-svg.py -n [-o dir] diagram.svg
#                ./check-svy.py --help  # to see options info
#
# Nevil Brownlee, U Auckland
# From a simple original version by Joe Hildebrand
# Updates from Tony Hansen for ietf web backend use

# TODO 
# warn goes to stderr ?
# trace goes to stderr ?
# add quite option? or reuse -v option for verbose and extra verbose
# output filename option ?
# append newline to new_fn


#'''  # ElementTree doesn't have nsmap
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
#'''
#from lxml import etree as ET

import getopt
import sys
import re

import word_properties as wp

indent = 4
warn_nbr = 0
current_file = None

verbose = False   # set by -v
warn_limit = 40   # set by -w nnn
new_file = False  # set by -n
output_dir = None # set by -O
trace = False     # set by -t

bad_namespaces = []

def help_msg(msg):
    suffix = ''
    if msg:
        suffix = ": %s" % msg
    print( "Nevil's SVG checker%s" % suffix )
    print( "\n  ./check-svg.py [options] input-svg-file(s)\n" )
    print( "options:" )
    print( "  -n/--writenew       write .new.svg file, stripping out anything\n" +
           "                      not allowed in SVG 1.2 RFC" )
    print( "  -O dir/--odir=dir   write files to dir (may be combined with -n)" )
    print( "  -w nn/--warnmax=nn  stop after nn warning messages\n" )
    exit()

def main():
    try:
        options, rem_args = getopt.getopt(sys.argv[1:], "hntvO:w:",
                                          ["warnmax=",
                                           "verbose", "help", "trace",
                                           "writenew", "odir="])
    except getopt.GetoptError:
        help_msg("Unknown option")
    
    filter = None
    for o,v in options:
        if o in ("-n", "--writenew"):
            global new_file
            new_file = True
        elif o in ("-O", "--odir"):
            global output_dir
            output_dir = v
        elif o in ("-w", "--warnmax"):
            global warn_limit
            warn_limit = int(v)
        elif o in ("-v", "--verbose"):
            global verbose
            verbose = True
        elif o in ("-t", "--trace"):
            global trace
            trace = True
        elif o in ("-h", "--help"):
            help_msg(None)
            
    if len(rem_args) == 0:
        help_msg("No input file(s) specified!")

    for arg in rem_args:
        warn_nbr = 0
        checkFile(arg)
        print( "%d warnings for %s\n" % (warn_nbr, arg) )

def warn(msg, depth):
    global indent, warn_nbr, warn_limit, current_file
    warn_nbr += 1
    print( "%5d %s%s" % (warn_nbr, ' '*(depth*indent), msg) )
    if warn_nbr == warn_limit:
        print( "warning limit (%d) reached for %s" % ( 
            warn_nbr, current_file) )

def check_some_props(attr, val, depth):  # For [style] properties
    vals = wp.properties[attr]
    props_to_check = wp.property_lists[vals]
    new_val = '';  ok = True
    old_props = val.rstrip(';').split(';')
    #print( "old_props = %s" % old_props )
    for prop in old_props:
        #print( "prop = %s" %  prop )
        p, v = prop.split(':')
        v = v.strip()  # May have leading blank
        if p in props_to_check:
            allowed_vals = wp.properties[p]
            #print( "$$$ p=%s, allowed_vals=%s." % (p, allowed_vals) )
            allowed = value_ok(v, p)
            if not allowed:
                warn("??? %s attribute: value '%s' not valid for '%s'" % (
                    attr,v, p), depth)
                ok = False
        else:
            new_val += ';' + prop
    return (ok, new_val)

def value_ok(v, obj):  # Is v OK for attrib/property obj?
    # print( "value_ok(%s, %s)" % (v, obj) )
    if obj not in wp.properties:
        if obj not in wp.basic_types:
            return (False, None)
        values = wp.basic_types[obj]
        if values == '+':  # Integer
            n = re.match(r'\d+$', v)
            return (n, None)
    else:
        values = wp.properties[obj]
    # if isinstance(values, basestring):
    if isinstance(values, str):
        if values[0] == '<' or values[0] == '+':
            print( ". . . values = >%s<" % values )
            return value_ok(False, None)
    else:
        ## print( "--- values=", ;  print values )
        for val in values:
            #print( "- - - val=%s, v=%s." % (val, v) )
            if val[0] == '<':
              return value_ok(v, val)
            if v == val:
                return (True, None)
            elif val == '#':  # RGB value
                lv = v.lower()
                if lv[0] == '#':  #rrggbb  hex
                    if len(lv) == 7:
                        return (lv[3:5] == lv[1:3] and lv[5:7] == lv[1:3], None)
                    if len(lv) == 4:
                        return (lv[2] == lv[1] and lv[3] == lv[1], None)
                    return (False, None)
                elif lv.find('rgb') == 0:  # integers
                    rgb = re.search(r'\((\d+),(\d+),(\d+)\)', lv)
                    if rgb:
                        return ((rgb.group(2) == rgb.group(1) and
                            rgb.group(3) == rgb.group(1)), None)
                    return (False, None)
        v = v.lower()
        if obj == 'font-family':
            if v.find('sans') >= 0:
                return (False, 'sans-serif')
        if obj == '<color>':
            return (False, wp.color_default)
        return (False, None)

def strip_prefix(element):  # Remove {namespace} prefix
    global bad_namespaces
    ns_ok = True
    if element[0] == '{':
        rbp = element.rfind('}')  # Index of rightmost }
        if rbp >= 0:
            ns = element[1:rbp]
            if not ns in wp.xmlns_urls:
                if not ns in bad_namespaces:
                    bad_namespaces.append(ns)
                ns_ok = False
            element = element[rbp+1:]
    return element, ns_ok  # return ns = False if it's not allowed

def check(el, depth):
    global new_file, trace, output_dir
    #print( "tag=%s<  text=%s<" % (el.tag, el.text) )
    #print( "tail=%s<  attrib=%s<" % (el.tail,el.attrib) )
    if trace:
        print( "%s tag = %s" % (' ' * (depth*indent), el.tag) )
    if warn_nbr >= warn_limit:
        return
    element, ns_ok = strip_prefix(el.tag)  # name of element
    #print( "element=%s, ns=%s" % (element, ns) )
        # ElementTree prefixes elements with default namespace in braces
    if not ns_ok:
        return False  # Remove this el
    if verbose:
        print( "%s element % s: %s" % (' ' * (depth*indent), element, el.attrib) )
    if element not in wp.elements:
        warn("... element '%s' not allowed" % element, depth )
        return False  # Remove this el
    else:
        attribs = wp.elements[element]  # Allowed attributes for element
        for attrib, val in el.attrib.items():
            attr, ns_ok = strip_prefix(attrib)
            if trace:
                print( "%s attr %s = %s (ns_ok = %s)" % (
                    ' ' * (depth*indent), attr, val, ns_ok) )
            if not ns_ok or ((attr not in attribs) and (attr not in wp.properties)):
                warn("--- element '%s' does not allow attribute '%s'" % (
                    element, attrib), depth)
                del el.attrib[attrib]  # remove this attribute
            elif (attr not in attribs):  # Not in elements{}, can't test value
                vals = wp.properties[attr]
                ## print( "vals = ", ); print( vals, ) ; print( "<<<<<" )
                if vals and vals[0] == '[':
                    ok, new_val = check_some_props(attr, val, depth)
                    if (new_file or output_dir) and not ok:
                        el.attrib[attr] = new_val[1:]
                else:
                    ok, new_val = value_ok(val, attr)
                    if vals and not ok:
                        warn("=== %s not allowed as value for %s" % (val, attr),
                             depth)
                        if new_file or output_dir:
                            if new_val != None:
                                el.attrib[attrib] = new_val
                            else:
                                del el.attrib[attrib]  # remove this attribute
    els_to_rm = []  # Can't remove them inside the iteration!
    for child in el:
        if trace:
            print( "%schild, tag = %s" % (' ' * (depth*indent), child.tag) )
        if not check(child, depth+1):
            els_to_rm.append(child)
    if (new_file or output_dir) and len(els_to_rm) != 0:
        for child in els_to_rm:
            el.remove(child)
    return True  # OK

def remove_namespace(doc, namespace):
    # From  http://stackoverflow.com/questions/18159221/
    #   remove-namespace-and-prefix-from-xml-in-python-using-lxml
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            print( "elem.tag before=%s," % elem.tag )
            elem.tag = elem.tag[nsl:]
            print( "after=%s." % elem.tag )

def checkFile(fn):
    global current_file, warn_nbr, root
    current_file = fn
    print( "Starting %s" % current_file )
    tree = ET.parse(fn)
    root = tree.getroot()
    #print( "root.attrib=%s, test -> %d" % (root.attrib, "xmlns" in root.attrib) )
    #    # attrib list doesn't have includes "xmlns", even though it's there
    #print( "root.tag=%s" % root.tag )
    no_ns = root.tag.find("{") < 0
    #print( "no_ns = %s" % no_ns )

    ET.register_namespace("", "http://www.w3.org/2000/svg")
        # Stops tree.write() from prefixing above with "ns0"
    check(root, 0)
    print( "bad_namespaces = %s" % bad_namespaces )
    if trace and len(bad_namespaces) != 0:
        print( "bad_namespaces = %s" % bad_namespaces )
    if new_file or output_dir:
        new_fn = None
        if output_dir:
            p = re.compile("^.*/")
            if p.match(fn):
                new_fn = p.sub(output_dir + "/", fn)
            else:
                new_fn = output_dir + "/" + fn;
            fn = new_fn

        if new_file:
            sp = fn.rfind('.svg')
            if sp+3 != len(fn)-1:  # Indices of last chars
                print( "filename doesn't end in '.svg' (%d, %d)" % (sp, len(fn)) )
            else:
                new_fn = fn.replace(".svg", ".new.svg")

        if new_fn:
            print( "writing to %s" % (new_fn) )
            if no_ns:
                root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
            for ns in bad_namespaces:
                remove_namespace(root, ns)
            tree.write(new_fn)
            # append newline to new_fn
            with open(new_fn, "a") as myfile:
                myfile.write("\n")

if __name__ == "__main__":
    main()
