# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen


class PyQtRds:
    def __init__(self,x,y,description="",dssource=None):
        self.dssource = dssource
        self.description = description
        self.x = x
        self.y = y
        self.x.flags.writeable = False #locks displayed array to find them later
        self.y.flags.writeable = False #locks displayed array to find them later
        self._plotitem = None
        self.argplot = None
    def setPlotItem(self,pltitem):
        self._plotitem = pltitem
    def clearPlotItem(self):
        self._plotitem
    def __del__():
        del(self.x,self.y)


class PyQtRGraph(QtWidgets.QWidget):
    def __init__(self,**kwargs):
        #pg.setConfigOption('useOpenGL', 0)
        super(PyQtRGraph, self).__init__()

        hbox = QtWidgets.QHBoxLayout()
        self.plotl=[]


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

    def add_plot(**kwargs):
        ploth = PyQtRPlot(**kwargs)
        self.plotl.append(ploth)
        ploth.addLegend()
        ploth.parentgraph = self

        self.tab.addTab(ploth,"Plot")
        self.tab.setCurrentWidget(ploth)

    def __del__(plot):
         self.plotl.remove(ploth)
         del(ploth)





class PyQtRPlot(pg.PlotWidget):
    def __init__(self,x=None,y=None,title="",xtitle="",ytitle="",logx=0,logy=0,**kwargs):
        pg.setConfigOption('useOpenGL', 0)
        super(PyQtRPlot, self).__init__(title=title)


        self.enableAutoRange(True, True)
        self.setLabel('left',ytitle)
        self.setLabel('bottom',xtitle)
        self.setLogMode(logx,logy)
        self.logx = logx
        self.logy = logy
        self.set_cross_hair()

        self.dsl=[] #contains the list of ds

        self.add_ds(x,y,**kwargs)

    def add_ds(self,x,y,**kwargs):
        newds = PyQtRds(x,y)
        if "name" in kwargs:
            newds.description = kwargs["name"]
        else:
            newds.description = ""
        self.dsl.append(newds)
        if not "pen" in kwargs:
            kwargs["pen"] = pg.intColor(len(self.dsl))
        pltitem = self.plot(self.dsl[-1].x,self.dsl[-1].y,**kwargs)#,pen=None,symbol='o',symbolSize=0.01,pxMode=False) #,symbolPen=mkPen("r"
        newds.setPlotItem(pltitem)
        newds.argplot = kwargs
        #self.vbox.addWidget(QtWidgets.QPushButton('button')) #for future buttons

    def hide_ds(self,ds):
        if ds not in self.dsl:
            raise ValueError("Ds not registered in this plot")
        self.removeItem(ds._plotitem)
        ds.clearPlotItem()

    def show_ds(self,ds):
        if ds not in self.dsl:
            raise ValueError("Ds not registered in this plot")
        pltitem = self.plot(self.dsl[-1].x,self.dsl[-1].y,ds.argplot)#,pen=None,symbol='o',symbolSize=0.01,pxMode=False) #,symbolPen=mkPen("r"
        newds.setPlotItem(pltitem)

    def clear_ds(self,ds):
        if ds not in self.dsl:
            raise ValueError("Ds not registered in this plot")
        self.removeItem(ds._plotitem)
        self.dsl.remove(ds)
        del(ds)


        dialog = ModuleDialog("Module Dialog",stringlist=fl2)
        if (dialog.exec() == QtWidgets.QDialog.Accepted):
            list_selected_modules = dialog.get_selected_modules()


    def set_cross_hair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved,rateLimit=60, slot=self.mouseMoved)
        #self.addItem(self.label)


    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.sceneBoundingRect().contains(pos):
            mousePoint = self.plotItem.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            vx = mousePoint.x()
            vy = mousePoint.y()
            if self.logx == 1:
                vx = 10**(vx)
            if self.logy == 1:
                vy = 10**(vy)


            self.parentgraph.graphstatusbar.setText(" X {0:.2e} Y : {1:.2e}".format(vx,vy))
            #xmin = self.viewRange()[0][0]
            #xmax = self.viewRange()[0][1]
            #ymin = self.viewRange()[1][0]
            #ymax = self.viewRange()[1][1]
            #x2  =0.8*xmax+0.2*xmin
            #y2  =0.8*ymax+0.2*ymin

    def __del__():
        for ds in self.dsl:
            del(ds)


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
        newplot = PyQtRGraph(*args, **kwargs)
        self.layout.addWidget(newplot,self.nexti,self.nextj)
        self.increment_grid()
        return newplot

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








