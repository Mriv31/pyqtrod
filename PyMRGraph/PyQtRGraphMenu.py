# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen



class PyQtRGraphMenu(QtWidgets.QMenu):
    # Creates a menu for graph and pass the right plot and right ds to submenu functions.
    def __init__(self,title,parent,plot):
        super(PyQtRGraphMenu, self).__init__(title,parent)
        self.plot = plot
        self.addMenu(RDSMenu("Datasets",self,plot))
        self.addMenu(RPlotMenu("Plots",self,plot))


