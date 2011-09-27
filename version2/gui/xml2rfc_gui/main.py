# Main module for xml2rfc-gui

VERSION = (0, 7, 3)

# xml2rfc module
import xml2rfc

# PyQt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtWebKit
import PyQt4.QtNetwork  # Required for py2exe for some reason

# UI modules    
import ui_mainwindow
import ui_about
import ui_report
import ui_help

# My modules    
from settings import Settings
from backend import XmlRfcHandler
from utils import Status
from editor import LinedEditor
import doc

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
        self.input_file = None
        self.xml_modified = False

        # Initialize UI class
        self.ui = ui_mainwindow.Ui_mainWindow()
        self.ui.setupUi(self)

        # Handles to text editors
        self.textEditors = []
        self.xmlEditor = None
        
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
        self.connect(self.handler, SIGNAL('viewDocument(int, QString)'), 
                     self.viewDocument)
        self.connect(self.handler, SIGNAL('finished(int)'),
                     self.convertFinished)
        self.connect(self.handler, SIGNAL('error(QString, int)'), 
                     self.recieveError)
        self.connect(self.handler, SIGNAL('status(QString)'), 
                     self.status.__call__)
        
        # Create Settings instance
        self.status('Loading settings...')
        self.settings = Settings(self, self.handler)
        self.status('Ready')
        
        # Connect main actions
        self.connect(self.ui.actionQuit,    SIGNAL('triggered()'),  self.close)
        self.connect(self.ui.actionHelp,    SIGNAL('triggered()'),  self.showHelp)
        self.connect(self.ui.actionAbout,   SIGNAL('triggered()'),  self.showAbout)
        self.connect(self.ui.actionAboutQt, SIGNAL('triggered()'),  self.showAboutQt)
        self.connect(self.ui.actionOpen,    SIGNAL('triggered()'),  self.openFile)
        self.connect(self.ui.actionSave,    SIGNAL('triggered()'),  self.saveFile)
        self.connect(self.ui.actionPreferences, SIGNAL('triggered()'),
                     self.settings.showPreferences)

        # Connect persistent UI settings
        self.connect(self.ui.actionOptionVerbose, SIGNAL('toggled(bool)'),
                     self.settings.setVerbose)

        # Connect any other widgets
        self.connect(self.ui.convertButton, SIGNAL('clicked()'),
                     self.convert)
        self.connect(self.ui.textConsole, SIGNAL('anchorClicked(const QUrl&)'),
                     self.consoleLinkClicked)
        self.connect(self.ui.tabWidget, SIGNAL('currentChanged(int)'),
                     self.tabChanged)

        # Label data
        self.formatLabels = {
            self.handler.XML: 'XML',
            self.handler.PAGED: 'Paginated Text',
            self.handler.RAW: 'Raw Text',
            self.handler.HTML: 'HTML',
            self.handler.NROFF: 'Nroff',
        }

        # Maintain a list of widgets to lock during batch processing
        self.lockableWidgets = [
            self.ui.formatRaw,
            self.ui.formatPaged,
            self.ui.formatHtml,
            self.ui.formatNroff,
            self.ui.convertButton
        ]

        # Was input file passed on commandline?
        if len(sys.argv) > 1:
            path = sys.argv[1]
            if os.access(path, os.R_OK):
                self.input_file = path
                self.ui.sourceLabel.setText(path)
                self.deleteTabs()
                self.viewDocument(self.handler.XML, path)

    def lockWidgets(self):
        """ Disables interaction with all widgets in lockable list """
        self.locked = True
        for widget in self.lockableWidgets:
            widget.setEnabled(False)
        
    def unlockWidgets(self):
        """ Enables interaction with all widgets in lockable list """
        self.locked = False
        for widget in self.lockableWidgets:
            widget.setEnabled(True)
            
    def stdOutCallback(self, text, color='black'):
        """ Redirect text to QTextWidget """
        # Replace newlines with <br>
        text = text.replace('\n', '<br>')
        self.ui.textConsole.insertHtml(\
            QString('<br><span style="color:%2">%1</span>').arg(text).arg(color))
        # Scroll to bottom  
        cursor = self.ui.textConsole.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.textConsole.setTextCursor(cursor)
        self.ui.textConsole.update()

    def stdErrCallback(self, text):
        self.stdOutCallback(text, color='red')

    def consoleLinkClicked(self, url):
        try:
            line = int(str(url.toString()).partition('line_')[2])
            self.gotoXmlLine(line)
        except ValueError:
            pass  # Invalid format
        
    def viewDocument(self, format, path):
        """ Open a finished document in a new editor tab """
        self.ui.tabWidget.setStyleSheet('QTabWidget::pane {background: none;}')

        # Read document
        fh = open(path, 'r')
        data = fh.read()
        fh.close()

        # Create a new editor and configure with current settings
        frame = QWidget(self.ui.tabWidget)
        label = self.formatLabels[format]
        if format == self.handler.HTML:
            editor = PyQt4.QtWebKit.QWebView(frame)
            editor.setHtml(data)
        else:
            editor = LinedEditor(parent=frame)
            font = QFont(self.settings.value('appearance/previewFontFamily').toString(),
                         self.settings.value('appearance/previewFontSize').toInt()[0])
            editor.setFont(font)
            editor.setPlainText(data)
            if format == self.handler.XML:
                if not os.access(path, os.W_OK):
                    # Read only!
                    editor.setReadOnly(True)
                    label += ' (Read-only)'
                lineNumbers = self.settings.value('appearance/previewLineNumbersXml').toBool()
                self.xmlEditor = editor
                # Create callback
                self.connect(editor, SIGNAL('textChanged()'), self.xmlChanged)
                self.xml_modified = False
            else:
                lineNumbers = self.settings.value('appearance/previewLineNumbersText').toBool()
                editor.setReadOnly(True)
            editor.enableLineNumbers = lineNumbers
            self.textEditors.append(editor)

        # Add editor to the tab
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(editor)
        frame.setLayout(layout)       
        self.ui.tabWidget.addTab(frame, label)

    def convertFinished(self, lastFormat):
        # Open tab
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)
        # Update status
        if self.input_file:
            self.status('Viewing document ' + self.input_file)

    def tabChanged(self, index):
        pass

    def gotoXmlLine(self, line):
        """ Jump to a line in the current XML document """
        if self.xmlEditor:
            cursor = self.xmlEditor.textCursor()
            cursor.setPosition(0)
            cursor.movePosition(QTextCursor.Down, \
                                QTextCursor.MoveAnchor, \
                                line - 1)
            self.xmlEditor.setTextCursor(cursor)
            self.xmlEditor.centerCursor()
        
    def recieveError(self, message, line):
        """ Recieved an XML error, highlight the line and jump to it """
        # Print error in console with link
        if line > 0:
            self.stdErrCallback(QString('&nbsp;&nbsp;<a href="line_%1">%2</a>').arg(line).arg(message))
            if self.xmlEditor:
                # Highlight error
                self.status('Error: ' + message)
                self.gotoXmlLine(line)
                self.xmlEditor.highlightCurrentLine()
                self.ui.tabWidget.setCurrentIndex(0)
        else:
            self.stdErrCallback(message)

    def showHelp(self):
        """ Show the help documentation in a webview popup """
        help = QDialog(self)
        help.ui = ui_help.Ui_Help()
        help.ui.setupUi(help)
        help.exec_()

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
    
    def deleteTabs(self):
        self.textEditors = []
        self.ui.tabWidget.clear()

    def clearConsole(self):
        self.ui.textConsole.clear()
    
    def openFile(self):
        """ Add one or more files to the queue """
        # Request file names with dialog
        self.status.push('Adding a new file')
        last = self.input_file or QDesktopServices.storageLocation(QDesktopServices.HomeLocation)
        filename = QFileDialog.getOpenFileName(self, 'Select an XML document to convert', \
                                               last, 'XML Files (*.xml)')
        self.status.pop()
        if filename:
            self.deleteTabs()
            self.clearConsole()
            self.viewDocument(self.handler.XML, filename)
            self.input_file = str(filename)
            self.ui.sourceLabel.setText(filename)

    def xmlChanged(self):
        if self.xmlEditor and not self.xmlEditor.isReadOnly():
            self.ui.tabWidget.setTabText(0, 'XML *')
            # Enable the action
            self.ui.actionSave.setEnabled(True)
            self.xml_modified = True

    def saveFile(self):
        """ Saves the current source document back to its original path """
        if self.xmlEditor:
            if os.access(self.input_file, os.W_OK):
                self.ui.tabWidget.setTabText(0, 'XML')
                # Disable the action
                self.ui.actionSave.setEnabled(False)
                self.xml_modified = False
                # Write the file
                file = open(self.input_file, 'w')
                file.write(self.xmlEditor.toPlainText())
                file.close()
                self.status('Wrote file ' + self.input_file)
            else:
                QMessageBox.critical(self, 'Unable to save', 'You don\'t have '
                                     'permission to write to the file "%s"' \
                                     % self.input_file)

    def convert(self):
        if not self.input_file or not os.path.exists(self.input_file):
            QMessageBox.critical(self, 'Could not convert',
                                 'You must first select a source document.')
            return
        if self.xml_modified:
            q =  QMessageBox.question(self, 'XML modified', 'You have modified the '
                                 'source document since it was last saved.  Do '
                                 'you want to save or discard your changes?',
                                 'Save', 'Discard', 'Cancel')
            if q == 0:
                self.saveFile()
            elif q == 2:
                return
            else:
                # Discard XML changes -- Occurs automatically through recreating the editor after deleting tabs
                self.xmlModified = False

        if self.settings.verify():
            # Clear preview tabs and console
            self.deleteTabs()
            self.clearConsole()
            self.viewDocument(self.handler.XML, self.input_file)
            self.status('Converting document ' + self.input_file)

            # Prepare parameters for conversion
            output_dir = str(self.settings.value('conversion/outputDir').toString())
            if output_dir:
                output_dir = os.path.normpath(os.path.expanduser(output_dir))  
            
            formats = [key for key, val in \
              { self.handler.PAGED: self.ui.formatPaged.checkState(),
                self.handler.RAW:   self.ui.formatRaw.checkState(),
                self.handler.HTML:  self.ui.formatHtml.checkState(),
                self.handler.NROFF: self.ui.formatNroff.checkState() }.items() \
              if val]
            
            # Setup backend thread with current state of settings
            verbose = bool(self.ui.actionOptionVerbose.isChecked())
            abs_cache = os.path.expanduser(str(self.settings.value('cache/location').toString()))
            local_libs = str(self.settings.value('references/local_libs').toString())
            network_lib = str(self.settings.value('references/network_lib').toString())
            self.handler.setCache(abs_cache)
            self.handler.setLocalLibraries(local_libs)
            self.handler.setNetworkLibrary(network_lib)
            self.handler.setVerbose(verbose)

            if len(formats) > 0:
                self.lockWidgets()
                self.handler.convert(self.input_file, formats, output_dir)
            else:
                QMessageBox.critical(self, 'Could not convert',
                                    'You must select at least one output format.')

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
