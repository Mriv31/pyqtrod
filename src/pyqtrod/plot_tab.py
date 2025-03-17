# This Python file uses the following en =oding: utf-8

from PyQt6 import QtWidgets
from pynavgui import PngPlotRegionGrid, PngPlotRegion

import numpy as np
import os


class PlotTab(QtWidgets.QMainWindow):

    def __init__(
        self, file, png_instance=None, rad_to_degree=False, xArrayLinSorted=False
    ):
        super(PlotTab, self).__init__()
        self.nexti = 0
        self.nextj = 0
        self.png_instance = png_instance
        self.file = file
        self.pr = None
        self.maxcol = 1
        w = PngPlotRegionGrid(title=file, png_instance=self.png_instance)
        self.setCentralWidget(w)
        self.w = w
        self.add_data(
            file, rad_to_degree=rad_to_degree, xArrayLinSorted=xArrayLinSorted
        )

    def add_data(self, file, rad_to_degree=False, xArrayLinSorted=False):
        w = self.w
        if file.endswith(".npy"):
            data = np.load(file)
            if len(data.shape) == 2:
                if data.shape[0] == 2:
                    x = data[0, :]
                    y = data[1, :]
                elif data.shape[1] == 2:
                    x = data[:, 0]
                    y = data[:, 1]
                else:
                    print(
                        "Format not supported 2 "
                        + str(data.shape[0])
                        + " "
                        + str(data.shape[1])
                    )
                    return
            elif len(data.shape) == 1:
                y = data
                x = np.arange(len(data), dtype=np.float64)
            else:
                print("Format not supported 1")
                return
            # if self.png_instance.active_plot is None:
            if rad_to_degree:
                y = np.degrees(y)
            if self.pr is None:
                self.pr = w.addScatterPlot(
                    x=x,
                    y=y,
                    name=os.path.basename(file),
                    xArrayLinSorted=xArrayLinSorted,
                )
            else:
                self.pr.plotl[-1].add_ds(x=x, y=y, xArrayLinSorted=xArrayLinSorted)
            # else:
            #     self.png_instance.active_plot.add_ds(x=x, y=y)

        elif file.endswith(".npz"):  # This will always create a new graph
            graph = PngPlotRegion(file=file, parentgrid=w)
            w.addGridWidget(graph)
        pass

    def get_current_active_widget(self):
        return self.w
