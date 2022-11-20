# This Python file uses the following encoding: utf-8


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



