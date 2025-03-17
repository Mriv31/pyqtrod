# This Python file uses the following encoding: utf-8
from PyQt6 import QtWidgets, uic
import numpy as np
from scipy import signal
from ..pyqtworker import PyQtWorker

import importlib.resources as pkg_resources


class FreqFFT(QtWidgets.QWidget):
    def __init__(self, NITab):
        super(QtWidgets.QWidget, self).__init__()
        with pkg_resources.path("pyqtrod.modules", "freq_fft.ui") as ui_path:
            uic.loadUi(ui_path, self)

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

        self.npersegbox.valueChanged.connect(self.set_nperseg)
        self.overlapbox.valueChanged.connect(self.set_overlap)
        self.nfftbox.valueChanged.connect(self.set_nfft)
        self.windowsizebox.valueChanged.connect(self.set_windowsize)
        self.startbox.valueChanged.connect(self.set_start)
        self.stopbox.valueChanged.connect(self.set_stop)

        self.boxes = [
            self.c0box,
            self.c90box,
            self.c45box,
            self.c135box,
            self.anisbox,
            self.itotbox,
        ]
        self.boxnames = ["C0", "C90", "C45", "C135", "ANIS", "ITOT"]

        NITab.add_tool_widget(self, "FreqFFT")

    def set_nperseg(self, x):
        self.nperseg = x

    def set_nfft(self, x):
        self.nfft = x

    def set_windowsize(self, x):
        self.windowsize = x

    def set_overlap(self, x):
        self.overlap = x

    def set_start(self, x):
        self.start = x

    def set_stop(self, x):
        self.stop = x

    def set_start_stop_visible(self):
        (xa, xb) = self.NITab.plotmain.viewRange()[0]

        self.startbox.setValue(xa)
        self.stopbox.setValue(xb)
        self.set_start(xa)
        self.set_stop(xb)

    def compute_freq(self):
        worker = PyQtWorker(
            self.main_comp
        )  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_result)
        # worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.NITab.threadpool.start(worker)

    def main_comp(self, progress_callback):
        progress_callback.emit(0)
        self.computebutton.setEnabled(False)

        c0, c90, c45, c135 = self.NITab.NIf.ret_cor_channel_in_file(
            start=int(self.start * self.NITab.NIf.freq),
            stop=int(self.stop * self.NITab.NIf.freq),
            dec=1,
        )
        dec = int(self.windowsize // 100)
        channel_list = [c0, c90, c45, c135]
        Sxx = []
        for i, ch in enumerate(channel_list):
            channel_list[i] = np.convolve(
                ch, np.ones((self.windowsize,)) / self.windowsize, mode="valid"
            )[::dec]
            frequencies, times, Sxxh = signal.spectrogram(
                ch,
                self.NITab.NIf.freq / dec,
                nperseg=self.nperseg,
            )
            Sxx.append(Sxxh)

        print("Sxx shape", np.shape(Sxx))
        print("times shape", np.shape(times))

        power = np.sum(Sxx, axis=0)

        max_freq = frequencies[np.argmax(power, axis=0)]
        return [(times, max_freq, "power")]

    def progress_fn(self, number):
        self.progressBar.setValue(number)

    def display_result(self, res):
        first = 1
        for r in res:
            xarr, max_freq, name = r
            if first == 1:
                ph = self.NITab.plot(
                    xarr,
                    max_freq,
                    title="Freq of X + i Y",
                    xtitle="Time(s)",
                    ytitle="Max Freq (Hz)",
                    name=name,
                )
                first = 0
            else:
                ph.add_ds(xarr, max_freq, name=name)
        self.computebutton.setEnabled(True)
