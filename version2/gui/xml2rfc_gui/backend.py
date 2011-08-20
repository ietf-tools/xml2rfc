# Python libs
import sys
import os
import tempfile

# External libs
import lxml

# My modules
import xml2rfc
import utils

from PyQt4.QtCore import *

class XmlRfcHandler(QThread):
    """ QThread to connect with xml2rfc library """
    # Enum of format types
    XML, PAGED, RAW, HTML, NROFF = range(5)
    
    writerClasses = { RAW: xml2rfc.RawTextRfcWriter,
                      PAGED: xml2rfc.PaginatedTextRfcWriter,
                      HTML: xml2rfc.HtmlRfcWriter,
                      NROFF: xml2rfc.NroffRfcWriter }
    
    # Wrapper methods to pass QString signals for stdout/stderr
    def _stdout(self, data):
        self.emit(SIGNAL('stdout(QString)'), QString(data))

    def _stderr(self, data):
        self.emit(SIGNAL('stderr(QString)'), QString(data))

    def __init__(self):
        QThread.__init__(self)
        # self.halt = False
        self.destroyed = False
        self.verbose = True
        self.cache_path = None
        self.library_dirs = None
        self.network_loc = None

        # Thread data to consume
        self.request_input = None
        self.request_output_dir = None
        self.request_formats = None

        # Temporary xmlrfc instance for requesting fast previews
        self.xmlrfc = None
        
        # Determine a usable templates directory in pyqt
        self.templates_dir = 'templates'
        for dir in [os.path.dirname(sys.executable),
                    os.path.dirname(xml2rfc.__file__),]:
            dir = os.path.normpath(os.path.join(dir, 'templates'))
            if os.path.exists(dir):
                self.templates_dir = dir
        
            
        # Override log streams to use QThread callbacks
        xml2rfc.log.write_out = utils.StreamHandler(self._stdout)
        xml2rfc.log.write_err = utils.StreamHandler(self._stderr)
        
    def __del__(self):
        """ Safety destructor """
        self.destroyed = True
        self.wait()

    def setCache(self, path):
        self.cache_path = path

    def setLocalLibraries(self, dirstring):
        self.library_dirs = dirstring

    def setNetworkLibrary(self, url):
        self.network_loc = url
    
    def setVerbose(self, verbose):
        self.verbose = verbose
        
    def signalStatus(self, text):
        self.emit(SIGNAL('status(QString)'), text)
        
    def convert(self, input_file, formats, output_dir):
        self.request_output_dir = output_dir or os.path.dirname(input_file)
        self.request_formats = formats
        self.request_input = input_file
        self.start()
    
    def signalHalt(self):
        self.halt = True
        
    def run(self):
        while not self.destroyed and self.request_input:
            # Consume the request
            path = self.request_input
            formats = self.request_formats
            output_dir = self.request_output_dir
            self.request_input = None
            # Parse the document
            ok = self.T_parseDocument(path)
            if ok:
                basename = os.path.splitext(os.path.basename(path))[0]
                for format in formats:
                    # Create proper file extension
                    ext  = { self.RAW: '-raw.txt',
                             self.PAGED: '.txt',
                             self.HTML: '.html',
                             self.NROFF: '.nroff' }[format]
                    outpath = os.path.join(output_dir, basename + ext)
                    # Run the writer
                    if format == self.HTML:
                        writer = xml2rfc.HtmlRfcWriter(self.xmlrfc, templates_dir=self.templates_dir)
                    else:
                        writer = self.writerClasses[format](self.xmlrfc)
                    writer.write(outpath)
                    # Signal UI to load the output
                    self.emit(SIGNAL('viewDocument(int, QString)'), format, outpath)
                self.emit(SIGNAL('finished(int)'), format)

    def deleteCache(self, path):
        xml2rfc.XmlRfcParser('').delete_cache(path=path)

# ----------------------------------------------------
# Thread-only functions, do not call directly
# ----------------------------------------------------

    def T_parseDocument(self, path):
        """ Parse an XML document and store the generated tree """
        # Create the parser
        parser = xml2rfc.XmlRfcParser(path, 
                                      verbose=self.verbose, 
                                      cache_path=self.cache_path,
                                      templates_path=self.templates_dir,
                                      library_dirs=self.library_dirs,
                                      network_loc=self.network_loc)

        # Try to parse the document, catching any errors
        self.xmlrfc = None
        self.signalStatus('Parsing XML document ' + path + '...')
        try:        
            self.xmlrfc = parser.parse()
        except (lxml.etree.XMLSyntaxError, xml2rfc.parser.XmlReferenceError), error:
            xml2rfc.log.error('Unable to parse the XML document: ' + path + '\n')
            # Signal UI with error
            linestr = error.position[0] > 0 and 'Line ' + str(error.position[0]) + ': ' \
                      or ''
            msg = linestr + error.msg
            self.emit(SIGNAL('error(QString, int)'), msg, error.position[0])
            return False
        
        # Try to validate the document, catching any errors
        ok, errors = self.xmlrfc.validate()
        self.signalStatus('Validating XML document ' + path + '...')
        if not ok:
            xml2rfc.log.error('Unable to validate the XML document: ' + path + '\n')
            for error in errors:
                msg = 'Line ' + str(error.line) + ': ' + error.message
                self.emit(SIGNAL('error(QString, int)'), msg, error.line)
            return False

        # Return success, no error object attached
        return True

