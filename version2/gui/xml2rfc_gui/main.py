# Main module for xml2rfc-gui

VERSION = (0, 5, 4)

# xml2rfc module
import xml2rfc

# PyQt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtNetwork  # Required for py2exe for some reason

# UI modules    
import ui_mainwindow
import ui_about
import ui_report

# My modules    
from settings import Settings
from backend import XmlRfcHandler
from utils import Status

# Python
import os
import sys
import lxml

ICON_DEFAULT    = QStyle.SP_FileIcon
ICON_GOOD       = QStyle.SP_DialogApplyButton
ICON_BAD        = QStyle.SP_MessageBoxCritical
ICON_WORKING    = QStyle.SP_MessageBoxQuestion


def stdIcon(val):
    """ Return the standard icon for the value given """
    return QIcon(qApp.style().standardPixmap(val))


class FileItem(QListWidgetItem):
    """ Item class for file list """
    def __init__(self, path):
        self.path = path
        self.basename = os.path.basename(path)
        self.passed = False
        
        # Create item, set proper display roles
        QListWidgetItem.__init__(self)
        self.setData(Qt.DisplayRole, self.basename)
        icon = stdIcon(ICON_DEFAULT)
        self.setData(Qt.DecorationRole, icon)
        
    def flag(self, passed):
        """ Flag the item as passed or failed and update the icon """
        self.passed = passed
        if passed:
            self.setData(Qt.DecorationRole, stdIcon(ICON_GOOD))
        else:
            self.setData(Qt.DecorationRole, stdIcon(ICON_BAD))

class MainWindow(QMainWindow):
    """ Main window class """

    def __init__(self):
        # Super
        QMainWindow.__init__(self)
        self.locked = False
        self.last_path = None
        self.report = {}

        # Initialize UI class
        self.ui = ui_mainwindow.Ui_mainWindow()
        self.ui.setupUi(self)
        
        # Initialize status
        self.status = Status(self.statusBar())
        
        # Setup backend thread to connect with xml2rfc library
        self.status('Loading backend...')
        self.handler = XmlRfcHandler()
        
        # Connect backend thread signals
        self.connect(self.handler, SIGNAL('finished()'), self.unlockWidgets)
        self.connect(self.handler, SIGNAL('terminated()'), self.unlockWidgets)
        self.connect(self.handler, SIGNAL('stdout(QString)'), 
                     self.stdOutCallback)
        self.connect(self.handler, SIGNAL('stderr(QString)'), 
                     self.stdErrCallback)
        self.connect(self.handler, SIGNAL('preview(QString, int, QString)'), 
                     self.recievePreview)
        self.connect(self.handler, SIGNAL('xmlError(QString, int)'), 
                     self.recieveError)
        self.connect(self.handler, SIGNAL('status(QString)'), 
                     self.status.__call__)
        self.connect(self.handler, SIGNAL('itemStarted(int)'),
                     self.itemStarted)
        self.connect(self.handler, SIGNAL('itemFinished(int, bool, QString)'),
                     self.itemFinished)
        self.connect(self.handler, SIGNAL('batchFinished()'),
                     self.showReport)

        
        # Create Settings instance
        self.status('Loading settings...')
        self.settings = Settings(self, self.handler)
        self.status('Ready')
        
        # Connect main actions
        self.connect(self.ui.actionQuit,    SIGNAL('triggered()'),  self.close)
        self.connect(self.ui.actionAbout,   SIGNAL('triggered()'),  self.showAbout)
        self.connect(self.ui.actionAboutQt, SIGNAL('triggered()'),  self.showAboutQt)
        self.connect(self.ui.actionAdd,     SIGNAL('triggered()'),  self.addFiles)
        self.connect(self.ui.actionClear,   SIGNAL('triggered()'),  self.clearQueue)
        self.connect(self.ui.actionPreferences, SIGNAL('triggered()'),
                     self.settings.showPreferences)
        self.connect(self.ui.outputDirButton, SIGNAL('clicked()'),
                     self.changeOutputDir)
        self.connect(self.ui.convertButton, SIGNAL('clicked()'),
                     self.batchConvert)

        # Connect widget events
        self.connect(self.ui.fileList,
                     SIGNAL('itemDoubleClicked(QListWidgetItem*)'), 
                     self.fileClicked)
        self.connect(self.ui.previewTabWidget,
                     SIGNAL('currentChanged(int)'),
                     self.previewTabChanged)

        # Create mapping of format types to UI tab indicies
        self.fmt2Tab = { self.handler.XML: 0,
                         self.handler.PAGED: 1,
                         self.handler.RAW: 2,
                         self.handler.HTML: 3,
                         self.handler.NROFF: 4 }
        
        # And the inverse, since python doesnt have a bijection structure
        self.tab2Fmt = {}
        for key, val in self.fmt2Tab.items():
            self.tab2Fmt[val] = key

        # Create mapping of format types to UI Editors
        self.editors = { self.handler.XML: self.ui.textXml,
                         self.handler.PAGED: self.ui.textPaged,
                         self.handler.RAW: self.ui.textRaw,
                         self.handler.NROFF: self.ui.textNroff }

        # Flags to track whether or not we've ran a writer for temp document
        self.ranWriterFlags = { self.handler.PAGED: False,
                           self.handler.RAW: False,
                           self.handler.NROFF: False, 
                           self.handler.HTML: False }
        
        # Maintain a list of widgets to lock during batch processing
        self.lockableWidgets = [
                                    self.ui.previewTabWidget,
                                    self.ui.outputDirButton,
                                    self.ui.outputDirText,
                                    self.ui.settingWarningError,
                                    self.ui.settingVerbose,
                                    self.ui.formatRaw,
                                    self.ui.formatPaged,
                                    self.ui.formatHtml,
                                    self.ui.formatNroff,
                                    self.ui.buttonAdd,
                                    self.ui.buttonClear,
                                    self.ui.fileList,
                                ]
    def lockWidgets(self):
        """ Disables interaction with all widgets in lockable list """
        self.locked = True
        self.ui.convertButton.setText('Halt')
        for widget in self.lockableWidgets:
            widget.setEnabled(False)
        
    def unlockWidgets(self):
        """ Enables interaction with all widgets in lockable list """
        self.locked = False
        self.ui.convertButton.setText('Convert')
        for widget in self.lockableWidgets:
            widget.setEnabled(True)
            
    def stdOutCallback(self, text, color='black'):
        """ Redirect text to QTextWidget """
        self.ui.textOutput.insertHtml(\
            QString('<br><span style="color:%2">%1</span>').arg(text).arg(color))
        # Scroll to bottom  
        cursor = self.ui.textOutput.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.textOutput.setTextCursor(cursor)
        self.ui.textOutput.update()

    def stdErrCallback(self, text):
        self.stdOutCallback(text, color='red')
        
    def recievePreview(self, text, format, docname):
        """ Recieved a prepared preview request, display it in editor """
        self.status('Viewing document ' + docname)
        if format == self.handler.HTML:
            self.ui.htmlView.setHtml(text)
            self.openPreviewTab(format)
        elif format <= self.handler.NROFF:
            self.editors[format].setPlainText(text)
            self.openPreviewTab(format)
        
    def recieveError(self, message, line):
        """ Recieved an XML error, highlight the line and jump to it """
        self.status('Error: ' + message)
        if self.settings.value('preview/openXmlOnErrors').toBool():
            cursor = self.ui.textXml.textCursor()
            cursor.setPosition(0)
            cursor.movePosition(QTextCursor.Down, \
                                QTextCursor.MoveAnchor, \
                                line - 1)
            self.ui.textXml.setTextCursor(cursor)
            self.ui.textXml.highlightCurrentLine()
            self.openPreviewTab(self.handler.XML)
            
    def openPreviewTab(self, format):
        self.ui.previewTabWidget.setCurrentIndex(self.fmt2Tab[format])

    def showAbout(self):
        """ Show the about window """
        about = QDialog(self)
        about.ui = ui_about.Ui_Dialog()
        about.ui.setupUi(about)
        # Replace proper version numbers
        about.ui.xml2rfc_gui_version.setText('xml2rfc-gui version: ' + \
                                             '.'.join(map(str, VERSION)))
        about.ui.xml2rfc_version.setText('xml2rfc version: ' + \
                                         '.'.join(map(str, xml2rfc.VERSION)))
        about.exec_()
        
    def showAboutQt(self):
        """ Show the about qt window """
        QMessageBox.aboutQt(self, 'About Qt')
    
    def addFiles(self):
        """ Add one or more files to the queue """
        # Request file names with dialog
        self.status.push('Adding a new file')
        homePath = QDesktopServices.storageLocation(QDesktopServices.HomeLocation)
        filenames = QFileDialog.getOpenFileNames(self, 'Select one or more documents to convert', \
                                                 homePath, 'XML Files (*.xml)')
        self.status.pop()

        # Add files to list view
        for filename in filenames:
            self.ui.fileList.addItem(FileItem(str(filename)))

    def changeOutputDir(self):
        self.status.push('Setting output directory')
        dir = QFileDialog.getExistingDirectory(caption='Select output directory')
        self.status.pop()
        if dir:
            self.ui.outputDirText.setText(dir)
            return True
        else:
            return False
        
    def showReport(self):
        report = QDialog(self)
        report.ui = ui_report.Ui_Report()
        report.ui.setupUi(report)
        # Fill in values
        repmap = {'pass': report.ui.pass_label,
                  'syntax': report.ui.syntax_label,
                  'validation': report.ui.validation_label,}
        for key, val in repmap.items():
            count = self.report.get(key, 0)
            val.setText(str(count))
            if count < 1:
                # Disable coloring
                val.setStyleSheet('')
        report.exec_()

    def batchConvert(self):
        if self.locked:
            # Already processing, halt execution
            self.handler.signalHalt()
            self.showReport()

        else:
            self.settings.verify()
            dir = self.ui.outputDirText.text()
            outpath = os.path.normpath(os.path.expanduser(str(dir)))
            if not dir:
                # Try to set a directory
                if not self.changeOutputDir():
                    return
            elif not os.path.exists(outpath):
                if QMessageBox.question(self, 'New Directory', 'The specified '
                                        'output directory does not exist.  Should '
                                        'I create it now?', 'No', 'Yes'):
                    try:
                        os.makedirs(outpath)
                    except OSError:
                        # Directory is not writable, try to set a new one
                        if QMessageBox.question(self, 'Invalid Directory',
                                                'You don\'t have permission to write '
                                                'to the specified outupt directory.  '
                                                'Do you want to choose a new one?',
                                                'No', 'Yes') and self.changeOutputDir():
                            outpath = str(self.ui.outputDirText.text())
                        else:
                            return
            elif not os.access(outpath, os.W_OK):
                if QMessageBox.question(self, 'Invalid Directory',
                        'You don\'t have permission to write '
                        'to the specified outupt directory.  '
                        'Do you want to choose a new one?',
                        'No', 'Yes') and self.changeOutputDir():
                    outpath = str(self.ui.outputDirText.text())
                else:
                    return
        
            # If we're here, the directory is valid
            # Assemble formats to write
            formats = [key for key, val in \
              { self.handler.PAGED: self.ui.formatPaged.checkState(),
                self.handler.RAW:   self.ui.formatRaw.checkState(),
                self.handler.HTML:  self.ui.formatHtml.checkState(),
                self.handler.NROFF: self.ui.formatNroff.checkState() }.items() \
              if val]
            verbose = bool(self.ui.settingVerbose.checkState())
            abs_cache = os.path.expanduser(str(self.settings.value('cache/location').toString()))
            abs_library = os.path.expanduser(str(self.settings.value('library/location').toString()))
            self.handler.setCache(abs_cache)
            self.handler.setLibrary(abs_library)
            self.handler.setVerbose(verbose)
    
            if len(formats) > 0:
                items = [self.ui.fileList.item(index) for 
                         index in range(self.ui.fileList.count())]
                paths = [item.path for item in items]
                outdir = outpath
                self.lockWidgets()
                self.newReport()
                self.handler.requestBatch(paths, formats, outdir)
            else:
                QMessageBox.warning(self, 'Warning',
                                    'You must select at least one output format.')

    def itemStarted(self, row):
        """ Intermediate callback during batch processing """
        # Set the icon as working and center the list view
        item = self.ui.fileList.item(row)                  
        item.setData(Qt.DecorationRole, stdIcon(ICON_WORKING))
        self.ui.fileList.setItemSelected(item, True)
        self.ui.fileList.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def itemFinished(self, row, passed, type):
        """ Intermediate callback during batch processing """
        # Flag the item as good or bad
        self.ui.fileList.item(row).flag(passed)
        # Update the report
        type = str(type)
        if type in self.report:
            self.report[type] += 1
            
    def newReport(self):
        self.report = {'syntax': 0, 'validation': 0, 'pass': 0}

    def clearQueue(self):
        """ Clear the list """
        self.ui.fileList.clear()
    
    def clearPreview(self):
        # Empty editor text
        for editor in self.editors.values():
            editor.setPlainText('')
        # Reset format flags
        for key in self.ranWriterFlags.keys():
            self.ranWriterFlags[key] = False
    
    def fileClicked(self, item):
        """ Callback to list item clicked """
        self.settings.verify()
        self.clearPreview()
        # Load XML document in XML viewer
        xmlfile = open(item.path, 'r')
        self.ui.textXml.setPlainText(xmlfile.read())
        defaultFormat, _ = self.settings.value('preview/defaultFormat').toInt()   
        self.last_path = item.path
        self.requestPreviewForFormat(item.path, defaultFormat)

    def previewTabChanged(self, tabIndex):
        format = self.tab2Fmt[tabIndex]
        if format != self.handler.XML and self.last_path:
            # Check if we already ran the writer for this document
            if not self.ranWriterFlags[format]:
                self.requestPreviewForFormat(self.last_path, format)
                self.ranWriterFlags[format] = True
                
    def requestPreviewForFormat(self, path, format):
        # Call xml2rfc library with current settings
        abs_cache = os.path.expanduser(str(self.settings.value('cache/location').toString()))
        abs_library = os.path.expanduser(str(self.settings.value('library/location').toString()))
        verbose = bool(self.ui.settingVerbose.checkState())
        self.lockWidgets()
        self.handler.setCache(abs_cache)
        self.handler.setLibrary(abs_library)
        self.handler.setVerbose(verbose)
        self.handler.requestPreview(path, format)

    def closeEvent(self, *args, **kwargs):
        # Cleanup settings
        self.settings.destroy()
        return QMainWindow.closeEvent(self, *args, **kwargs)

def main():
    # Create Qt Application
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()

    # Ensure applications exits when all windows are closed
    QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))
    
    # Run application
    window.show()
    window.raise_()
    sys.exit(app.exec_())
