import numpy as np

import pyqtgraph as pg

import time



class PyQtRViewBox(pg.ViewBox): # Subclass ViewBox
        def __init__(self,parent=None):
            super(PyQtRViewBox, self).__init__(parent)

        def autoRangeY(self, padding=None, items=None, item=None):
            if item is None:
                bounds = self.childrenBoundingRect(items=items)
            else:
                bounds = self.mapFromItemToView(item, item.boundingRect()).boundingRect()

            if bounds is not None:
                co = bounds.getCoords()
                print(co)
                self.setYRange(co[1],co[3], padding=padding)

        def keyPressEvent(self, ev):
                ev.accept()
                if (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier) and (ev.key() == QtCore.Qt.Key.Key_Z):
                        self.autoRange()

                elif (ev.key() == QtCore.Qt.Key.Key_Right):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        t1 = time.time()
                        self.setXRange(xr[0]+xsize*0.3,xr[1]+xsize*0.3)

                        t2 = time.time()

                        self.autoRangeY()
                        t3 = time.time()
                        print(f"sdf{t2-t1}qsd{t3-t2}")

                elif (ev.key() == QtCore.Qt.Key.Key_Left):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]-xsize*0.3,xr[1]-xsize*0.3)
                        self.autoRangeY()
                elif (ev.key() == QtCore.Qt.Key.Key_Up):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]+xsize*0.3,xr[1]-xsize*0.3)
                        self.autoRangeY()
                elif (ev.key() == QtCore.Qt.Key.Key_Down):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]-xsize*0.3,xr[1]+xsize*0.3)
                        self.autoRangeY()
                else:
                    ev.ignore()


class PyQtRPlot(pg.PlotWidget):
    def __init__(self):
        #pg.setConfigOption('useOpenGL', 0)
        super(PyQtRPlot, self).__init__(viewBox=PyQtRViewBox())
        self.setClipToView( True)
        self.enableAutoRange(False)
        self.setDownsampling( ds=100, auto=1, mode="subsample")

from PyQt6 import QtCore, QtWidgets

pp = pg.mkQApp()
mw = QtWidgets.QMainWindow()
mw.setWindowTitle('pyqtgraph example: PlotWidget')
mw.resize(800,800)
cw = QtWidgets.QWidget()
mw.setCentralWidget(cw)
l = QtWidgets.QVBoxLayout()
cw.setLayout(l)

pw = PyQtRPlot()  ## giving the plots names allows us to link their axes together
l.addWidget(pw)
data = np.arange(10000000)+np.random.normal(0,10,10000000)
pw.plot(data, title="Simplest possible plotting example")
mw.show()

if __name__ == '__main__':
    pg.exec()
