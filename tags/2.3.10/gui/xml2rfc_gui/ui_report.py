# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/report.ui'
#
# Created: Tue Aug 16 18:32:01 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Report(object):
    def setupUi(self, Report):
        Report.setObjectName(_fromUtf8("Report"))
        Report.resize(404, 198)
        self.verticalLayout = QtGui.QVBoxLayout(Report)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(Report)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.pass_label = QtGui.QLabel(self.groupBox)
        self.pass_label.setStyleSheet(_fromUtf8("color: green;"))
        self.pass_label.setObjectName(_fromUtf8("pass_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.pass_label)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.syntax_label = QtGui.QLabel(self.groupBox)
        self.syntax_label.setStyleSheet(_fromUtf8("color: red"))
        self.syntax_label.setObjectName(_fromUtf8("syntax_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.syntax_label)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.validation_label = QtGui.QLabel(self.groupBox)
        self.validation_label.setStyleSheet(_fromUtf8("color: red"))
        self.validation_label.setObjectName(_fromUtf8("validation_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.validation_label)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(Report)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Report)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Report.close)
        QtCore.QMetaObject.connectSlotsByName(Report)

    def retranslateUi(self, Report):
        Report.setWindowTitle(QtGui.QApplication.translate("Report", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Report", "Document Summary", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Report", "Documents successfully converted:", None, QtGui.QApplication.UnicodeUTF8))
        self.pass_label.setText(QtGui.QApplication.translate("Report", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Report", "Documents with XML syntax errors:", None, QtGui.QApplication.UnicodeUTF8))
        self.syntax_label.setText(QtGui.QApplication.translate("Report", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Report", "Documents with DTD validation errors:", None, QtGui.QApplication.UnicodeUTF8))
        self.validation_label.setText(QtGui.QApplication.translate("Report", "0", None, QtGui.QApplication.UnicodeUTF8))

