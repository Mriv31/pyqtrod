# This Python file uses the following en =oding: utf-8

from PyQt6 import QtWidgets
from PyMRGraph import *

import numpy as np
from PyQtFunc import *


class PlotTab(QtWidgets.QMainWindow):
    def __init__(self,file):
        super(PlotTab, self).__init__()
        self.nexti = 0
        self.nextj = 0

        self.file = file

        self.maxcol = 1
        w = PyQtGraphGrid(title=file)
        self.setCentralWidget(w)
        self.w = w
        if (file.endswith('.npy')):

            data = np.load(file)
            if len(data.shape) == 2:
                if(data.shape[0] == 2):
                    x = data[0,:]
                    y = data[1,:]
                elif(data.shape[1] == 2):
                    x = data[:,0]
                    y = data[:,1]
                else:
                    print("Format not supported 2 "+str(data.shape[0])+" "+str(data.shape[1]))
                    return
            elif len(data.shape) == 1:
                y = data
                x = np.arange(len(data),dtype=np.float64)
            else:
                print("Format not supported 1")
                return
            g = w.addScatterPlot(x=x,y=y)


        elif (file.endswith('.npz')):
            graph = PyQtRGraph(file=file,parentgrid=w)
            w.addGridWidget(graph)
        pass

    def get_current_active_widget(self):

        return self.w


