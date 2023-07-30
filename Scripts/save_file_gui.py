# -*- coding: utf-8 -*-
# -*- Save File Dialog GUI -*-
# -*- Bibian Robert -*-
# -*- Geog 489 Final Project -*-

# Form implementation generated from reading ui file 'saveFile_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 299)
        Dialog.setAutoFillBackground(False)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.newOutputFileLE = QtWidgets.QLineEdit(Dialog)
        self.newOutputFileLE.setObjectName("newOutputFileLE")
        self.gridLayout.addWidget(self.newOutputFileLE, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.newOutputFileBrowseTB = QtWidgets.QToolButton(Dialog)
        self.newOutputFileBrowseTB.setObjectName("newOutputFileBrowseTB")
        self.gridLayout_2.addWidget(self.newOutputFileBrowseTB, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Save file"))
        self.label.setText(_translate("Dialog", "Output File name: "))
        self.newOutputFileBrowseTB.setToolTip(_translate("Dialog", "Click to browse output file "))
        self.newOutputFileBrowseTB.setText(_translate("Dialog", "..."))

