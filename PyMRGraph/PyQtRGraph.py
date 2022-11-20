# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
from .PyQtRPlot import PyQtRPlot



class PyQtRGraph(QtWidgets.QWidget):
    def __init__(self,**kwargs):
        #pg.setConfigOption('useOpenGL', 0)
        super(PyQtRGraph, self).__init__()

        hbox = QtWidgets.QHBoxLayout()
        self.plotl=[]
        self.plot_inc = 0


        self.graphstatusbar = QtWidgets.QLabel()

        #Future emplacement for buttons
        buttonw = QtWidgets.QWidget()
        self.vbox = QtWidgets.QVBoxLayout()
        buttonw.setLayout(self.vbox)

        hbox.addWidget(buttonw)

        #plotc widget for plot and title bar
        plotc = QtWidgets.QWidget()
        self.plotvbox = QtWidgets.QVBoxLayout()
        plotc.setLayout(self.plotvbox)

        self.plotvbox.addWidget(self.graphstatusbar)
        self.tab = QtWidgets.QTabWidget()
        self.plotvbox.addWidget(self.tab)


        hbox.addWidget(plotc)


        self.setLayout(hbox)

        self.add_plot(**kwargs)


    def add_plot(self,**kwargs):

        ploth = PyQtRPlot(parentgraph=self,**kwargs)
        self.plotl.append(ploth)
        ploth.parentgraph = self

        if "name" in kwargs:
            plotname = kwargs["name"]
        else:
            plotname = "plot" + str(self.plot_inc)
            self.plot_inc += 1

        self.tab.addTab(ploth,plotname)
        self.tab.setCurrentWidget(ploth)

    def remove_plot(self,ploth):
        self.plotl.remove(ploth)
        self.tab.removeTab(self.tab.indexOf(ploth))
        del(ploth)

    def remove_active_plot(self):
        ploth = self.currentWidget()
        if ploth == 0:
            return
        self.plotl.remove(ploth)
        self.tab.removeTab(self.tab.indexOf(ploth))
        del(ploth)

    def get_current_plot(self):
        return self.currentWidget()



    def __del__(self):
        for p in self.plotl:
            del(p)


