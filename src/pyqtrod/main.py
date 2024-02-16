# This Python file uses the following encoding: utf-8
import sys
import importlib.resources as pkg_resources
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThreadPool

from .ni_file import NIfile
from .ni_tab import NITab
from .plot_tab import PlotTab
from pynavgui import PngPlotRegionMenu
from pynavgui import PngInstance
from .ni_foldertab import NIFolderTab


QT_API = "pyqt6"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        with pkg_resources.path("pyqtrod", "form.ui") as ui_path:
            uic.loadUi(ui_path, self)
        self.setWindowTitle("PyQtRod")
        self.threadpool = QThreadPool()
        self.png_instance = PngInstance()
        self.menubar.addMenu(
            PngPlotRegionMenu("Graph menu", self, png_instance=self.png_instance)
        )

    def loadTDMS(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open a file", "", "TDMS files (*.tdms)"
        )
        if path == ("", ""):
            return
        NIf = NIfile(path[0])
        newtab = NITab(NIf, self.threadpool, png_instance=self.png_instance)
        self.FileTab.addTab(newtab, path[0])
        self.FileTab.setCurrentWidget(newtab)

        return

    def SumFolder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", "")
        if path == ("", ""):
            return
        newtab = NIFolderTab(path, png_instance=self.png_instance)
        self.FileTab.addTab(newtab, path)
        return

    def OpenFile(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open a file", "", "Npy files (*.npy)"
        )
        if path == ("", ""):
            return
        newtab = PlotTab(path[0], png_instance=self.png_instance)
        self.FileTab.addTab(newtab, path[0])
        self.FileTab.setCurrentWidget(newtab)
        return

    def saveAsNpz(self):
        if PngInstance.active_plot_region is None:
            return
        path = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save a file", "", "Npz (*.npz)"
        )
        if path == ("", ""):
            return
        print("saving" + path[0])
        self.png_instance.active_plot_region.save(path[0])

    def LoadNpz(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open a file", "", "NPZ files (*.npz)"
        )
        if path == ("", ""):
            return
        newtab = PlotTab(path[0], png_instance=self.png_instance)
        self.FileTab.addTab(newtab, path[0])
        self.FileTab.setCurrentWidget(newtab)
        return


def main():
    app = QtWidgets.QApplication(["PyQtRod"])

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
