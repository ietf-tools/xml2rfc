# Python libs
import os.path

# PyQT modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# UI modules
import ui_preferences

# My modules
import utils
import xml2rfc

# Determine safe path defaults
default_network_lib = 'http://xml.resource.org/public/rfc/'
default_local_libs = os.environ.get('XML_LIBRARY', '/usr/share/xml2rfc')
default_cache_path = os.path.normpath('/var/cache/xml2rfc:')
if not os.access(default_cache_path, os.W_OK):
    try:
        os.makedirs(default_cache_path)
    except OSError:
        # Default to homedir
        default_cache_path = os.path.normpath(os.path.expanduser('~/.cache/xml2rfc'))

class Settings(QSettings):
    """ Settings class which encapsulates QSettings with QDialogs """
    # Default settings
    defaults = {}
    defaults['conversion/outputDir']                = ''
    defaults['conversion/verbose']                  = False
    defaults['appearance/previewFontFamily']        = 'Courier'
    defaults['appearance/previewFontSize']          = 12
    defaults['appearance/previewLineNumbersXml']    = True
    defaults['appearance/previewLineNumbersText']   = False
    defaults['appearance/consoleFontFamily']        = 'Courier'
    defaults['appearance/consoleFontSize']          = 12
    defaults['cache/location']                      = default_cache_path
    defaults['references/local_libs']               = default_local_libs
    defaults['references/network_lib']              = default_network_lib

    def __init__(self, mainWindow, backendHandler):
        # Super
        QSettings.__init__(self, 'Concentric Sky', 'xml2rfc')
        self.mainWindow = mainWindow    # Reference to parent
        self.handler = backendHandler
        
        # Setup preference window
        self.dialog = QDialog(self.mainWindow)
        self.dialog.ui = ui_preferences.Ui_Dialog()
        self.dialog.ui.setupUi(self.dialog)
        
        # Hash that stores temporary settings as python str -> QVariant
        # This is used during the dialog interaction
        self.temp = {}  
            
        # Guarentee that we are in a safe namespace
        self.beginGroup('com/xml2rfc')
        
        # Fill in any defaults
        self.populateDefaults()
        
        # Apply loaded settings to main window
        self.applyStaticSettings()                      
    
    def applyStaticSettings(self):
        """ Applys any static settings to mainwindow ui elements """
        # Appearance settings
        self.beginGroup('appearance')
        
        # Text views
        previewFont    = QFont(self.value('previewFontFamily').toString(),
                               self.value('previewFontSize').toInt()[0])
        xmlLineNumbers = self.value('previewLineNumbersXml').toBool()
        textLineNumbers = self.value('previewLineNumbersXml').toBool()
        for editor in self.mainWindow.textEditors:
            editor.enableLineNumbers = textLineNumbers
            editor.setFont(previewFont)
            editor.update()
        if self.mainWindow.xmlEditor:
            self.mainWindow.xmlEditor.enableLineNumbers = xmlLineNumbers
            self.mainWindow.xmlEditor.update()

        # Console outputs
        consoleFont = QFont(self.value('consoleFontFamily').toString(),
                            self.value('consoleFontSize').toInt()[0])
        self.mainWindow.ui.textConsole.setFont(consoleFont)

        self.endGroup()  # End appearance settings

        # Menus
        verbose = self.value('conversion/verbose').toBool()
        self.mainWindow.ui.actionOptionVerbose.setChecked(verbose)
        
    def populateDefaults(self, force=False):
        # Iterate through settings and insert any missing values with defaults
        for key, val in Settings.defaults.items():
            if force or key not in self.allKeys():
                self.setValue(key, val)

    def destroy(self):
        # Pop namespace
        self.endGroup()
        
    def loadTemp(self):
        """ Loads QSettings into temp hash """
        self.temp = {}
        for key in self.allKeys():
            self.temp[str(key)] = self.value(key)
    
    def saveTemp(self):
        """ Saves temp hash to QSettings """
        for key, val in self.temp.items():
            self.setValue(QString(key), val)  # Assume val to be QVariant
            
    def setTempValue(self, key, val):
        """ Sets a temporary value as a QVariant """
        self.temp[key] = QVariant(val)
        
    def tempValue(self, key):
        """ Returns a QVariant from the temp hash, or an empty QVariant """
        return self.temp.get(key, QVariant())
    
    def updateLabels(self):
        """ Updates the labels on the dialog to reflect temp settings """
        # Conversion Tab
        outputDir = self.tempValue('conversion/outputDir').toString()
        self.dialog.ui.outputDir.setText(outputDir)

        # Appearance Tab
        pFontFamily = self.tempValue('appearance/previewFontFamily').toString()
        pFontSize   = self.tempValue('appearance/previewFontSize').toString()
        if pFontFamily and pFontSize:
            label = pFontFamily + ' ' + pFontSize
            self.dialog.ui.previewFontButton.setText(label)
        cFontFamily = self.tempValue('appearance/consoleFontFamily').toString()
        cFontSize   = self.tempValue('appearance/consoleFontSize').toString()
        if cFontFamily and cFontSize:
            label = cFontFamily + ' ' + cFontSize
            self.dialog.ui.consoleFontButton.setText(label)
        self.dialog.ui.previewLineNumbersXml.setChecked( \
            self.tempValue('appearance/previewLineNumbersXml').toBool())
        self.dialog.ui.previewLineNumbersText.setChecked( \
            self.tempValue('appearance/previewLineNumbersText').toBool())
        
        # Cache tab
        loc = self.tempValue('cache/location').toString()
        self.dialog.ui.cacheLocationText.setText(loc)
        fullpath = os.path.join(os.path.expanduser(str(loc)), 
                                xml2rfc.CACHE_PREFIX)
        kb = utils.getDirectorySize(fullpath) / 2 ** 10
        self.dialog.ui.cacheSizeLabel.setText(str(kb) + ' KB')
        
        # References tab
        locallibs = self.tempValue('references/local_libs').toString()
        netloc = self.tempValue('references/network_lib').toString()
        self.dialog.ui.localLibraries.setText(locallibs)
        self.dialog.ui.networkLibrary.setText(netloc)

    def showPreferences(self):
        """ Open the preferences dialog window """       
        self.dialog = QDialog(self.mainWindow)
        self.dialog.ui = ui_preferences.Ui_Dialog()
        self.dialog.ui.setupUi(self.dialog)

        # Populate temporary settings with current and update labels
        self.loadTemp()
        self.updateLabels()
        
        # Connect dialogue button callbacks
        for button, function in {
         self.dialog.ui.outputBrowse:           self.browseOutputDir,
         self.dialog.ui.outputClear:            self.clearOutputDir,
         self.dialog.ui.previewFontButton:      self.changePreviewFont,
         self.dialog.ui.consoleFontButton:      self.changeConsoleFont,
         self.dialog.ui.cacheBrowseButton:      self.browseCacheLocation,
         self.dialog.ui.cacheDeleteButton:      self.deleteCache,
         self.dialog.ui.cacheResetButton:       self.resetCacheLocation,
         self.dialog.ui.libraryBrowseButton:    self.browseLibraryLocation,
         self.dialog.ui.libraryResetButton:     self.resetLibraryLocation,
         self.dialog.ui.networkLibraryResetButton: self.resetNetworkLibraryLocation,
        }.items():
            self.connect(button, SIGNAL('clicked()'), function)

        self.connect(self.dialog.ui.buttonBox, \
             SIGNAL('clicked(QAbstractButton*)'), self.dialogButton)

        # Connect other dialog signals
        # Conversion tab
        self.connect(self.dialog.ui.outputDir, 
                     SIGNAL('textChanged(QString)'), self.outputDirChanged)

        # Appearance tab
        self.connect(self.dialog.ui.previewLineNumbersXml,
                     SIGNAL('stateChanged(int)'), self.enableLineNumbersXml)
        self.connect(self.dialog.ui.previewLineNumbersText,
                     SIGNAL('stateChanged(int)'), self.enableLineNumbersText)

        # References tab
        self.connect(self.dialog.ui.localLibraries, 
                     SIGNAL('textChanged(QString)'), self.libraryChanged)
        self.connect(self.dialog.ui.networkLibrary,
                     SIGNAL('textChanged(QString)'), self.networkLibraryChanged)

        # Open the dialog
        if self.dialog.exec_():
            self.saveTemp()
            self.applyStaticSettings()
        else:
            pass  # Discard temp settings

    def verify(self):
        """ Ensure safety on settings before invoking xml2rfc """
        self.loadTemp()

        # Check library directory
        lib = str(self.tempValue('library/location').toString())
        if not os.access(lib, os.R_OK) or len(os.listdir(lib)) == 0:
            if QMessageBox.question(self.dialog, 'Library location', \
                     'Your citation library location \'%s\' is either inaccessible '
                     'or does not exist.  This may affect xml2rfc\'s ability to '
                     'evaluate document references when parsing.  Would you '
                     'like to set the location now?' % lib, 
                     'No', 'Yes'):
                self.browseLibraryLocation()
                self.saveTemp()

        # Check output directory
        output_dir = str(self.tempValue('conversion/outputDir').toString())
        if output_dir:
            path = os.path.normpath(os.path.expanduser(output_dir))
            if not os.path.exists(path):
                if QMessageBox.question(self.dialog, 'New Directory', 'The specified '
                                        'output directory \'%s\' does not exist.  Should '
                                        'I create it now?' % path, 
                                        'No', 'Yes'):
                    try:
                        os.makedirs(path)
                    except OSError:
                        # Directory is not writable, try to set a new one
                        if QMessageBox.question(self.dialog, 'Invalid Directory',
                                                'You don\'t have permission to write '
                                                'to the specified outupt directory \'%s\'. '
                                                'Do you want to choose a new one?' % path,
                                                'No', 'Yes'):
                            self.browseOutputDir()
                            self.saveTemp()
                            return self.verify()
                        else:
                            return False
                else:
                    return False
            elif not os.access(path, os.W_OK):
                if QMessageBox.question(self.dialog, 'Invalid Directory',
                        'You don\'t have permission to write '
                        'to the specified outupt directory \'%s\'. '
                        'Do you want to choose a new one?' % path,
                        'No', 'Yes'):
                    self.browseOutputDir()
                    self.saveTemp()
                    return self.verify()
                else:
                    return False
        return True
    
# ------ UI CALLBACKS ------------------------------

    def dialogButton(self, button):
        # Restore defaults button
        if self.dialog.ui.buttonBox.standardButton(button) == \
            QDialogButtonBox.RestoreDefaults:
            if QMessageBox.question(self.dialog, 'Restore Defaults', \
                                 'Are you sure you want to restore all ' \
                                 'settings to their defaults?', 'No', 'Yes'):
                self.populateDefaults(force=True)
                self.loadTemp()
                self.updateLabels()
    
    def outputDirChanged(self, text):
        self.setTempValue('conversion/outputDir', text)

    def libraryChanged(self, text):
        self.setTempValue('references/local_libs', text)

    def networkLibraryChanged(self, text):
        self.setTempValue('references/network_lib', text)

    def clearOutputDir(self):
        self.setTempValue('conversion/outputDir', '')
        self.updateLabels()

    def browseOutputDir(self):
        dir = QFileDialog.getExistingDirectory(caption='Select output directory')
        if dir:
            if os.access(dir, os.W_OK):
                self.setTempValue('conversion/outputDir', dir)
                self.updateLabels()
            else:
                QMessageBox.critical(self.dialog, 'Error',
                                     'You don\'t have permission to write to '
                                     'this directory.')

    def enableLineNumbersXml(self, checked):
        self.setTempValue('appearance/previewLineNumbersXml', checked)
            
    def enableLineNumbersText(self, checked):
        self.setTempValue('appearance/previewLineNumbersText', checked)

    def changePreviewFont(self):
        current = QFont(self.temp.get('appearance/previewFontFamily', \
                        QVariant()).toString())
        newFont, ok = QFontDialog.getFont(current)
        if ok:
            self.setTempValue('appearance/previewFontFamily', newFont.family())
            self.setTempValue('appearance/previewFontSize', newFont.pointSize())
            self.updateLabels()

    def changeConsoleFont(self):
        current = QFont(self.temp.get('appearance/consoleFontFamily', \
                        QVariant()).toString())
        newFont, ok = QFontDialog.getFont(current)
        if ok:
            self.setTempValue('appearance/consoleFontFamily', newFont.family())
            self.setTempValue('appearance/consoleFontSize', newFont.pointSize())
            self.updateLabels()
        
    def resetNetworkLibraryLocation(self):
        self.setTempValue('references/network_lib', 
                          self.defaults['references/network_lib'])
        self.updateLabels()
            
    def resetLibraryLocation(self):
        self.setTempValue('references/local_libs', 
                          self.defaults['references/local_libs'])
        self.updateLabels()
    
    def browseLibraryLocation(self):
        dir = QFileDialog.getExistingDirectory(caption='Select library location')
        if dir:  # Clicked OK?
            if os.access(dir, os.R_OK):
                self.setTempValue('library/location', dir)
                self.updateLabels()
            else:
                QMessageBox.critical(self.dialog, 'Error',
                                     'You don\'t have permission to read from '
                                     'this directory.')

    def resetCacheLocation(self):
        self.setTempValue('cache/location', self.defaults['cache/location'])
        self.updateLabels()
    
    def browseCacheLocation(self):
        dir = QFileDialog.getExistingDirectory(caption='Select cache location')
        if dir:
            if os.access(dir, os.W_OK):
                if len(os.listdir(dir)) == 0 or \
                    QMessageBox.warning(self.dialog, 'Warning',
                                        'The directory you have selected is not'
                                        ' empty, are you sure this is correct?',
                                        'No', 'Yes'):
                    self.setTempValue('cache/location', dir)
                    self.updateLabels()
            else:
                QMessageBox.critical(self.dialog, 'Error',
                                     'You don\'t have permission to write to '
                                     'this directory.')

    def deleteCache(self):
        path = os.path.expanduser(str(self.tempValue('cache/location').toString()))
                                
        if QMessageBox.question(self.dialog, 'Delete Cache', \
                                'Are you sure you want to delete the ' \
                                'entire cache at ' + path + '?', 'No', 'Yes'):
            self.handler.deleteCache(path)
            self.updateLabels()

# ------- Persistent Settings from MainWindow ----------

    def setVerbose(self, yes):
        self.setValue('conversion/verbose', yes)
