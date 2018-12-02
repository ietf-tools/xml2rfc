#!/usr/bin/env python

from __future__ import print_function

import sys
import os

# If this script is renamed to 'xml2rfc.py' on a Windows system, the import
# of the realy xml2rfc module will break.  In order to handle this, we remove
# the directory of the script file from the python system path:
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

import datetime
import json
import lxml.etree
import optparse
import os
import xml2rfc

try:
    import debug
    assert debug
except ImportError:
    pass



def display_version(self, opt, value, parser):
    print('%s %s' % (xml2rfc.NAME, xml2rfc.__version__))
    debug.dir('parser')
    sys.exit()


def clear_cache(self, opt, value, parser):
    xml2rfc.parser.XmlRfcParser('').delete_cache()
    sys.exit()


def print_pi_help(self, opt, value, parser):
    pis = xml2rfc.parser.XmlRfc(None, None).pis.items()
    pis.sort()
    print("Available processing instructions (PIs), with defaults:\n")
    for k, v in pis:
        if isinstance(v, type('')):
            print('    %-20s  "%s"' % (k,v))
        else:
            print('    %-20s  %s' % (k,v))
    sys.exit()

def extract_anchor_info(xml):
    info = {
        'version': 1,
        'sections': {},
        }
    for item in xml.xpath('./middle//section'):
        anchor = item.get('anchor')
        label  = item.get('pn')
        if anchor and label and not anchor.startswith('anchor-'):
            info['sections'][anchor] = label.replace('section-','')
    return info

def main():
    # Populate options
    formatter = optparse.IndentedHelpFormatter(max_help_position=40)
    optionparser = optparse.OptionParser(usage='xml2rfc SOURCE [OPTIONS] '
                                        '...\nExample: xml2rfc '
                                        'draft.xml -o Draft-1.0 --text --html',
                                        formatter=formatter)

    formatgroup = optparse.OptionGroup(optionparser, 'Formats',
                                       'Any or all of the following '
                                       'output formats may be specified. '
                                       'The default is --text. '
                                       'The destination filename will be based '
                                       'on the input filename, unless an '
                                       'argument is given to --basename.')
    formatgroup.add_option('', '--text', action='store_true',
                           help='outputs to a text file with proper page breaks')
    formatgroup.add_option('', '--html', action='store_true',
                           help='outputs to an html file')
    formatgroup.add_option('', '--nroff', action='store_true',
                           help='outputs to an nroff file')
    formatgroup.add_option('', '--raw', action='store_true',
                           help='outputs to a text file, unpaginated')
    formatgroup.add_option('', '--expand', action='store_true',
                           help='outputs to an XML file with all references expanded')
    formatgroup.add_option('', '--v2v3', action='store_true',
                           help='convert vocabulary version 2 XML to version 3')
    formatgroup.add_option('', '--preptool', action='store_true',
                           help='run preptool on the input')
    formatgroup.add_option('', '--info', action='store_true',
                           help='generate a JSON file with anchor to section lookup information')
    optionparser.add_option_group(formatgroup)


    plain_options = optparse.OptionGroup(optionparser, 'Plain Options')
    plain_options.add_option('-C', '--clear-cache', action='callback', callback=clear_cache,
                            help='purge the cache and exit')
    plain_options.add_option('-H', '--pi-help', action='callback', callback=print_pi_help,
                            help='show the names and default values of PIs')
    plain_options.add_option(      '--debug', action='store_true',
                            help='Show debugging output')
    plain_options.add_option('-n', '--no-dtd', action='store_true',
                            help='disable DTD validation step')
    plain_options.add_option('-N', '--no-network', action='store_true', default=False,
                            help='don\'t use the network to resolve references')
    plain_options.add_option('-q', '--quiet', action='store_true',
                            help='dont print anything')
    plain_options.add_option('-u', '--utf8', action='store_true',
                            help='generate utf8 output')
    plain_options.add_option('-v', '--verbose', action='store_true',
                            help='print extra information')
    plain_options.add_option('-V', '--version', action='store_true', 
                            help='display the version number and exit')
    plain_options.add_option('-r', '--remove-pis', action='store_true', default=False,
                            help='Remove XML processing instructions')
    optionparser.add_option_group(plain_options)


    value_options = optparse.OptionGroup(optionparser, 'Other Options')
    value_options.add_option('-b', '--basename', dest='basename', metavar='NAME',
                            help='specify the base name for output files')
    value_options.add_option('-c', '--cache', dest='cache',
                            help='specify a primary cache directory to write to; default: try [ %s ]'%', '.join(xml2rfc.CACHES) )
    value_options.add_option('-d', '--dtd', dest='dtd', help='specify an alternate dtd file')
    value_options.add_option('-D', '--date', dest='datestring', metavar='DATE',
                            default=datetime.datetime.today().strftime("%Y-%m-%d"),
                            help='run as if the date is DATE (format: yyyy-mm-dd)')
    value_options.add_option('-f', '--filename', dest='filename', metavar='FILE',
                            help='Deprecated.  The same as -o.')
    value_options.add_option('-i', '--indent', type=int, default=2, 
                            help='With some v3 formatters: Indentation to use when pretty-printing XML')
    value_options.add_option('-o', '--out', dest='output_filename', metavar='FILE',
                            help='specify an explicit output filename')
    value_options.add_option('-p', '--path', dest='output_path', metavar='PATH',
                            help='specify the directory path for output files')
    optionparser.add_option_group(value_options)


    formatoptions = optparse.OptionGroup(optionparser, 'Format Options')
    formatoptions.add_option('--v3', dest='legacy', action='store_false',
                           help='with --text and --html: use the v3 formatter, rather than the legacy one.')
    formatoptions.add_option('--legacy', default=True, action='store_true',
                           help='with --text and --html: use the legacy text formatter, rather than the v3 one.')
    optionparser.add_option_group(formatoptions)

    textoptions = optparse.OptionGroup(optionparser, 'Text Format Options')
    textoptions.add_option('--no-headers', dest='omit_headers', action='store_true',
                           help='calculate page breaks, and emit form feeds and page top'
                           ' spacing, but omit headers and footers from the paginated format')
    textoptions.add_option('--legacy-list-symbols', default=False, action='store_true',
                           help='use the legacy list bullet symbols, rather than the new ones.')
    textoptions.add_option('--legacy-date-format', default=False, action='store_true',
                           help='use the legacy date format, rather than the new one.')
    textoptions.add_option('--list-symbols', metavar='4*CHAR',
                           help='use the characters given as list bullet symbols.')
    optionparser.add_option_group(textoptions)

    htmloptions = optparse.OptionGroup(optionparser, 'Html Format Options')
    htmloptions.add_option('--css', default=None,
                           help='Use the given CSS file instead of the builtin')
    htmloptions.add_option('--external-css', action='store_true', default=False,
                           help='place css in an external file')
    htmloptions.add_option('--rfc-base-url', default="https://www.rfc-editor.org/info/",
                           help='Base URL for RFC links')
    htmloptions.add_option('--id-base-url', default="https://www.ietf.org/archive/id/",
                           help='Base URL for Internet-Draft links')
    optionparser.add_option_group(htmloptions)

    v2v3options = optparse.OptionGroup(optionparser, 'V2-V3 Converter Options')
    v2v3options.add_option('--add-xinclude', action='store_true',
                           help='replace reference elements with RFC and Internet-Draft'
                           ' seriesInfo with the appropriate XInclude element')
    v2v3options.add_option('--strict', action='store_true',
                           help='be strict about stripping some deprecated attributes')
    optionparser.add_option_group(v2v3options)

    preptooloptions = optparse.OptionGroup(optionparser, 'Preptool Options')
    preptooloptions.add_option('--accept-prepped', action='store_true',
                           help='accept already prepped input')
    optionparser.add_option_group(preptooloptions)


    # --- Parse and validate arguments ---------------------------------

    (options, args) = optionparser.parse_args()
    # Some additional values not exposed as options
    options.doi_base_url = "https://doi.org/"

    # Show version information, then exit
    if options.version:
        print('%s %s' % (xml2rfc.NAME, xml2rfc.__version__))
        if options.verbose:
            try:
                import pkg_resources
                this = pkg_resources.working_set.by_key[xml2rfc.NAME]
                for p in this.requires():
                    dist = pkg_resources.get_distribution(p.key)
                    print('  %s'%dist)
            except:
                pass
        sys.exit(0)

    if len(args) < 1:
        optionparser.print_help()
        sys.exit(2)
    source = args[0]
    if not os.path.exists(source):
        sys.exit('No such file: ' + source)
    # Default (this may change over time):
    options.vocabulary = 'v2'
    # Option constraints
    if sys.argv[0].endswith('v2v3'):
        options.v2v3 = True
        options.utf8 = True
    #
    if options.preptool:
        options.vocabulary = 'v3'
        options.no_dtd = True
    else:
        if options.accept_prepped:
            sys.exit("You can only use --accept-prepped together with --preptool.")            
    if options.v2v3:
        options.vocabulary = 'v2'
        options.no_dtd = True
    #
    if options.basename:
        if options.output_path:
            sys.exit('--path and --basename has the same functionality, please use only --path')
        else:
            options.output_path = options.basename
            options.basename = None
    #
    num_formats = len([ o for o in [options.raw, options.text, options.nroff, options.html, options.expand, options.v2v3, options.preptool, options.info, ] if o])
    if num_formats > 1 and (options.filename or options.output_filename):
        sys.exit('Cannot give an explicit filename with more than one format, '
                 'use --path instead.')
    if num_formats < 1:
        # Default to paginated text output
        options.text = True
    if options.debug:
        options.verbose = True
    #
    if options.cache:
        if not os.path.exists(options.cache):
            try:
                os.makedirs(options.cache)
                if options.verbose:
                    xml2rfc.log.write('Created cache directory at', 
                                      options.cache)
            except OSError as e:
                print('Unable to make cache directory: %s ' % options.cache)
                print(e)
                sys.exit(1)
        else:
            if not os.access(options.cache, os.W_OK):
                print('Cache directory is not writable: %s' % options.cache)
                sys.exit(1)
    options.date = datetime.datetime.strptime(options.datestring, "%Y-%m-%d").date()
    if options.omit_headers and not options.text:
        sys.exit("You can only use --no-headers with paginated text output.")
    #
    if options.text and not options.legacy:
        if options.legacy_list_symbols and options.list_symbols:
            sys.exit("You cannot specify both --list-symbols and --legacy_list_symbols.")
        if options.list_symbols:
            options.list_symbols = tuple(list(options.list_symbols))
        elif options.legacy_list_symbols:
            options.list_symbols = ('o', '*', '+', '-')
        else:
            options.list_symbols = ('*', '-', 'o', '+')
    else:
        if options.legacy_list_symbols:
            sys.exit("You can only use --legacy_list_symbols with v3 text output.")
        if options.list_symbols:
            sys.exit("You can only use --list_symbols with v3 text output.")

    if not options.legacy:
        # I.e., V3 formatter
        options.no_dtd = True        
        if options.nroff:
            sys.exit("You can only use --nroff in legacy mode")
        if options.raw:
            sys.exit("You can only use --raw in legacy mode")

    if options.utf8:
        xml2rfc.log.warn("The --utf8 switch is deprecated.  Use the new unicode insertion element <u>\nto refer to unicode values in a protocol specification.")

    # ------------------------------------------------------------------

    # Setup warnings module
    # xml2rfc.log.warn_error = options.warn_error and True or False
    xml2rfc.log.quiet = options.quiet and True or False
    xml2rfc.log.verbose = options.verbose

    # Parse the document into an xmlrfc tree instance
    parser = xml2rfc.XmlRfcParser(source, verbose=options.verbose,
                                  quiet=options.quiet,
                                  cache_path=options.cache,
                                  no_network=options.no_network,
                                  templates_path=globals().get('_TEMPLATESPATH', None),
                              )
    try:
        xmlrfc = parser.parse(remove_pis=options.remove_pis, normalize=True)
    except xml2rfc.parser.XmlRfcError as e:
        xml2rfc.log.exception('Unable to parse the XML document: ' + args[0], e)
        sys.exit(1)
    except lxml.etree.XMLSyntaxError as e:
        # Give the lxml.etree.XmlSyntaxError exception a line attribute which
        # matches lxml.etree._LogEntry, so we can use the same logging function
        xml2rfc.log.exception('Unable to parse the XML document: ' + args[0], e.error_log)
        sys.exit(1)
        
    # Remember if we're building an RFC
    options.rfc = xmlrfc.tree.getroot().get('number')

    # Validate the document unless disabled
    if not options.no_dtd:
        ok, errors = xmlrfc.validate(dtd_path=options.dtd)
        if not ok:
            xml2rfc.log.exception('Unable to validate the XML document: ' + args[0], errors)
            sys.exit(1)

    if options.filename:
        xml2rfc.log.warn("The -f and --filename options are deprecated and will"
                        " go away in version 3.0 of xml2rfc.  Use -o instead")
        if options.output_filename and options.filename != options.output_filename:
            xml2rfc.log.warn("You should not specify conflicting -f and -o options.  Using -o %s"
                        % options.output_filename)
        if not options.output_filename:
            options.output_filename = options.filename

    # Execute any writers specified
    try:
        source_path, source_base = os.path.split(source)
        source_name, source_ext  = os.path.splitext(source_base)
        if options.output_path:
            if os.path.isdir(options.output_path):
                basename = os.path.join(options.output_path, source_name)
            else:
                sys.exit("The given output path '%s' is not a directory, cannot place output files there" % (options.output_path, ))
        else:
            # Create basename based on input
            basename = os.path.join(source_path, source_name)

        if options.expand and options.legacy:
            # Expanded XML writer needs a separate tree instance with
            # all comments and PI's preserved.  We can assume there are no
            # parse errors at this point since we didnt call sys.exit() during
            # parsing.
            filename = options.output_filename
            if not filename:
                filename = basename + '.exp.xml'
                options.output_filename = filename
            new_xmlrfc = parser.parse(remove_comments=False, quiet=True, normalize=False)
            expwriter = xml2rfc.ExpandedXmlWriter(new_xmlrfc,
                                                  options=options,
                                                  date=options.date)
            expwriter.write(filename)
            options.output_filename = None

        if options.html and options.legacy:
            filename = options.output_filename
            if not filename:
                filename = basename + '.html'
                options.output_filename = filename
            htmlwriter = xml2rfc.HtmlRfcWriter(xmlrfc,
                                               options=options,
                                               date=options.date,
                                               templates_dir=globals().get('_TEMPLATESPATH', None))
            htmlwriter.write(filename)
            options.output_filename = None

        if options.raw:
            filename = options.output_filename
            if not filename:
                filename = basename + '.raw.txt'
                options.output_filename = filename
            rawwriter = xml2rfc.RawTextRfcWriter(xmlrfc,
                                                 options=options,
                                                 date=options.date)
            rawwriter.write(filename)
            options.output_filename = None

        if options.text and options.legacy:
            filename = options.output_filename
            if not filename:
                filename = basename + '.txt'
                options.output_filename = filename
            pagedwriter = xml2rfc.PaginatedTextRfcWriter(xmlrfc,
                                                         options=options,
                                                         date=options.date,
                                                         omit_headers=options.omit_headers,
                                                     )
            pagedwriter.write(filename)
            options.output_filename = None

        if options.nroff:
            filename = options.output_filename
            if not filename:
                filename = basename + '.nroff'
                options.output_filename = filename
            nroffwriter = xml2rfc.NroffRfcWriter(xmlrfc,
                                                 options=options,
                                                 date=options.date)
            nroffwriter.write(filename)
            options.output_filename = None

        # --- End of legacy formatter invocations ---

        if options.expand and not options.legacy:
            xmlrfc = parser.parse(remove_comments=False, quiet=True, normalize=False, strip_cdata=False)
            filename = options.output_filename
            if not filename:
                filename = basename + '.exp.xml'
                options.output_filename = filename
            #v2v3 = xml2rfc.V2v3XmlWriter(xmlrfc, options=options, date=options.date)
            #xmlrfc.tree = v2v3.convert2to3()
            expander = xml2rfc.ExpandV3XmlWriter(xmlrfc, options=options, date=options.date)
            expander.write(filename)
            options.output_filename = None

        if options.v2v3:
            xmlrfc = parser.parse(remove_comments=False, quiet=True, normalize=False)
            filename = options.output_filename
            if not filename:
                filename = basename + '.v2v3.xml'
                options.output_filename = filename
            v2v3writer = xml2rfc.V2v3XmlWriter(xmlrfc, options=options, date=options.date)
            v2v3writer.write(filename)
            options.output_filename = None

        if options.preptool:
            xmlrfc = parser.parse(remove_comments=False, quiet=True)
            filename = options.output_filename
            if not filename:
                filename = basename + '.prepped.xml'
                options.output_filename = filename
            v2v3 = xml2rfc.V2v3XmlWriter(xmlrfc, options=options, date=options.date)
            xmlrfc.tree = v2v3.convert2to3()
            preptool = xml2rfc.PrepToolWriter(xmlrfc, options=options, date=options.date)
            preptool.write(filename)
            options.output_filename = None

        if options.text and not options.legacy:
            xmlrfc = parser.parse(remove_comments=False, quiet=True)
            filename = options.output_filename
            if not filename:
                filename = basename + '.txt'
                options.output_filename = filename
            v2v3 = xml2rfc.V2v3XmlWriter(xmlrfc, options=options, date=options.date)
            xmlrfc.tree = v2v3.convert2to3()
            prep = xml2rfc.PrepToolWriter(xmlrfc, options=options, date=options.date, liberal=True, keep_pis=[xml2rfc.V3_PI_TARGET])
            xmlrfc.tree = prep.prep()
            writer = xml2rfc.TextWriter(xmlrfc, options=options, date=options.date)
            writer.write(filename)
            options.output_filename = None

        if options.html and not options.legacy:
            xmlrfc = parser.parse(remove_comments=False, quiet=True)
            filename = options.output_filename
            if not filename:
                filename = basename + '.html'
                options.output_filename = filename
            v2v3 = xml2rfc.V2v3XmlWriter(xmlrfc, options=options, date=options.date)
            xmlrfc.tree = v2v3.convert2to3()
            prep = xml2rfc.PrepToolWriter(xmlrfc, options=options, date=options.date, liberal=True, keep_pis=[xml2rfc.V3_PI_TARGET])
            xmlrfc.tree = prep.prep()
            writer = xml2rfc.HtmlWriter(xmlrfc, options=options, date=options.date)
            writer.write(filename)
            options.output_filename = None

        if options.info:
            xmlrfc = parser.parse(remove_comments=False, quiet=True)
            filename = options.output_filename
            if not filename:
                filename = basename + '.json'
                options.output_filename = filename
            v2v3 = xml2rfc.V2v3XmlWriter(xmlrfc, options=options, date=options.date)
            xmlrfc.tree = v2v3.convert2to3()
            prep = xml2rfc.PrepToolWriter(xmlrfc, options=options, date=options.date, liberal=True, keep_pis=[xml2rfc.V3_PI_TARGET])
            xmlrfc.tree = prep.prep()
            info = extract_anchor_info(xmlrfc.tree)
            with open(filename, 'w') as fp:
                json.dump(info, fp, indent=2, ensure_ascii=False, encoding='utf-8')
            if not options.quiet:
                xml2rfc.log.write('Created file', filename)

    except xml2rfc.RfcWriterError as e:
        xml2rfc.log.error('Unable to convert the document: ' + args[0],  
                          '\n  ' + e.msg)

if __name__ == '__main__':

    major, minor = sys.version_info[:2]
    if not (major == 2 and minor >= 6) and not major == 3:
        print ("")
        print ("The xml2rfc script requires python 2, with a version of 2.6 or higher, or python 3.")
        print ("Can't proceed, quitting.")
        exit()

    main()
