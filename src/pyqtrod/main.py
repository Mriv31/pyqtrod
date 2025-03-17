# This Python file uses the following encoding: utf-8
import sys
import importlib.resources as pkg_resources
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMessageBox

from .ni_file import NIfile
from .ni_tab import NITab
from .plot_tab import PlotTab
from pynavgui import PngPlotRegionMenu
from pynavgui import PngInstance
from .ni_foldertab import NIFolderTab
from .helpers.batch_analysis import (
    compute_all_phi,
    compute_all_speeds,
)
import os

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
        self.menuFile.addAction("Batch compute speed", self.speed_folder)
        self.menuFile.addAction("Show phase and signal", self.show_phase_versus_signal)

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

    def PhiFolder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", "")
        if path == ("", ""):
            return
        compute_all_phi(path)
        return

    def speed_folder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", "")
        if path == ("", ""):
            return
        compute_all_speeds(path, threadpool=self.threadpool)
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
        if self.png_instance.active_plot_region is None:
            QMessageBox.critical(None, "Error", "No plot region selected.")
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

    def show_phase_versus_signal(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", "")
        if path == ("", ""):
            return
        file_list = os.listdir(path)
        for f in file_list:
            print(f)
            if f.endswith("smooth_points.npy"):
                newtab = PlotTab(os.path.join(path, f), png_instance=self.png_instance)
                if f.split("_")[0] + "_avg_signal.npy" in file_list:
                    newtab.add_data(
                        os.path.join(path, f.split("_")[0] + "_avg_signal.npy"),
                        "avg_signal",
                    )
                self.FileTab.addTab(newtab, f)

    def open_all_phiu(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", "")
        if path == ("", ""):
            return
        file_list = os.listdir(path)
        file_list_to_open = []
        for f in file_list:
            print(f)
            if f.endswith("phiu.npy"):
                file_list_to_open.append(f)
        file_list_to_open = [os.path.join(path, f) for f in file_list_to_open]
        file_list_failed = []
        for f in file_list_to_open:
            try:
                newtab = PlotTab(
                    f,
                    png_instance=self.png_instance,
                    rad_to_degree=True,
                    xArrayLinSorted=True,
                )
                self.FileTab.addTab(newtab, f)
            except Exception as e:
                print(e)
                file_list_failed.append(f)
        if file_list_failed:
            error_message = (
                "The following files encountered errors during processing:\n"
            )
            error_message += "\n".join(file_list_failed)
            QMessageBox.critical(None, "Processing Errors", error_message)
        else:
            QMessageBox.information(
                None, "Success", "All files processed successfully."
            )
        return


def main():
    app = QtWidgets.QApplication(["PyQtRod"])

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
