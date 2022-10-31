# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from NIfile import NIfile
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThreadPool, QCoreApplication, Qt, QPointF, QSize
from PyQt6.QtCharts import QChartView, QChart, QScatterSeries, QLineSeries
from PyQt6.QtGui import QPolygonF, QIcon
import numpy as np
import ctypes
import time
from NITab import NITab
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



    def loadTDMS(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open a file', '','TDMS files (*.tdms)')
        if path == ('', ''):
            return
        NIf = NIfile(path[0]);
        newtab = NITab(NIf,self.threadpool);
        self.FileTab.addTab(newtab,path[0])
        return

    def SumFolder(self):

        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder', '')
        if path == ('', ''):
            return
        newtab = NIFolderTab(path);
        self.FileTab.addTab(newtab,path)
        return


if __name__ == "__main__":

    app = QtWidgets.QApplication(['PyQtRod'])
    #app.setApplicationName("PyQtRod")
    #QtWidgets.qApp.setApplicationName("PyQtRod")

    window = MainWindow()
    sys.path.insert(0, './Modules')


    window.show()



    sys.exit(app.exec())
