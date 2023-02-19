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

        self.boxes = [self.c0box,self.c90box,self.c45box,self.c135box,self.anisbox,self.itotbox]
        self.boxnames = ["C0","C90","C45","C135","ANIS","ITOT"]


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



    def compute_freq(self):
        worker = PyQtWorker(self.main_comp) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_result)
        #worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.NITab.threadpool.start(worker)
    def main_comp(self, progress_callback):
        channels = []
        progress_callback.emit(0)
        self.computebutton.setEnabled(False)




        C0,C90,C45,C135 = self.NITab.NIf.ret_cor_channel(self.start,self.stop)
        I0 = (C0 - C90) / (C0 + C90)
        I1 = (C45 - C135) / (C45 + C135)
        if (self.anisbox.isChecked()):
            ANIS = I0 + 1.j * I1
        if (self.itotbox.isChecked()):
            ITOT = C90+C0+C45+C135
        res= []

        nchecked = 0

        for b in self.boxes:
            if b.isChecked():
                nchecked+=1


        for bi in range(len(self.boxes)):
            if self.boxes[bi].isChecked():
                x = locals()[self.boxnames[bi]]
            else:
                continue

            n_seg = int(len(x)/self.overlap) - 1
            max_freq = []
            xarr= []
            for i in range(n_seg):
                f0, Pxx_den0 = signal.welch(x[i*self.overlap:i*self.overlap+self.windowsize], self.NITab.NIf.freq/self.NITab.NIf.dec,nperseg=self.nperseg,nfft=self.nfft)
                max_freq.append(f0[np.argmax(Pxx_den0)])
                xarr.append((self.start + self.overlap*i)/self.NITab.NIf.freq*self.NITab.NIf.dec)
                progress_callback.emit(int(i/n_seg*100*(bi+1)/nchecked))
            progress_callback.emit(int(100*(bi+1)/nchecked))
            res.append((np.array(xarr),np.array(max_freq),self.boxnames[bi]))
        return res

    def progress_fn(self,number):
        self.progressBar.setValue(number)
    def display_result(self,res):
        first = 1
        for r in res:
            xarr,max_freq,name = r
            if (first == 1):
                ph = self.NITab.plot(xarr,max_freq,title="Freq of X + i Y",xtitle="Time(s)",ytitle="Max Freq (Hz)",name=name)
                first = 0
            else:
                ph.add_ds(xarr,max_freq,name=name)
        self.computebutton.setEnabled(True)



