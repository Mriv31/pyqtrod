# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
import numpy as np
from scipy import signal
from PyQtWorker import PyQtWorker




class FreqFFT(QtWidgets.QWidget):
    def __init__(self,NITab):
        super(QtWidgets.QWidget, self).__init__()
        uic.loadUi('Modules/FreqFFT.ui', self)


        self.NITab = NITab
        self.nperseg = 8000
        self.nfft = 32000
        self.windowsize = 8000
        self.overlap = 4000

        self.npersegbox.setValue(self.nperseg)
        self.nfftbox.setValue(self.nfft)
        self.windowsizebox.setValue(self.windowsize)
        self.overlapbox.setValue(self.overlap)

        self.startstopbutton.pressed.connect(self.set_start_stop_visible)
        self.computebutton.pressed.connect(self.compute_freq)

        self.set_start_stop_visible()
        self.stopbox.setMaximum(self.NITab.NIf.datasize/self.NITab.NIf.freq)
        self.startbox.setMaximum(self.NITab.NIf.datasize/self.NITab.NIf.freq)



        self.npersegbox.valueChanged.connect(self.set_nperseg)
        self.overlapbox.valueChanged.connect(self.set_overlap)
        self.nfftbox.valueChanged.connect(self.set_nfft)
        self.windowsizebox.valueChanged.connect(self.set_windowsize)
        self.startbox.valueChanged.connect(self.set_start)
        self.stopbox.valueChanged.connect(self.set_stop)


        NITab.add_tool_widget(self,"FreqFFT")


    def set_nperseg(self,x):
        self.nperseg = x
    def set_nfft(self,x):
        self.nfft = x
    def set_windowsize(self,x):
        self.windowsize = x
    def set_overlap(self,x):
        self.overlap = x
    def set_start(self,x):
        self.start = int((x-self.NITab.NIf.time_off)*self.NITab.NIf.freq)
    def set_stop(self,x):
        self.stop = int((x-self.NITab.NIf.time_off)*self.NITab.NIf.freq)

    def set_start_stop_visible(self):
        xa,ya,xb,yb = self.NITab.NIv.get_lim()
        self.startbox.setValue(xa)
        self.stopbox.setValue(xb)
        self.set_start(xa)
        self.set_stop(xb)



    def compute_freq(self):
        worker = PyQtWorker(self.main_comp) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_result)
        #worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.NITab.threadpool.start(worker)
    def main_comp(self, progress_callback):
        channels = []
        for i in range(4):
            channels.append(self.NITab.NIf.channels[i][self.start:self.stop]*self.NITab.NIf.a[i]+self.NITab.NIf.b[i])
        pol_ind = self.NITab.NIf.get_pol_ind(["0","90","45","135"])
        c0,c90,c45,c135 = [channels[pol_ind[i]] for i in range(len(pol_ind))]
        I0 = (c0 - c90) / (c0 + c90)
        I1 = (c45 - c135) / (c45 + c135)
        x = I0 + 1.j * I1

        xar = np.arange(0,len(I0),1)/self.NITab.NIf.freq

        n_seg = int(len(xar)/self.overlap) - 1
        max_freq = []
        xarr= []
        for i in range(n_seg):
            f0, Pxx_den0 = signal.welch(x[i*self.overlap:i*self.overlap+self.windowsize], self.NITab.NIf.freq,nperseg=self.nperseg,nfft=self.nfft)
            max_freq.append(f0[np.argmax(Pxx_den0)])
            xarr.append((self.start + self.overlap*i)/self.NITab.NIf.freq)
            progress_callback.emit(int(i/n_seg*100))
        return xarr,max_freq

    def progress_fn(self,number):
        self.progressBar.setValue(number)
    def display_result(self,res):
        xarr,max_freq = res
        self.NITab.plot(xarr,max_freq,title="Freq of X + i Y",xtitle="Time(s)",ytitle="Max Freq (Hz)")
