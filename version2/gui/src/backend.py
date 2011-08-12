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
        self.halt = False
        self.destroyed = False
        self.verbose = True
        self.cache_path = None
        self.library_path = None
        self.output_dir = None
        self.current_docpath = None

        # Thread data to consume
        # Requests are in the format: (docpath, [fmt1, fmt2, ...])
        self.preview_request = None
        self.batch_request = None
        self.batch_formats = None

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

    def setLibrary(self, path):
        self.library_path = path
    
    def setVerbose(self, verbose):
        self.verbose = verbose
        
    def signalStatus(self, text):
        self.emit(SIGNAL('status(QString)'), text)
        
    def requestPreview(self, docpath, format):
        self.preview_request = (docpath, format)
        self.start()
        
    def requestBatch(self, paths, formats, outdir):
        self.output_dir = outdir
        self.batch_request = paths
        self.batch_formats = formats
        self.halt = False
        self.start()
    
    def signalHalt(self):
        self.halt = True
        
    def run(self):
        while not self.destroyed and self.preview_request or \
        self.batch_request:
            if self.preview_request:
                # Consume the preview request
                docpath, format = self.preview_request
                self.preview_request = None
                if docpath != self.current_docpath:
                    # Need to parse this docpath
                    ok, error, type = self.T_parseDocument(docpath)
                    if ok:
                        self.current_docpath = docpath
                        self.T_previewOutput(format)
                    else:
                        # Signal the line number of the top-level error
                        self.emit(SIGNAL('xmlError(QString, int)'), 
                                  error.message, error.line)
                else:
                    # Assume the xmlrfc is already valid
                    self.T_previewOutput(format)
            if self.batch_request:
                for row, path in enumerate(self.batch_request):
                    if self.halt:
                        # Stop processing
                        return
                    self.emit(SIGNAL('itemStarted(int)'), row)
                    # Parse the document
                    ok, error, type = self.T_parseDocument(path)
                    if ok:
                        basename = os.path.splitext(os.path.basename(path))[0]
                        for format in self.batch_formats:
                            # Create proper file extension
                            ext  = { self.RAW: '-raw.txt',
                                     self.PAGED: '.txt',
                                     self.HTML: '.html',
                                     self.NROFF: '.nroff' }[format]
                            outpath = os.path.join(self.output_dir, basename + ext)
                            # Run the writer
                            if format == self.HTML:
                                writer = xml2rfc.HtmlRfcWriter(self.xmlrfc, templates_dir=self.templates_dir)
                            else:
                                writer = self.writerClasses[format](self.xmlrfc)
                            writer.write(outpath)
                    self.emit(SIGNAL('itemFinished(int, bool, QString)'), row, ok, type)
                # Consume request
                self.batch_request = None
                self.emit(SIGNAL('batchFinished()'))
                

    def deleteCache(self, path):
        xml2rfc.XmlRfcParser('').delete_cache(path=path)

# ----------------------------------------------------
# Thread-only functions, do not call directly
# ----------------------------------------------------

    def T_previewOutput(self, format):
        """ Emit the output for a format as a QString """
        if format <= self.NROFF and format != self.XML and self.xmlrfc:
            # Write xmlrfc to new temp file
            self.signalStatus('Converting XML document ' + \
                              self.current_docpath + '...')
            if format == self.HTML:
                writer = xml2rfc.HtmlRfcWriter(self.xmlrfc, templates_dir=self.templates_dir)
            else:
                writer = self.writerClasses[format](self.xmlrfc)
            file = tempfile.TemporaryFile()
            writer.write('', tmpfile=file)
            file.seek(0)
            self.emit(SIGNAL('preview(QString, int, QString)'),
                      file.read(), format, self.current_docpath)

    def T_parseDocument(self, path):
        """ Parse an XML document and store the generated tree """
        # Create the parser
        parser = xml2rfc.XmlRfcParser(path, 
                                      verbose=self.verbose, 
                                      cache_path=self.cache_path,
                                      library_path=self.library_path,
                                      templates_path=self.templates_dir)

        # Try to parse the document, catching any errors
        self.xmlrfc = None
        self.signalStatus('Parsing XML document ' + path + '...')
        try:        
            self.xmlrfc = parser.parse()
        except lxml.etree.XMLSyntaxError, error:
            xml2rfc.log.error('Unable to parse the XML document:', path,
                              '\n  ' + error.msg)
            # return the line number(s) of the error(s)
            # hack in attributes to keep consistent with validation errors
            error.line = error.position[0]
            error.message = error.msg
            return False, error, 'syntax'
        
        # Try to validate the document, catching any errors
        ok, errors = self.xmlrfc.validate()
        self.signalStatus('Validating XML document ' + path + '...')
        if not ok:
            error_str = 'Unable to validate the XML document: ' + path
            for error in errors:
                error_str += '\n  Line ' + str(error.line) + ': '
                error_str += error.message
            xml2rfc.log.error(error_str)
            return False, errors[0], 'validation'

        # Return success, no error object attached
        return True, None, 'pass'

