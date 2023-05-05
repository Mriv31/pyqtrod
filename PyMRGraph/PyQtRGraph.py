# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtGui
from .PyQtRPlot import PyQtRPlot
import numpy as np
from datetime import datetime
# A graph region. Has tabs, a statusbars and contains PyQtRPlots.


class PyQtRGraph(QtWidgets.QWidget):



    def __init__(self,**kwargs):
        #pg.setConfigOption('useOpenGL', 0)
        super(PyQtRGraph, self).__init__()

        hbox = QtWidgets.QHBoxLayout()
        self.plotl=[]
        self.plot_inc = 0
        self.parentgrid = None
        if "parentgrid" in kwargs:
            self.parentgrid = kwargs["parentgrid"]

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

        self.setLayout(hbox)


        hbox.addWidget(plotc)

        if 'file' in kwargs and kwargs['file'] is not None:
            self.init_from_file(kwargs['file'])
            return



        properties=['Date','Author']
        values = [datetime.now(),'MR']

        self.prop=dict(zip(properties,values))



        self.add_plot(**kwargs)




    def add_plot(self,**kwargs):
        if 'parentgrid' not in kwargs and self.parentgrid is not None:
            kwargs['parentgrid'] = self.parentgrid

        if "plotname" in kwargs:
            plotname = kwargs["plotname"]
        else:
            plotname = "plot" + str(self.plot_inc)
            self.plot_inc += 1
        print(kwargs)
        ploth = PyQtRPlot(parentgraph=self,plotname=plotname,**kwargs)
        self.plotl.append(ploth)
        self.tab.addTab(ploth,plotname)
        self.tab.setCurrentWidget(ploth)

        return ploth

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


    def init_from_file(self,file):
        try:
            f = np.load(file,allow_pickle=True)
        except:
            raise("Problem while opening the file")

        self.prop=dict(f[f.files[0]])
        ind_plots_data = f[f.files[1]]
        for i in range(ind_plots_data.shape[0]):
            inds,inde = ind_plots_data[i,:]
            ploth = PyQtRPlot(parentgraph=self,parentgrid=self.parentgrid,file=f,inds=inds,inde=inde)
            self.plotl.append(ploth)
            plotname = ploth.prop['plotname']
            self.tab.addTab(ploth,plotname)
            self.tab.setCurrentWidget(ploth)


    def save(self,file):
        ArToSave = [np.array(list(self.prop.items())),0]
        indstart = 2
        indarray = np.empty([0,2],dtype="int")

        for plot in self.plotl:
            h,indr = plot.save(indstart)
            if (indr - indstart) == len(h):
                indarray = np.vstack((indarray,[indstart,indr]))
                indstart = indr
                ArToSave += h
            else:
                raise("problem - will not be saved")

        ArToSave[1] = indarray

        np.savez(file,*ArToSave)





    def __del__(self):
        for p in self.plotl:
            del(p)


