# This Python file uses the following encoding: utf-8
# No pyqtgraph there
import pyqtgraph as pg
from functools import partial
import numpy as np
class PyQtRds(pg.PlotDataItem):
    def __init__(self,x,y,parentplot=None,params=None,**kwargs):


        super(PyQtRds, self).__init__(x=x,y=y,**kwargs)

        parentplot.addItem(self)
        self.sigClicked.connect(partial(parentplot.set_active_dataset,self))
        self.parentplot = parentplot
        properties = ['name','source','description','pen','symbol','symbolPen','symbolBrush','symbolSize','xArrayLinSorted']
        values = [None,None,None,"red",None,None,None,1,0]

        for i,p in enumerate(properties):
            if p in kwargs:
                values[i] = kwargs[p]

        self.prop = dict(zip(properties,values))


        self._dataset.x.flags.writeable = False #locks displayed array to find them later
        self._dataset.y.flags.writeable = False #locks displayed array to find them later

    def change_point_color(self,c):
        self.setSymbolPen(c)
        self.prop['SymbolPen'] = c

    def change_line_color(self,c):
        self.setPen(c)
        self.prop['pen'] = c

    def change_point_symbol(self,c):
        self.setSymbol(c)
        self.prop['Symbol'] = c

    def change_point_fill_color(self,c):
        self.setSymbolBrush(c)
        self.prop['SymbolBrush'] = c

    def change_point_size(self,c):
        self.setSymbolSize(c)
        self.prop['SymbolSize'] = c

    def change_name(self,s):
        self.prop['name'] = s
        self.opts['name'] = s
        self.parentplot.getPlotItem().legend.removeItem(self)
        self.parentplot.getPlotItem().legend.addItem(self, s)


    def save(self):
        return [np.array(list(self.prop.items())),self._dataset.x,self._dataset.y]






