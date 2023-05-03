# This Python file uses the following encoding: utf-8
# No pyqtgraph there
import pyqtgraph as pg
class PyQtRds(pg.PlotDataItem):
    def __init__(self,x,y,description="",dssource=None,parentplot=None,params=None,**kwargs):
        super(PyQtRds, self).__init__(x=x,y=y,**kwargs)
        if params is None:
                    params = {}
        if parentplot is not None:
            parentplot.addItem(self, params=params)
        self.dssource = dssource
        self.description = description
        self._dataset.x.flags.writeable = False #locks displayed array to find them later
        self._dataset.y.flags.writeable = False #locks displayed array to find them later




