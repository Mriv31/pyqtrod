# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
sys.path.insert(0, './Modules')
sys.path.insert(0, './Helpers')

from NIfile import NIfile
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThreadPool, QCoreApplication, Qt, QPointF, QSize
from PyQt6.QtCharts import QChartView, QChart, QScatterSeries, QLineSeries
from PyQt6.QtGui import QPolygonF, QIcon
import numpy as np
import ctypes
import time
from NITab import NITab
from PlotTab import PlotTab
from PyMRGraph import *

from NIFolderTab import NIFolderTab
from threading import Thread
QT_API = "pyqt6"
from pyqtgraph.console import ConsoleWidget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('form.ui', self)
        self.setWindowTitle("PyQtRod")
        self.threadpool = QThreadPool()
        self.menubar.addMenu(PyTabGraphMenu("Graph menu",self))




    def loadTDMS(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open a file', '','TDMS files (*.tdms)')
        if path == ('', ''):
            return
        NIf = NIfile(path[0]);
        newtab = NITab(NIf,self.threadpool);
        self.FileTab.addTab(newtab,path[0])
        self.FileTab.setCurrentWidget(newtab)

        return

    def SumFolder(self):

        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder', '')
        if path == ('', ''):
            return
        newtab = NIFolderTab(path);
        self.FileTab.addTab(newtab,path)
        return

    def OpenFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open a file', '','TDMS files (*.npy)')
        if path == ('', ''):
            returnNITab
        newtab = PlotTab(path[0]);
        self.FileTab.addTab(newtab,path[0])
        self.FileTab.setCurrentWidget(newtab)
        return


    def get_current_active_widget(self):
        cw = self.FileTab.currentWidget().get_current_active_widget()
        return cw

if __name__ == "__main__":

    app = QtWidgets.QApplication(['PyQtRod'])

    window = MainWindow()



    window.show()



    sys.exit(app.exec())
