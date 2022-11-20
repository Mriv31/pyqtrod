# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen
from .ActionStyle import MenuStyler



class DsSelectMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,plot):
        super(DsSelectMenu, self).__init__(title,parent)
        for ds in plot.dsl:
            self.addAction(QtGui.QAction(ds.description,self))
        styler = MenuStyler(self)

        for ds in plot.dsl:
            styler.setColor(ds.description, ds.argplot["pen"])


class RPlotMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,plot):
        super(RPlotMenu, self).__init__(title,parent)

        remove_active_plot = QtGui.QAction("Remove active plot",self)
        remove_active_plot.triggered.connect(plot.del_from_graph)
        self.addAction(remove_active_plot)

        self.addMenu(DsSelectMenu("Select active data set",self,plot))

