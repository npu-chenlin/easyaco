# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FinalScore(object):
    def setupUi(self, FinalScore):
        FinalScore.setObjectName("FinalScore")
        FinalScore.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(FinalScore)
        self.centralwidget.setObjectName("centralwidget")
        self.AntNumLable = QtWidgets.QLabel(self.centralwidget)
        self.AntNumLable.setGeometry(QtCore.QRect(200, 120, 63, 22))
        self.AntNumLable.setObjectName("AntNumLable")
        self.IterationBox = QtWidgets.QSpinBox(self.centralwidget)
        self.IterationBox.setGeometry(QtCore.QRect(320, 120, 47, 31))
        self.IterationBox.setMaximum(100000)
        self.IterationBox.setProperty("value", 100)
        self.IterationBox.setObjectName("IterationBox")
        self.IterationLable = QtWidgets.QLabel(self.centralwidget)
        self.IterationLable.setGeometry(QtCore.QRect(190, 180, 63, 22))
        self.IterationLable.setObjectName("IterationLable")
        self.AntNumBox = QtWidgets.QSpinBox(self.centralwidget)
        self.AntNumBox.setGeometry(QtCore.QRect(310, 180, 47, 31))
        self.AntNumBox.setMaximum(100000)
        self.AntNumBox.setProperty("value", 100)
        self.AntNumBox.setObjectName("AntNumBox")
        self.RunButton = QtWidgets.QPushButton(self.centralwidget)
        self.RunButton.setGeometry(QtCore.QRect(470, 180, 87, 31))
        self.RunButton.setObjectName("RunButton")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(310, 270, 113, 30))
        self.lineEdit.setObjectName("lineEdit")
        self.IterationLable_2 = QtWidgets.QLabel(self.centralwidget)
        self.IterationLable_2.setGeometry(QtCore.QRect(192, 270, 81, 22))
        self.IterationLable_2.setObjectName("IterationLable_2")
        FinalScore.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(FinalScore)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 27))
        self.menubar.setObjectName("menubar")
        FinalScore.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(FinalScore)
        self.statusbar.setObjectName("statusbar")
        FinalScore.setStatusBar(self.statusbar)

        self.retranslateUi(FinalScore)
        QtCore.QMetaObject.connectSlotsByName(FinalScore)

    def retranslateUi(self, FinalScore):
        _translate = QtCore.QCoreApplication.translate
        FinalScore.setWindowTitle(_translate("FinalScore", "MainWindow"))
        self.AntNumLable.setText(_translate("FinalScore", "Iteration"))
        self.IterationLable.setText(_translate("FinalScore", "AntNum"))
        self.RunButton.setText(_translate("FinalScore", "运行"))
        self.IterationLable_2.setText(_translate("FinalScore", "FinalScore"))


