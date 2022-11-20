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
    def __del__(self):
        del(self.x,self.y)






class PyTabGraphMenu(QtWidgets.QMenu):
    #Class of menu to be added in any window which has a PyQtRGraph and a method get_current_PyQtRGraph
    def __init__(self,title,window):
        self.window = window
        super(PyTabGraphMenu, self).__init__(title,window)
        self.aboutToHide.connect(self.clear)
        self.aboutToShow.connect(self.create_graph_menu)

    def create_graph_menu(self):
        w = self.window.get_current_active_widget()
        if w.__class__.__name__ == "PyQtGraphGrid":
            w = w._cur_active_w
        if w.__class__.__name__ == "PyQtRPlot":
            self.addMenu(RDSMenu("Cur. Dataset",self,w))
            self.addMenu(RPlotMenu("Cur. Plot",self,w))

class Style(QtWidgets.QProxyStyle):
    def __init__(self, style = None):
        super().__init__(style)
        self._colors = dict()

    def setColor(self, text, color):
        self._colors[text] = color

    def drawControl(self, element, option, painter, widget):
        if element == QtWidgets.QStyle.CE_MenuItem:
            text = option.text
            option_ = QtWidgets.QStyleOptionMenuItem(option)
            if text in self._colors:
                color = self._colors[text]
            else:
                color = QtGui.QColor("#A9BBAE")
            option_.palette.setColor(QtGui.QPalette.Text, color)
            return self.baseStyle().drawControl(element, option_, painter, widget)
        return self.baseStyle().drawControl(element, option, painter, widget)

class MenuStyler():
    def __init__(self, menu):
        style = Style()
        style.setBaseStyle(menu.style())
        menu.setStyle(style)
        self._style = style
        self._menu = menu

    def setColor(self, key, color):
        if isinstance(key, str):
            self._style.setColor(key, color)
        elif isinstance(key, int):
            text = self._menu.actions()[key].text()
            self._style.setColor(text, color)
        else:
            raise ValueError("Key must be either int or string")

class PyQtRGraphMenu(QtWidgets.QMenu):
    # Creates a menu for graph and pass the right plot and right ds to submenu functions.
    def __init__(self,title,parent,plot):
        super(PyQtRGraphMenu, self).__init__(title,parent)
        self.plot = plot
        self.addMenu(RDSMenu("Datasets",self,plot))
        self.addMenu(RPlotMenu("Plots",self,plot))


class RDSMenu(QtWidgets.QMenu):
    def __init__(self,title,parent,plot):
        super(RDSMenu, self).__init__(title,parent)
        list_dataset_action = QtGui.QAction("List datasets",self)
        list_dataset_action.triggered.connect(plot.list_data_set)

        self.addAction(list_dataset_action)
        styler = MenuStyler(self)
        styler.setColor("List datasets", QtGui.QColor("#3D6BC4"))


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
        ploth.addLegend()
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
        newplot = PyQtRGraph(*args,parentgrid=self, **kwargs)
        self.layout.addWidget(newplot,self.nexti,self.nextj)
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








