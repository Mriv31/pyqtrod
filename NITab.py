# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
import numpy as np
from functools import partial
import time
from NIVisualizator import NIVisualizator
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from importlib import import_module, reload
import os

from ModuleDialog import ModuleDialog
from MatrixDialog import MatrixDialog,MatrixChoose

from PyMRGraph import PyTabGraphMenu, PyQtGraphGrid



class NITab(QtWidgets.QMainWindow):
    def __init__(self,NIf,threadpool):
        super(NITab, self).__init__()
        self.NIf = NIf
        self.threadpool = threadpool
        uic.loadUi('NITab.ui', self)
        win = self.mdiArea.addSubWindow(self.Visualizator)
        win.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.WindowTitleHint | QtCore.Qt.WindowType.WindowMinMaxButtonsHint | QtCore.Qt.WindowType.SubWindow)
        self.NIv = NIVisualizator(self.rawview,NIf,self.DataSlider)
        self.choose_matrix_menu()

        self.set_file_properties()
        self.pols = [self.pol0,self.pol1,self.pol2,self.pol3]
        self.checkbuttons = [self.check0,self.check1,self.check2,self.check3]
        self.decimatebox.setCurrentText(str(self.NIf.dec))
        self.set_visualizator_buttons()
        self.init_pol_from_NIf_default()
        self.setslider()
        self.n_modules = 0
        self.set_coeffs_buttons()
        self.toolmodules = []
        self.imported_modules = []
        self.load_all_modules()
        self.menuBar.addMenu(PyTabGraphMenu("Graph menu",self))

    def load_all_modules(self):
        fl = os.listdir("./Modules/")
        fl2 = []
        for f in fl:
            if f.endswith(".py"):
                if not f.endswith("beta.py"):
                    fl2.append(f)
        for t in fl2:
            self.load_module(t[:-3])


    def load_module_menu(self):
        fl = os.listdir("./Modules/")
        fl2 = []
        for f in fl:
            if f.endswith(".py"):
                fl2.append(f)
        dialog = ModuleDialog("Module Dialog",stringlist=fl2)
        if (dialog.exec() == QtWidgets.QDialog.Accepted):
            list_selected_modules = dialog.get_selected_modules()
        else:
            return
        for t in list_selected_modules:
            self.load_module(t[:-3])


    def edit_matrix_menu(self):
        dialog = MatrixDialog("Edit correction matrix",mat=self.NIf.matcor)
        dialog.exec()
        self.NIf.update_data_from_file(time=-2)
        self.NIv.update_series_from_file()



    def choose_matrix_menu(self):
        dialog = MatrixChoose("Choose correction matrix",file=self.NIf)
        dialog.exec()
        self.NIf.update_data_from_file(time=-2)
        self.NIv.update_series_from_file()






    def load_module(self,module_name): #load or reload
            found = 0
            for i in range(len(self.imported_modules)):
                m, mn = self.imported_modules[i]
                if mn == module_name:
                    found = 1
                    module = reload(m)
                    self.imported_modules[i][0] = module
                    break
            if (found == 0):
                module = import_module(module_name)
                self.imported_modules.append([module,module_name])

            my_class = getattr(module, module_name)
            module = my_class(self)


    def add_tool_widget(self,widget,name):
        if self.toolmodules == []:
            self.toolbox = QtWidgets.QToolBox()
            self.dockanalysis.setWidget(self.toolbox)
        else:
            for i in range(len(self.toolmodules)):
                w,n,ind = self.toolmodules[i]
                if n == name:
                    del self.toolmodules[i]
                    #w.hide()
                    self.toolbox.removeItem(ind)
                    for j in range(len(self.toolmodules)):
                        w2,n2,ind2 = self.toolmodules[j]
                        if (ind2 >= ind):
                            self.toolmodules[j][2]-=1
                    break
        ind = self.toolbox.addItem(widget,name)
        self.toolmodules.append([widget,name,ind])

    def set_coeffs_buttons(self):
        self.abut = []
        self.bbut = []


        qg = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        qg.setLayout(layout)
        for i in range(4):

            label = QtWidgets.QLabel()
            layout.addWidget(label)
            label.setText(self.NIf.channelnames[i])

            hw = QtWidgets.QWidget()
            layout.addWidget(hw)

            layout2 = QtWidgets.QHBoxLayout()
            hw.setLayout(layout2)

            label = QtWidgets.QLabel()
            layout2.addWidget(label)
            label.setText("a")


            nb = QtWidgets.QDoubleSpinBox()
            layout2.addWidget(nb)
            nb.setValue(self.NIf.a[i])
            nb.valueChanged.connect(partial(self.NIv.set_a,channel = i))
            self.abut.append(nb)

            label = QtWidgets.QLabel()
            layout2.addWidget(label)
            label.setText("b")

            nb = QtWidgets.QDoubleSpinBox()
            layout2.addWidget(nb)
            nb.setValue(self.NIf.b[i])
            nb.setMinimum(-3)
            nb.valueChanged.connect(partial(self.NIv.set_b,channel = i))
            self.bbut.append(nb)

        self.toolBox_2.addItem(qg,"Corr coeffs")

    def update_coeffs_buttons(self):
        for i in range(4):
            self.abut[i].setValue(self.NIf.a[i])
            self.bbut[i].setValue(self.NIf.b[i])


    def set_file_properties(self):
        self.filepathdisplay.setText(self.NIf.path)
        self.groupnbdisplay.setText(str(self.NIf.groupnb))
        self.freqdisplay.setText(str(round(self.NIf.freq/1000)))
        self.startTimedisplay.setDateTime(QtCore.QDateTime.fromSecsSinceEpoch(int(self.NIf.starttime.astype("int")/1e6))) #trick will need to correct that if dates become incorrect
        self.lengthptsdisplay.setText("{:.3e}".format(self.NIf.datasize))
        self.lengthmindisplay.setText("{:.2f}".format(self.NIf.datasize/self.NIf.freq/60))
        self.labelchannel0.setText(self.NIf.channelnames[0])
        self.labelchannel1.setText(self.NIf.channelnames[1])
        self.labelchannel2.setText(self.NIf.channelnames[2])
        self.labelchannel3.setText(self.NIf.channelnames[3])
        pass

    def set_visualizator_buttons(self):
        for i in range(4):
            self.checkbuttons[i].stateChanged.connect(partial(self.NIv.set_visible_channel, channel = i))
            self.pols[i].currentTextChanged.connect(partial(self.set_pol_channel, channel = i))
            #self.pols[i].setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            #self.checkbuttons[i].setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.decimatebox.currentTextChanged.connect(self.NIv.change_decimation)
        #self.decimatebox.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def setslider(self):
        self.DataSlider.setMinimum(0)
        self.DataSlider.setMaximum(self.NIf.datasize/self.NIf.freq)
        #self.DataSlider.setHandleLabelPosition(LabelPosition.NoLabel)
        self.DataSlider.valueChanged.connect(self.NIv.sliderchanged)
    def init_pol_from_NIf_default(self):
        for i in range(4):
            self.pols[i].setCurrentText(self.NIf.orientations[i])




    def set_pol_channel(self,string,channel):
        current_strings = []
        p = ["0","45","90","135"]
        str_to_change = string
        for i in range(4):
            current_strings.append(str(self.pols[i].currentText()))
        for i in range(4):
            if current_strings.count(p[i]) == 2:
                str_to_change = p[i]
            if current_strings.count(p[i]) == 0:
                new_value = p[i]

        for i in range(4):
            if (i!= channel):
                if current_strings[i] == str_to_change:
                    self.pols[i].setCurrentText(new_value)
        self.NIf.orientations[channel] = string

    def get_current_active_widget(self):
        ac_subwindow = self.mdiArea.activeSubWindow()
        cw = ac_subwindow.widget()
        return cw





    def plot(self,x,y,title="",xtitle="",ytitle="",**kwargs):
         winpg = QtWidgets.QMdiSubWindow()
         winpg.setWindowTitle(title)
         self.mdiArea.addSubWindow(winpg)
         w = PyQtGraphGrid(title=title)
         winpg.setWidget(w)
         ph = w.addPlot(x=x,y=y,xtitle=xtitle,ytitle=ytitle,**kwargs)
         winpg.show()
         return ph

    def plot3D(self,title="",xtitle="",ytitle=""):
          winpg = QtWidgets.QMdiSubWindow()
          winpg.setWindowTitle(title)
          self.mdiArea.addSubWindow(winpg)
          w = gl.GLViewWidget()
          w.setWindowTitle(title)
          w.setCameraPosition(distance=40)
          winpg.setWidget(w)
          winpg.show()
          winpg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
          return winpg,w

    def plot3D2D(self,title="",xtitle="",ytitle=""):
        winpg = QtWidgets.QMdiSubWindow()
        winpg.setWindowTitle(title)
        widget = QtWidgets.QWidget()
        winpg.setWidget(widget)
        self.mdiArea.addSubWindow(winpg)
        w = gl.GLViewWidget()
        w.setWindowTitle(title)
        w.setCameraPosition(distance=40)
        layoutgb = QtWidgets.QGridLayout()
        widget.setLayout(layoutgb)
        ploth= pg.PlotWidget(title=title)
        ploth.enableAutoRange(True, True)
        layoutgb.addWidget(w, 0, 0)
        layoutgb.addWidget(ploth, 0, 1)
        winpg.show()
        winpg.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        ploth.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        w.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        w.setSizePolicy(ploth.sizePolicy())
        return winpg,w,ploth

