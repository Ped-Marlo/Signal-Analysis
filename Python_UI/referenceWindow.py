# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'referenceWindow.ui',
# licensing of 'referenceWindow.ui' applies.
#
# Created: Mon Jan 27 12:16:42 2020
#      by: PyQt5-uic  running on PyQt5 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(464, 502)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_10 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 2)
        self.fileSelect = QtWidgets.QListWidget(Dialog)
        self.fileSelect.setMaximumSize(QtCore.QSize(999999, 999999))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.fileSelect.setFont(font)
        self.fileSelect.setMouseTracking(True)
        self.fileSelect.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.fileSelect.setWordWrap(True)
        self.fileSelect.setObjectName("fileSelect")
        self.gridLayout.addWidget(self.fileSelect, 1, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 1)
        self.pushButtonTXT = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonTXT.sizePolicy().hasHeightForWidth())
        self.pushButtonTXT.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.pushButtonTXT.setFont(font)
        self.pushButtonTXT.setObjectName("pushButtonTXT")
        self.gridLayout.addWidget(self.pushButtonTXT, 2, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Select offset to loaded CDFs", None, -1))
        self.label_10.setText(QtWidgets.QApplication.translate("Dialog", "Select the reference CDFs", None, -1))
        self.fileSelect.setSortingEnabled(True)
        self.pushButton.setText(QtWidgets.QApplication.translate("Dialog", "Apply offset with CDFs", None, -1))
        self.pushButtonTXT.setText(QtWidgets.QApplication.translate("Dialog", "Apply offset with TXT", None, -1))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

