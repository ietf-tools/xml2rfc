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

import optparse
import os
import xml2rfc
import lxml.etree
import datetime


def display_version(self, opt, value, parser):
    print(xml2rfc.__version__)
    sys.exit()


def clear_cache(self, opt, value, parser):
    xml2rfc.parser.XmlRfcParser('').delete_cache()
    sys.exit()


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
    formatgroup.add_option('', '--text', dest='text', action='store_true',
                           help='outputs to a text file with proper page '
                           'breaks')
    formatgroup.add_option('', '--html', dest='html', action='store_true',
                           help='outputs to an html file')
    formatgroup.add_option('', '--nroff', dest='nroff', action='store_true',
                           help='outputs to an nroff file')
    formatgroup.add_option('', '--raw', dest='raw', action='store_true',
                           help='outputs to a text file, unpaginated')
    formatgroup.add_option('', '--exp', dest='exp', action='store_true',
                           help='outputs to an XML file with all references'
                           ' expanded')
    optionparser.add_option_group(formatgroup)


    plain_options = optparse.OptionGroup(optionparser, 'Plain Options')
    plain_options.add_option('-C', '--clear-cache', action='callback',
                            help='purge the cache and exit', callback=clear_cache)
    plain_options.add_option('-n', '--no-dtd', dest='no_dtd', action='store_true',
                            help='disable DTD validation step')
    plain_options.add_option('-N', '--no-network', dest='no_network', action='store_true',
                            help='don\'t use the network to resolve references', default=False)
    plain_options.add_option('-q', '--quiet', action='store_true',
                            dest='quiet', help='dont print anything')
    plain_options.add_option('-v', '--verbose', action='store_true',
                            dest='verbose', help='print extra information')
    plain_options.add_option('-V', '--version', action='callback',
                            help='display the version number and exit',
                            callback=display_version)
    optionparser.add_option_group(plain_options)


    value_options = optparse.OptionGroup(optionparser, 'Other Options')
    value_options.add_option('-b', '--basename', dest='basename', metavar='NAME',
                            help='specify the base name for output files')
    value_options.add_option('-c', '--cache', dest='cache', 
                            help='specify an alternate cache directory to write to')
    value_options.add_option('-d', '--dtd', dest='dtd', help='specify an alternate dtd file')
    value_options.add_option('-D', '--date', dest='datestring', metavar='DATE',
                            default=datetime.datetime.today().strftime("%Y-%m-%d"),
                            help='run as if thedate is DATE (format: yyyy-mm-dd)')
    value_options.add_option('-f', '--filename', dest='filename', metavar='FILE',
                            help='Deprecated.  The same as -o.')
    value_options.add_option('-o', '--out', dest='output_filename', metavar='FILE',
                            help='specify an explicit output filename')
    optionparser.add_option_group(value_options)


    formatoptions = optparse.OptionGroup(optionparser, 'Format Options', 
                                       ' Some formats accept additional format-specific options')
    formatoptions.add_option('', '--no-headers', dest='omit_headers', action='store_true',
                           help='with --text: calculate page breaks, and emit form feeds and page top'
                           ' spacing, but omit headers and footers from the paginated format'
                       )
    optionparser.add_option_group(formatoptions)


    # Parse and validate arguments
    (options, args) = optionparser.parse_args()
    if len(args) < 1:
        optionparser.print_help()
        sys.exit(2)
    source = args[0]
    if not os.path.exists(source):
        sys.exit('No such file: ' + source)
    num_formats = len([ o for o in [options.raw, options.text, options.nroff, options.html, options.exp] if o])
    if num_formats > 1 and (options.filename or options.output_filename):
        sys.exit('Cannot give an explicit filename with more than one format, '
                 'use --basename instead.')
    if num_formats < 1:
        # Default to paginated text output
        options.text = True
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

    # Setup warnings module
    # xml2rfc.log.warn_error = options.warn_error and True or False
    xml2rfc.log.quiet = options.quiet and True or False
    xml2rfc.log.verbose = options.verbose

    # Parse the document into an xmlrfc tree instance
    parser = xml2rfc.XmlRfcParser(source, verbose=options.verbose,
                                  quiet=options.quiet,
                                  cache_path=options.cache,
                                  no_network=options.no_network,
                                  templates_path=globals().get('_TEMPLATESPATH', None))
    try:
        xmlrfc = parser.parse()
    except xml2rfc.parser.XmlRfcError as e:
        xml2rfc.log.exception('Unable to parse the XML document: ' + args[0], e)
        sys.exit(1)
    except lxml.etree.XMLSyntaxError as e:
        # Give the lxml.etree.XmlSyntaxError exception a line attribute which
        # matches lxml.etree._LogEntry, so we can use the same logging function
        xml2rfc.log.exception('Unable to parse the XML document: ' + args[0], e.error_log)
        sys.exit(1)
        
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
        if options.basename:
            if os.path.isdir(options.basename):
                basename = os.path.join(options.basename, source_name)
            else:
                basename = options.basename
        else:
            # Create basename based on input
            basename = os.path.join(source_path, source_name)

        if options.exp:
            # Expanded XML writer needs a separate tree instance with
            # all comments and PI's preserved.  We can assume there are no
            # parse errors at this point since we didnt call sys.exit() during
            # parsing.
            new_xmlrfc = parser.parse(remove_comments=False, quiet=True)
            expwriter = xml2rfc.ExpandedXmlWriter(new_xmlrfc,
                                                  quiet=options.quiet,
                                                  verbose=options.verbose,
                                                  date=options.date)
            filename = options.output_filename
            if not filename:
                filename = basename + '.exp.xml'
            expwriter.write(filename)
        if options.html:
            htmlwriter = xml2rfc.HtmlRfcWriter(xmlrfc,
                                               quiet=options.quiet,
                                               verbose=options.verbose,
                                               date=options.date,
                                               templates_dir=globals().get('_TEMPLATESPATH', None))
            filename = options.output_filename
            if not filename:
                filename = basename + '.html'
            htmlwriter.write(filename)
        if options.raw:
            rawwriter = xml2rfc.RawTextRfcWriter(xmlrfc,
                                                 quiet=options.quiet,
                                                 verbose=options.verbose,
                                                 date=options.date)
            filename = options.output_filename
            if not filename:
                filename = basename + '.raw.txt'
            rawwriter.write(filename)
        if options.text:
            pagedwriter = xml2rfc.PaginatedTextRfcWriter(xmlrfc,
                                                         quiet=options.quiet,
                                                         verbose=options.verbose,
                                                         date=options.date,
                                                         omit_headers=options.omit_headers,
                                                     )
            filename = options.output_filename
            if not filename:
                filename = basename + '.txt'
            pagedwriter.write(filename)
        if options.nroff:
            nroffwriter = xml2rfc.NroffRfcWriter(xmlrfc,
                                                 quiet=options.quiet,
                                                 verbose=options.verbose,
                                                 date=options.date)
            filename = options.output_filename
            if not filename:
                filename = basename + '.nroff'
            nroffwriter.write(filename)
    except xml2rfc.RfcWriterError as e:
        xml2rfc.log.error('Unable to convert the document: ' + args[0],  
                          '\n  ' + e.msg)

if __name__ == '__main__':

    major, minor = sys.version_info[:2]
    if not major == 2 and minor >= 6:
        print ("")
        print ("The xml2rfc script requires python 2, with a version of 2.6 or higher.")
        print ("Can't proceed, quitting.")
        exit()

    main()
