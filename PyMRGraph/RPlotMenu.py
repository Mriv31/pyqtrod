# This Python file uses the following encoding: utf-8
from PyQt6 import QtWidgets, QtGui
from .ActionStyle import MenuStyler



class DsSelectMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,plot):
        super(DsSelectMenu, self).__init__(title,parent)
        for ds in plot.dsl:
            action = QtGui.QAction(ds.prop["name"],self)
            action.triggered.connect(lambda _,y=ds: plot.set_active_dataset(y))
            self.addAction(action)
        styler = MenuStyler(self)

        for ds in plot.dsl:
            if ds.prop['pen'] is not None:
                styler.setColor(ds.prop['name'],ds.prop['pen'])
            elif ds.prop['symbolPen'] is not None:
                styler.setColor(ds.prop['name'], ds.prop['symbolPen'])
            else:
                styler.setColor(ds.prop['name'], "k")



class RPlotMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,plot):
        super(RPlotMenu, self).__init__(title,parent)

        remove_active_plot = QtGui.QAction("Remove active plot",self)
        remove_active_plot.triggered.connect(plot.del_from_graph)
        self.addAction(remove_active_plot)

        self.addMenu(DsSelectMenu("Select active data set",self,plot))

