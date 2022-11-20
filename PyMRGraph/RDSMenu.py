# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen
from .RPlotMenu import RPlotMenu
from .ActionStyle import MenuStyler


class RDSMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,plot):
        super(RDSMenu, self).__init__(title,parent)
        list_dataset_action = QtGui.QAction("List datasets",self)
        list_dataset_action.triggered.connect(plot.list_data_set)

        self.addAction(list_dataset_action)
        styler = MenuStyler(self)
        styler.setColor("List datasets", QtGui.QColor("#3D6BC4"))


