# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen

class PyQtGraph(QtWidgets.QWidget):
    def __init__(self,x,y,title="",xtitle="",ytitle="",logx=0,logy=0):
        super(PyQtGraph, self).__init__()

        self.x = x
        self.y = y
        self.x.flags.writeable = False #locks displayed array to find them later
        self.y.flags.writeable = False #locks displayed array to find them later
        self.title=""
        self.xtitle=""
        self.ytitle=""
        self.ploth= pg.PlotWidget(title=title)
        self.ploth.enableAutoRange(True, True)
        self.ploth.plot(x,y) #,pen=None,symbol='o',symbolSize=0.01,pxMode=False) #,symbolPen=mkPen("r"
        self.ploth.setLabel('left',ytitle)
        self.ploth.setLabel('bottom',xtitle)
        self.ploth.setLogMode(logx,logy)




class PyQtGraphGrid(QtWidgets.QWidget):
    def __init__(self,title=""):
        super(PyQtGraphGrid, self).__init__()
        self.layout = QGridLayoutHWFixed()
        self.setLayout(self.layout)


        self.layout.addWidget(QtWidgets.QLabel(title),0,0,1,-1)
        self.nexti = 1
        self.nextj = 0

        self.setMinimumSize(500, 500)
        pass

    def addGridWidget(self,w):
        self.layout.addWidget(w,self.nexti,self.nextj)
        self.increment_grid()

    def addPlot(self,*args,**kwargs):
        newplot = PyQtGraph(*args, **kwargs)
        self.layout.addWidget(newplot.ploth,self.nexti,self.nextj)

        self.increment_grid()

    def increment_grid(self):
        if self.nextj >= self.nexti:
            self.nextj=0
            self.nexti+=1
        else:
            self.nextj+=1


class QGridLayoutHWFixed(QtWidgets.QGridLayout):
    def __init__(self,title=""):
        super(QGridLayoutHWFixed, self).__init__()
    def heightForWidth(self,w):
        return w
    def hasHeightForWidth(self):
        return True










