# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
from .PyQtRGraph import PyQtRGraph




class PyQtGraphGrid(QtWidgets.QWidget):
    def __init__(self,title=""):
        super(PyQtGraphGrid, self).__init__()
        self.layout = QGridLayoutHWFixed()
        self.setLayout(self.layout)
        self.layout.addWidget(QtWidgets.QLabel(title),0,0,1,-1)
        self.nexti = 1
        self.nextj = 0
        self.setMinimumSize(500, 500)
        self._cur_active_w = None
        pass

    def addGridWidget(self,w):
        self.layout.addWidget(w,self.nexti,self.nextj)
        self.increment_grid()

    def addPlot(self,*args,**kwargs):
        newplotgraph = PyQtRGraph(*args,parentgrid=self, **kwargs)
        newplot = newplotgraph.plotl[-1]
        self.layout.addWidget(newplotgraph,self.nexti,self.nextj)
        self.increment_grid()
        return newplot

    def set_cur_graph(self,w):
        self._cur_active_w = w

    def addScatterPlot(self,*args,**kwargs):
        newplot = PyQtRGraph(*args, **kwargs,pen=None, symbol='o',symbolPen='red',symbolBrush='red',symbolSize=0.005,pxMode=False)
        self.layout.addWidget(newplot,self.nexti,self.nextj)

        self.increment_grid()
        return newplot

    def addImage(self,im):
        imv = pg.ImageView()
        imv.setImage(im)
        self.layout.addWidget(imv,self.nexti,self.nextj)
        self.increment_grid()
        return imv


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








