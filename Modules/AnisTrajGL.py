# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
import numpy as np
from PyQtWorker import PyQtWorker
import pyqtgraph.opengl as gl
from pyqtgraph import mkColor
from corr_matrix import *
from Fourkas import *




class AnisTrajGL(QtWidgets.QWidget):
    def __init__(self,NITab):
        super(AnisTrajGL, self).__init__()
        uic.loadUi('Modules/AnisTrajGL.ui', self)


        self.NITab = NITab

        self.startstopbutton.pressed.connect(self.set_start_stop_visible)
        self.playbutton.pressed.connect(self.start_animation)
        self.stopbutton.pressed.connect(self.stop_animation)

        self.playbutton.setEnabled(False)
        self.stopbutton.setEnabled(False)

        self.computebutton.pressed.connect(self.compute_freq)


        self.set_start_stop_visible()
        self.stopbox.setMaximum(self.NITab.NIf.datasize/self.NITab.NIf.freq)
        self.startbox.setMaximum(self.NITab.NIf.datasize/self.NITab.NIf.freq)


        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_rod)

        self.startbox.valueChanged.connect(self.set_start)
        self.stopbox.valueChanged.connect(self.set_stop)

        self.timerslider.valueChanged.connect(self.set_timer)
        self.npointsslider.valueChanged.connect(self.set_npoints)
        self.stepslider.valueChanged.connect(self.set_step)

        self.step = 10
        self.npoints=100
        self.updatetimer = 10
        self.index = 0

        self.timerslider.setValue(self.updatetimer)
        self.npointsslider.setValue(self.npoints)
        self.stepslider.setValue(self.step)



        NITab.add_tool_widget(self,"AnisTrajGL")



    def set_npoints(self,x):
        self.npoints = x
    def compute_freq(self):
        worker = PyQtWorker(self.main_comp) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_result)
        #worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.NITab.threadpool.start(worker)

    def set_timer(self,x):
        self.timer.setInterval(x)
    def set_step(self,x):
        self.step = x

    def set_start(self,x):
        self.start = int((x-self.NITab.NIf.time_off)*self.NITab.NIf.freq)
        if self.start < 0 :
            self.start = 0
    def set_stop(self,x):
        self.stop = int((x-self.NITab.NIf.time_off)*self.NITab.NIf.freq)
        if self.stop >= self.NITab.NIf.datasize :
            self.stop = self.NITab.NIf.datasize-1

    def set_start_stop_visible(self):
        xa,ya,xb,yb = self.NITab.NIv.get_lim()
        self.startbox.setValue(xa)
        self.stopbox.setValue(xb)
        self.set_start(xa)
        self.set_stop(xb)



    def main_comp(self, progress_callback):

        self.stopbutton.setEnabled(False)
        self.timer.stop()
        channels = []
        print(self.start,self.stop)


        c0,c90,c45,c135 = self.NITab.NIf.ret_cor_channel(self.start,self.stop)

        progress_callback.emit(30)


        self.I0 = (c0 - c90) / (c0 + c90)
        self.I1 = (c45 - c135) / (c45 + c135)
        self.samplesize = len(self.I0)


        progress_callback.emit(70)



        progress_callback.emit(100)



    def update_rod(self):
        self.index += self.step
        self.index = self.index % self.samplesize
        self.elapsedtime.setText("{:.3f}".format(self.index/self.NITab.NIf.freq*1000)+ "ms")
        self.curplt.setData(pos=self.v1[self.index:self.index+self.npoints])
        self.elapsedtime.setText("{:.3f}".format(self.index/self.NITab.NIf.freq*1000)+ "ms")
        self.text3D.setData(text="{:.3f}".format(self.index/self.NITab.NIf.freq*1000)+ "ms")


    def stop_animation(self):
        self.stopbutton.setEnabled(False)
        self.timer.stop()
        self.playbutton.setEnabled(True)



    def start_animation(self):
        self.playbutton.setEnabled(False)
        self.timer.start(self.updatetimer)
        self.stopbutton.setEnabled(True)

    def progress_fn(self,number):
        self.progressBar.setValue(number)

    def wdestroyed(self,wpg):
        if (self.winpg == wpg): #if destroyed current window
            self.timer.stop()
            self.stopbutton.setEnabled(False)



    def display_result(self):
        self.winpg,self.w = self.NITab.plot3D(title="3D plot - FKtraj")

        self.v1 = np.column_stack((self.I0,self.I1,np.zeros(len(self.I0))))

        self.plt = gl.GLScatterPlotItem(pos=self.v1,size=0.01,pxMode=False,color=mkColor("red"))
        self.curplt = gl.GLScatterPlotItem(pos=self.v1[:self.npoints],size=0.01,pxMode=False,color=mkColor("white"))
        self.plt.setGLOptions('translucent')


        self.text3D = gl.GLTextItem(pos=[1,1,1],color=mkColor("g"))
        self.w.addItem(self.text3D)


        self.w.addItem(self.plt)
        self.w.addItem(self.curplt)
        self.w.show()
        self.winpg.show()




        self.playbutton.setEnabled(True)

