# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import mkPen
from .PyQtRds import PyQtRds


class PyQtRPlot(pg.PlotWidget):
    def __init__(self,parentgraph=None,parentgrid=None,x=None,y=None,title="",xtitle="",ytitle="",logx=0,logy=0,**kwargs):
        pg.setConfigOption('useOpenGL', 0)
        super(PyQtRPlot, self).__init__(title=title)

        self.parentgraph = parentgraph
        self.parentgrid = parentgrid
        self.enableAutoRange(True, True)
        self.setLabel('left',ytitle)
        self.setLabel('bottom',xtitle)
        self.setLogMode(logx,logy)
        self.logx = logx
        self.logy = logy
        self.set_cross_hair()
        self.dsnb_auto = 0

        self.dsl=[] #contains the list of ds
        self.addLegend()

        self.add_ds(x,y,**kwargs)

    def add_ds(self,x,y,**kwargs):
        newds = PyQtRds(x,y)
        if "name" in kwargs:
            newds.description = kwargs["name"]
        else:
            newds.description = "Dataset "+str(self.dsnb_auto)
            self.dsnb_auto += 1
        self.dsl.append(newds)
        if not "pen" in kwargs:
            kwargs["pen"] = pg.intColor(len(self.dsl))
        pltitem = self.plot(self.dsl[-1].x,self.dsl[-1].y,**kwargs)#,pen=None,symbol='o',symbolSize=0.01,pxMode=False) #,symbolPen=mkPen("r"
        newds.setPlotItem(pltitem)
        newds.argplot = kwargs
        return newds
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
        if (self.parentgrid != None):
            self.parentgrid.set_cur_graph(self)
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

    def list_data_set(self):
        print("Brabo")
        return

    def del_from_graph(self):
        if (self.parentgraph != None):
            self.parentgraph.remove_plot(self)

    def __del__(self):
        for ds in self.dsl:
            del(ds)
