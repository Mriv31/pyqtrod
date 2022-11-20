# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen
from .RDSMenu import RDSMenu
from .RPlotMenu import RPlotMenu




class PyTabGraphMenu(QtWidgets.QMenu):
    #Class of menu to be added in any window which has a PyQtRGraph and a method get_current_PyQtRGraph
    def __init__(self,title,window):
        self.window = window
        super(PyTabGraphMenu, self).__init__(title,window)
        #self.aboutToHide.connect(self.clear)
        self.aboutToShow.connect(self.create_graph_menu)

    def create_graph_menu(self):
        self.clear()
        w = self.window.get_current_active_widget()
        print(w.__class__.__name__ )
        if w.__class__.__name__ == "PyQtGraphGrid":
            w = w._cur_active_w
        print(w.__class__.__name__ )
        if w.__class__.__name__ == "PyQtRPlot":
            self.addMenu(RDSMenu("Cur. Dataset",self,w))
            self.addMenu(RPlotMenu("Cur. Plot",self,w))
        else:
            action = QtGui.QAction("No editable graph selected",self)
            action.setEnabled(False)
            self.addAction(action)
        self.show()

