# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/help.ui'
#
# Created: Mon Oct 17 19:13:28 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Help(object):
    def setupUi(self, Help):
        Help.setObjectName(_fromUtf8("Help"))
        Help.resize(796, 689)
        self.verticalLayout = QtGui.QVBoxLayout(Help)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.webView = QtWebKit.QWebView(Help)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("qrc:/doc/gui.html")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.verticalLayout.addWidget(self.webView)

        self.retranslateUi(Help)
        QtCore.QMetaObject.connectSlotsByName(Help)

    def retranslateUi(self, Help):
        Help.setWindowTitle(QtGui.QApplication.translate("Help", "xml2rfc Documentation", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
