# coding=utf-8
# -*- coding: utf-8 -*-

import sys, threading
import matplotlib

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import ui, aco


class ApplicationWindow(QMainWindow, ui.Ui_Frame):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.is_ready = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_func)
        self.is_running = False
        self.algorithm = aco.aco("./conf.json", self.IterationBox.value(),
                                 self.AntNumBox.value(),
                                 self.DecayRateBox.value(),
                                 self.IncreaseBox.value())
        self.Nurseinfo = "Nurse\nNo1:\t%d\nNo2:\t%d\nNo3:\t%d \tTotal:\t%d" % (
        self.algorithm.HnurseNum, self.algorithm.MnurseNum, self.algorithm.LnurseNum, self.algorithm.nurseNum)
        self.OTinfo = "OperatingTheatre\nHighOT\t%d\nLowOT\t%d \tTotal:\t%d" % (
        self.algorithm.HOT, self.algorithm.LOT, self.algorithm.OTNum)
        self.Nurse.setText(self.Nurseinfo)
        self.OT.setText(self.OTinfo)
        self.is_ready = True
        self.RunButton.clicked.connect(self.RunButtonClicked)
        self.StopButton.clicked.connect(self.StopButtonClicked)
        self.SaveDataButton.clicked.connect(self.SaveDataButtonClicked)
        self.SaveImageButton.clicked.connect(self.SaveImageButtonClicked)
        self.IterationBox.valueChanged.connect(self.IterationBoxValueChanged)
        self.AntNumBox.valueChanged.connect(self.AntNumBoxValueChanged)
        self.DecayRateBox.valueChanged.connect(self.DecayRateBoxValueChanged)
        self.IncreaseBox.valueChanged.connect(self.IncreaseBoxValueChanged)

        def dragEnterEvent(self, event):
            self.algorithm = aco.aco(event.mimeData().text()[7:], self.IterationBox.value(),
                                     self.AntNumBox.value(),
                                     self.DecayRateBox.value(),
                                     self.IncreaseBox.value())
            self.Nurseinfo = "Nurse\nNo1:\t%d\nNo2:\t%d\nNo3:\t%d \tTotal:\t%d" % (
                self.algorithm.HnurseNum, self.algorithm.MnurseNum, self.algorithm.LnurseNum, self.algorithm.nurseNum)
            self.OTinfo = "OperatingTheatre\nHighOT\t%d\nLowOT\t%d \tTotal:\t%d" % (
                self.algorithm.HOT, self.algorithm.LOT, self.algorithm.OTNum)
            self.Nurse.setText(self.Nurseinfo)
            self.OT.setText(self.OTinfo)
            self.is_ready = True

    def update_func(self):
        self.progressBar.setValue(self.algorithm.rate)

        if (self.algorithm.rate == 100):
            self.timer.stop()
            self.is_running = False
            self.algorithm.drawImg()
            self.Image.setPixmap(QtGui.QPixmap("./src/results.png"))
            self.FinalScoreBox.setText(str(self.algorithm.bestScore[0][-1])[:4])

    def RunButtonClicked(self):
        if self.is_running:
            QMessageBox.information(self, "Running", "Programming is running, please wait!", QMessageBox.Yes)
        else:
            if self.is_ready:
                self.timer.start(100)
                self.t = threading.Thread(target=self.algorithm.run)
                self.t.setDaemon(True)
                self.t.start()
                self.is_running = True
            else:
                QMessageBox.information(self, "Error", "Data not loaded!", QMessageBox.Yes)

    def StopButtonClicked(self):
        pass

    def SaveDataButtonClicked(self):
        self.algorithm.saveData()
        QMessageBox.information(self, "Save data", "Data have been saved into output.csv", QMessageBox.Yes)

    def SaveImageButtonClicked(self):
        QMessageBox.information(self, "Save image", "Data have been saved into results.png", QMessageBox.Yes)
        self.algorithm.drawImg("./results.png")

    def IterationBoxValueChanged(self):
        self.algorithm.iteratorNum = self.IterationBox.value()

    def AntNumBoxValueChanged(self):
        self.algorithm.antNum = self.AntNumBox.value()

    def DecayRateBoxValueChanged(self):
        self.algorithm.decayRate = self.DecayRateBox.value()

    def IncreaseBoxValueChanged(self):
        self.algorithm.inceaseRate = self.IncreaseBox.value()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    mw = ApplicationWindow()
    mw.show()
    App.exit()
    sys.exit(App.exec_())
