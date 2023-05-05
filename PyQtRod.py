# This Python file uses the following encoding: utf-8
import sys
sys.path.insert(0, './Modules')
sys.path.insert(0, './Helpers')

from NIfile import NIfile
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThreadPool
from NITab import NITab
from PlotTab import PlotTab
from PyMRGraph import *
import PyMRGraph.shared as shared
from NIFolderTab import NIFolderTab
QT_API = "pyqt6"


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
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open a file', '','Npy files (*.npy)')
        if path == ('', ''):
            return
        newtab = PlotTab(path[0]);
        self.FileTab.addTab(newtab,path[0])
        self.FileTab.setCurrentWidget(newtab)
        return

    def saveAsNpz(self):
        if shared.active_graph == None:
            return
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save a file', '','Npz (*.npz)')
        if path == ('', ''):
            return
        print("saving" + path[0])
        shared.active_graph.save(path[0])

    def LoadNpz(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open a file', '','NPZ files (*.npz)')
        if path == ('', ''):
            return
        newtab = PlotTab(path[0]);
        self.FileTab.addTab(newtab,path[0])
        self.FileTab.setCurrentWidget(newtab)
        return


if __name__ == "__main__":

    app = QtWidgets.QApplication(['PyQtRod'])

    window = MainWindow()



    window.show()



    sys.exit(app.exec())
