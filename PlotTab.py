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
        #self.layout = QtWidgets.QGridLayout()

        #self.scrolled = QtWidgets.QScrollArea()

        #widget = QtWidgets.QWidget()
        #widget.setLayout(self.layout)
        #self.setCentralWidget(widget)
        #self.scrolled.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        #self.scrolled.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #self.scrolled.setWidgetResizable(True)
        #self.scrolled.setWidget(widget)
        self.maxcol = 1
        w = PyQtGraphGrid(title=file)
        self.setCentralWidget(w)
        self.w = w
        #self.layout.addWidget(w,0,0)
#        data = np.load(file)
#        if len(data.shape) == 2:
#            if(data.shape[1] == 2):
#                x = data[0,:]
#                y = data[1,:]
#        else:
#            y = data[:]
#            x = np.arange(len(data[:]))

        #g = w.addScatterPlot(x=x,y=y)
        #g.add_plot(x=x,y=x)
        graph = PyQtRGraph(file=file,parentgrid=w)
        w.addGridWidget(graph)
        pass

    def get_current_active_widget(self):

        return self.w


