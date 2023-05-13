# This Python file uses the following encoding: utf-8
from PyQt6 import QtWidgets
import pyqtgraph as pg
from .PyQtRds import PyQtRds
from .PyQtRViewBox import PyQtRViewBox
from .RDSMenu import RDSMenu
import numpy as np
from .InputF import InputF
import PyMRGraph.shared as shared

# A graph ; subinstace of PlotWidget.
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
class PyQtRPlot(pg.PlotWidget):
    def __init__(self,parentgraph=None,parentgrid=None,x=None,y=None,**kwargs):
        pg.setConfigOption('useOpenGL', 0)
        vb = PyQtRViewBox(parentplot=self)
        if 'title' in kwargs:
            title = kwargs['title']
        else:
            title = None
        super(PyQtRPlot, self).__init__(title=title,viewBox=vb)

        self.parentgraph = parentgraph
        self.parentgrid = parentgrid
        self.dsnb_auto = 0
        self.active_dataset = None
        self.dsl=[] #contains the list of ds



        self.set_cross_hair()
        self.addLegend()
        self.CustomizeMenu()

        if 'file' in kwargs and kwargs['file'] is not None:
            self.init_from_file(kwargs['file'],kwargs['inds'],kwargs['inde'])
            return

        properties = ['plotname','xtitle','ytitle','xunits','yunits','title','logx','logy']
        values = [None,None,None,None,None,None,0,0]
        for i,p in enumerate(properties):
            if p in kwargs:
                values[i] = kwargs[p]
        self.prop = dict(zip(properties[:],values[:]))
        self.setLabel('left',text=self.prop['ytitle'],units=self.prop['yunits'])
        self.setLabel('bottom',text=self.prop['xtitle'],units=self.prop['xunits'])
        self.setLogMode(self.prop['logx'],self.prop['logy'])

        self.add_ds(x,y,**kwargs)

    def init_from_file(self,f,inds,inde):
        self.prop=dict(f[f.files[inds]])
        ind_ds_data = f[f.files[inds+1]]
        for i in range(ind_ds_data.shape[0]):
            dinds,dinde = ind_ds_data[i,:]
            dictio = dict(f[f.files[dinds]])
            self.add_ds(f[f.files[dinds+1]],f[f.files[dinds+2]],**dictio)


    def CustomizeMenu(self):
        pltitem = self.getPlotItem()
        self.menu = pltitem.ctrlMenu

        xact = self.menu.addAction("Set X Label")
        yact = self.menu.addAction("Set Y Label")

        xact.triggered.connect(self.set_X_label)
        yact.triggered.connect(self.set_Y_label)


        self.dsmenu =  self.menu.addMenu(RDSMenu("Cur. Dataset",self.menu,self))

        #save = self.menu.addAction("Save all")
        #save.triggered.connect(self.parentgraph.save)

    def reload_DSMenu(self):
        self.menu.removeAction(self.dsmenu)
        self.dsmenu = self.menu.addMenu(RDSMenu("Cur. Dataset",self.menu,self))


    def set_X_label(self):
        title,unit = InputF("Title of X-Axis %s Unit %s")
        self.setLabel("bottom",text=title,units=unit)
        self.prop['xtitle']=title
        self.prop['xunits']=unit


    def set_Y_label(self):
        title,unit = InputF("Title of Y-Axis %s Unit %s")
        self.setLabel("left",text=title,units=unit)
        self.prop['ytitle']=title
        self.prop['yunits']=unit

    def get_active_dataset(self):
        return self.active_dataset

    def set_active_dataset(self,ds):
        if ds in self.dsl:
            self.active_dataset = ds
            self.reload_DSMenu()


    def add_ds(self,x,y,**kwargs):
        if 'xArrayLinSorted' in kwargs and kwargs['xArrayLinSorted']==1:
            self.setClipToView( True)
            self.enableAutoRange(False)
            self.setDownsampling( ds=None, auto=1, mode="subsample") #Wait for Repair by pyqtgraph team.
            self.setXRange(x[0],x[-1])
            kwargs['autoDownsample']=1
            kwargs['downsample']=None,
            kwargs['downsampleMethod']="subsample"
            kwargs['clipToView'] = True
        else:
             if len(x)>1e6:
                b,= InputF("This is a long dataset. If it is sorted with linear indices (time series) please enter 1. \n If you don't I will remove scatter indices. %d ")
                print(b)
                if int(b) == 1 :
                    self.setClipToView( True)
                    self.enableAutoRange(False)
                    self.setDownsampling( ds=None, auto=1, mode="subsample") #Wait for Repair by pyqtgraph team.
                    self.setXRange(x[0],x[-1])
                    kwargs['autoDownsample']=1
                    kwargs['downsample']=None,
                    kwargs['downsampleMethod']="subsample"
                    kwargs['clipToView'] = True
                    kwargs['xArrayLinSorted']=1
                else:
                    kwargs['symbol']=None
                    kwargs['symbolBrush']=None
                    kwargs['symbolPen']=None
                    kwargs['xArrayLinSorted']=0
        print(kwargs)
        if "name" in kwargs:
            dsname = kwargs["name"]
        else:
            dsname = "Dataset "+str(self.dsnb_auto)
        self.dsnb_auto += 1
        if not "pen" in kwargs:
            kwargs["pen"] = pg.intColor(len(self.dsl))
        if 'name' in kwargs:
            newds = PyQtRds(parentplot=self,**kwargs,clickable=True)
            newds.setData(x=x,y=y)
        else:
            newds = PyQtRds(name=dsname,parentplot=self,**kwargs,clickable=True)
            newds.setData(x=x,y=y)


        newds.opts["useCache"] = 1
        self.dsl.append(newds)

        self.active_dataset = newds
        return newds

    def set_cross_hair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved,rateLimit=60, slot=self.mouseMoved)
        #self.addItem(self.label)


    def mouseMoved(self,evt):
        shared.active_plot = self
        shared.active_graph = self.parentgraph
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.sceneBoundingRect().contains(pos):
            mousePoint = self.plotItem.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            vx = mousePoint.x()
            vy = mousePoint.y()
            if self.prop['logx'] == 1:
                vx = 10**(vx)
            if self.prop['logy'] == 1:
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

    def save(self,indstart):

        h = [np.array(list(self.prop.items())),0]
        indstart +=2
        indarray = np.empty([0,2],dtype="int")
        for ds in self.dsl:
            h1 = ds.save() #return arrays saved by plot
            indarray = np.vstack((indarray,[indstart,indstart+len(h1)])) #keep numbers of arrays in child
            h+=h1
            indstart+=len(h1)
        h[1] = indarray #save arrays from datasets


        return h,indstart

    def __del__(self):
        for ds in self.dsl:
            del(ds)
