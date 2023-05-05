# This Python file uses the following encoding: utf-8
import pyqtgraph as pg
from PyQt6 import QtGui
from PyQt6 import QtCore
from .RDSMenu import RDSMenu
#You can edit the contextual menu here by modifying myMenuEdit. Note that the PlotItem class and other parents of the ViewBox with a method "getContextMenus" also add their own
# actions every time the viewboxmenu is called. You can override this actions by override those classes.

class PyQtRViewBox(pg.ViewBox): # Subclass ViewBox
        def __init__(self,parent=None,parentplot=None):
            super(PyQtRViewBox, self).__init__(parent)
            self.parentplot = parentplot
            self.myMenuEdit()

        def autoRangeY(self, padding=None, items=None, item=None):
            if item is None:
                bounds = self.childrenBoundingRect(items=items)
            else:
                bounds = self.mapFromItemToView(item, item.boundingRect()).boundingRect()

            if bounds is not None:
                co = bounds.getCoords()
                self.setYRange(co[1],co[3], padding=padding)

        def keyPressEvent(self, ev):
                ev.accept()
                if (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier) and (ev.key() == QtCore.Qt.Key.Key_Z):
                        self.autoRange()

                elif (ev.key() == QtCore.Qt.Key.Key_Right):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]+xsize*0.3,xr[1]+xsize*0.3,update=True,padding=0)

                        self.autoRangeY()

                elif (ev.key() == QtCore.Qt.Key.Key_Left):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]-xsize*0.3,xr[1]-xsize*0.3,update=True,padding=0)
                        self.autoRangeY()
                elif (ev.key() == QtCore.Qt.Key.Key_Up):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]+xsize*0.3,xr[1]-xsize*0.3,update=True,padding=0)
                        self.autoRangeY()
                elif (ev.key() == QtCore.Qt.Key.Key_Down):
                        ranges = self.viewRange()
                        xr = ranges[0]
                        xsize = xr[1]-xr[0]
                        self.setXRange(xr[0]-xsize*0.3,xr[1]+xsize*0.3,update=True,padding=0)
                        self.autoRangeY()
                else:
                    ev.ignore()

        def myMenuEdit(self):
            #Hide Default Actions
            MenusToHide = []
            w = self.menu.actions()
            for m in w:
                for mhs in MenusToHide:
                    if (m.text().startswith(mhs)):
                        m.setVisible(False)
                        break

            #AddMySubMenu

            leftMenu = self.menu.addMenu("Background color")
            group = QtGui.QActionGroup(self)
            Yellow = QtGui.QAction(u'Yellow', group)
            Red = QtGui.QAction(u'Red', group)
            White = QtGui.QAction(u'White', group)
            leftMenu.addActions(group.actions())
            Yellow.setCheckable(True)
            Red.setCheckable(True)
            White.setCheckable(True)
            group.triggered.connect(self.setBgColor)
            self.bgActions=[Yellow,Red,White]

        def setBgColor(self, action):
              mode = None
              if action == self.bgActions[0]:
                  self.setBackgroundColor("y")
              elif action == self.bgActions[1]:
                  self.setBackgroundColor("r")
              elif action == self.bgActions[2]:
                  self.setBackgroundColor("w")




