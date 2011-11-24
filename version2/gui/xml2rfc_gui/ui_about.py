# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/about.ui'
#
# Created: Wed Nov 23 16:40:25 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(600, 340)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(600, 340))
        Dialog.setMaximumSize(QtCore.QSize(600, 340))
        Dialog.setCursor(QtCore.Qt.ArrowCursor)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(False)
        self.horizontalLayout = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(192, 192))
        self.label.setMaximumSize(QtCore.QSize(192, 192))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/assets/xml2rfc.png")))
        self.label.setScaledContents(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.frame = QtGui.QFrame(Dialog)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.xml2rfc_version = QtGui.QLabel(self.frame)
        self.xml2rfc_version.setStyleSheet(_fromUtf8("font-family:\'Verdana\'; font-size:11pt; color:#888888;"))
        self.xml2rfc_version.setAlignment(QtCore.Qt.AlignCenter)
        self.xml2rfc_version.setObjectName(_fromUtf8("xml2rfc_version"))
        self.verticalLayout.addWidget(self.xml2rfc_version)
        self.xml2rfc_gui_version = QtGui.QLabel(self.frame)
        self.xml2rfc_gui_version.setStyleSheet(_fromUtf8("font-family:\'Verdana\'; font-size:11pt; color:#888888;"))
        self.xml2rfc_gui_version.setAlignment(QtCore.Qt.AlignCenter)
        self.xml2rfc_gui_version.setObjectName(_fromUtf8("xml2rfc_gui_version"))
        self.verticalLayout.addWidget(self.xml2rfc_gui_version)
        spacerItem = QtGui.QSpacerItem(0, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.line = QtGui.QFrame(self.frame)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        spacerItem1 = QtGui.QSpacerItem(0, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setStyleSheet(_fromUtf8("font-family:\'Verdana\'; font-size:12pt; color:#202020;"))
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "About xml2rfc", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Verdana\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:48pt; color:#364f5f;\">xml2rfc</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.xml2rfc_version.setText(QtGui.QApplication.translate("Dialog", "Core version 0.0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.xml2rfc_gui_version.setText(QtGui.QApplication.translate("Dialog", "GUI version 0.0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Verdana\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">xml2rfc is a tool for validating and converting XML RFC documents to various formats.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copyright © The IETF Trust 2011, All Rights Reserved</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://tools.ietf.org\"><span style=\" text-decoration: underline; color:#0000ff;\">http://tools.ietf.org</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import assets_rc
