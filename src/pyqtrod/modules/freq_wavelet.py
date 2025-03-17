# This Python file uses the following encoding: utf-8
from PyQt6 import QtWidgets, uic
import numpy as np
import pywt
from ..pyqtworker import PyQtWorker

import importlib.resources as pkg_resources


class FreqWT(QtWidgets.QWidget):
    def __init__(self, NITab=None, NIfile=None, threadpool=None):
        super(QtWidgets.QWidget, self).__init__()
        with pkg_resources.path("pyqtrod.modules", "freq_wavelet.ui") as ui_path:
            uic.loadUi(ui_path, self)

        if NITab is not None:
            self.NITab = NITab
            self.NIf = NITab.NIf
            self.threadpool = NITab.threadpool
        elif NIfile is not None and threadpool is not None:
            self.NIf = NIfile
            self.threadpool = threadpool
        else:
            raise ImportError("cannot initialize without file and threadpool")

        self.ph = None

        self.windowsize = 1000
        self.min_estimated_frequency = 10
        self.max_estimated_frequency = 300
        self.frequency_step = 10
        self.refine_freq_step = 2
        self.refine_freq_range = 0.2

        self.worker_window = 1  # s

        if NITab is not None:
            self.firbox.setValue(self.windowsize)
            self.maxfreqbox.setValue(self.max_estimated_frequency)
            self.minfreqbox.setValue(self.min_estimated_frequency)
            self.freqstepbox.setValue(self.frequency_step)
            self.refinefreqstepbox.setValue(self.refine_freq_step)
            self.refinerangebox.setValue(int(self.refine_freq_range * 100))

            self.startstopbutton.pressed.connect(self.set_start_stop_visible)
            self.computebutton.pressed.connect(self.compute_freq)
            self.refinebutton.pressed.connect(self.refine)
            self.refinebutton.setEnabled(False)

            self.set_start_stop_visible()
            self.startbox.setMinimum(0)
            self.stopbox.setMaximum(self.NIf.datasize / self.NIf.freq)
            self.maxfreqbox.valueChanged.connect(self.set_max_estimated_frequency)
            self.minfreqbox.valueChanged.connect(self.set_min_estimated_frequency)
            self.freqstepbox.valueChanged.connect(self.set_frequency_step)
            self.refinefreqstepbox.valueChanged.connect(self.set_refine_freq_step)
            self.refinerangebox.valueChanged.connect(self.set_refine_freq_range)

            self.firbox.valueChanged.connect(self.set_windowsize)
            self.startbox.valueChanged.connect(self.set_start)
            self.stopbox.valueChanged.connect(self.set_stop)
            self.set_start_stop_visible()

        self.save = False
        if NITab is not None:
            NITab.add_tool_widget(self, "FreqWT")

    def set_frequency_step(self, x):
        self.frequency_step = x

    def set_refine_freq_step(self, x):
        self.refine_freq_step = x

    def set_refine_freq_range(self, x):
        self.refine_freq_range = x / 100

    def set_max_estimated_frequency(self, x):
        self.max_estimated_frequency = x

    def set_min_estimated_frequency(self, x):
        self.min_estimated_frequency = x

    def set_windowsize(self, x):
        self.windowsize = x

    def set_start(self, x):
        self.start = x
        self.stopbox.setMinimum(x)

    def set_stop(self, x):
        self.stop = x
        self.startbox.setMaximum(x)

    def set_start_stop_visible(self):
        (xa, xb) = self.NITab.plotmain.viewRange()[0]
        if xa < 0:
            xa = 0
        if xb > self.NIf.datasize / self.NIf.freq:
            xb = self.NIf.datasize / self.NIf.freq - 0.1

        self.startbox.setValue(xa)
        self.stopbox.setValue(xb)

        self.set_start(xa)
        self.set_stop(xb)

    def refine(self):
        self.compute_freq(refine=True)

    def compute_freq(self, refine=False):
        self.done = 0
        start = int(self.start * self.NIf.freq)
        stop = int(self.stop * self.NIf.freq)
        length = stop - start
        num_splits = int((self.stop - self.start) / self.worker_window) + 1
        split_size = length // num_splits

        self.results = []
        self.completed_splits = 0
        self.computebutton.setEnabled(False)
        self.refinebutton.setEnabled(False)
        self.split_to_be_done = num_splits
        self.resstart = start
        C0, C90, C45, C135 = self.NIf.ret_cor_channel_in_file(start, stop, dec=1)
        if self.windowsize > 1:
            C0 = np.convolve(
                C0, np.ones((self.windowsize)) / self.windowsize, mode="valid"
            )[
                :: int(self.windowsize // 100)
            ]  # I remove only one tenth of the averaging window. So take every 100 points if averaing over 1000
            C90 = np.convolve(
                C90, np.ones((self.windowsize)) / self.windowsize, mode="valid"
            )[
                :: int(self.windowsize // 100)
            ]  # I remove only one tenth of the averaging window. So take every 100 points if averaing over 1000
            C45 = np.convolve(
                C45, np.ones((self.windowsize)) / self.windowsize, mode="valid"
            )[
                :: int(self.windowsize // 100)
            ]  # I remove only one tenth of the averaging window. So take every 100 points if averaing over 1000
            C135 = np.convolve(
                C135, np.ones((self.windowsize)) / self.windowsize, mode="valid"
            )[
                :: int(self.windowsize // 100)
            ]  # I remove only one tenth of the averaging window. So take every 100 points if averaing over 1000
        for i in range(num_splits):
            split_start = int(start + i * split_size)
            split_stop = (
                int(split_start + split_size) if i < num_splits - 1 else self.stop
            )
            if split_stop - split_start < 10000:
                print("Split too small ; ignored worker")
                self.split_to_be_done -= 1
                continue
            self.resstop = split_stop
            print("Starting worker" + str(i))
            split_size_dec = int(split_size / self.windowsize * 100)
            worker = PyQtWorker(
                self.main_comp,
                start=split_start,
                stop=split_stop,
                C0=C0[i * split_size_dec : (i + 1) * split_size_dec],
                C90=C90[i * split_size_dec : (i + 1) * split_size_dec],
                C45=C45[i * split_size_dec : (i + 1) * split_size_dec],
                C135=C135[i * split_size_dec : (i + 1) * split_size_dec],
                refine=refine,
            )
            worker.signals.result.connect(self.collect_results)
            worker.signals.progress.connect(self.progress_fn)
            self.threadpool.start(worker)

    def collect_results(self, result):
        self.results.append(result)
        self.completed_splits += 1
        print("Collecting result " + str(self.completed_splits))

        if self.completed_splits == self.split_to_be_done:  # All splits are done
            self.results.sort()  # Sort results by split_start
            for r in self.results:
                print(r[0])
            combined_result = np.concatenate([res[2] for res in self.results])
            self.display_result(
                self.results[0][0], self.results[-1][1], combined_result
            )

    def main_comp(
        self,
        progress_callback=None,
        start: int | None = None,
        stop: int | None = None,
        C0=None,
        C90=None,
        C45=None,
        C135=None,
        refine=False,
    ):
        if progress_callback:
            progress_callback.emit(0)
        if start is None:
            print("Start is None")
            return None, None
        if stop is None:
            print("Stop is None")
            return None, None
        if C0 is None:
            print("C0 is None")
            return None, None
        if C90 is None:
            print("C90 is None")
            return None, None
        if C45 is None:
            print("C45 is None")
            return None, None
        if C135 is None:
            print("C135 is None")
            return None, None

        if start < 0:
            start = 0
        if stop > self.NIf.datasize:
            stop = self.NIf.datasize - 1

        C0 = C0 - np.mean(C0)
        C90 = C90 - np.mean(C90)
        C45 = C45 - np.mean(C45)
        C135 = C135 - np.mean(C135)
        sampling_period = 1 / self.NIf.freq * (self.windowsize // 100)
        if refine:
            inds = np.where(
                (self.xarr_freq > (start / self.NIf.freq))
                & (self.xarr_freq < (stop / self.NIf.freq))
            )
            center_gross_freq = np.mean(self.gross_frequency[inds])
            print(center_gross_freq, self.refine_freq_range, self.refine_freq_step)

            frequencies = np.arange(
                center_gross_freq * (1 - self.refine_freq_range),
                center_gross_freq * (1 + self.refine_freq_range),
                self.refine_freq_step,
            )
        else:
            frequencies = np.arange(
                self.min_estimated_frequency,
                self.max_estimated_frequency,
                self.frequency_step,
            )
        scales = 1 / np.array(frequencies) / sampling_period
        scales = scales.astype(int)
        scales = np.unique(scales)
        scales = scales[::-1]

        all_coeff = []
        for i, channel in enumerate([C0, C90, C45, C135]):
            coefficients, frequencies = pywt.cwt(
                channel,
                scales,
                "cmor1.5-1.0",
                sampling_period=sampling_period,  # cmor1.5-1.0"
            )
            all_coeff.append(coefficients)
        power = np.zeros(coefficients.shape)
        for c in all_coeff:
            power += np.abs(c) ** 2

        weighted_freqs = np.sum(frequencies[:, None] * power, axis=0) / np.sum(
            power, axis=0
        )

        # max_freq = np.argmax(power, axis=0)

        # for i in range(power.shape[1]):
        #     startfit = max(0, max_freq[i] - 4)
        #     endfit = min(len(frequencies), max_freq[i] + 4)
        #     a, b, c = np.polyfit(
        #         frequencies[startfit:endfit],
        #         power[startfit:endfit, i],
        #         2,
        #     )
        #     max_freq[i] = -b / (2 * a)

        # print("Done")

        return start, stop, weighted_freqs

    def progress_fn(self, number):
        self.progressBar.setValue(number)

    def display_result(self, start, stop, res):
        xarr = np.linspace(start, stop, res.shape[0]) / self.NIf.freq
        self.xarr_freq = xarr
        if self.save:
            np.save(
                self.NIf.path[:-5] + "_freq_wt.npy",
                np.array([xarr, res]),
            )
        else:
            if self.ph is None:
                self.ph = self.NITab.plot(
                    xarr,
                    res,
                    title="Wavelet",
                    xtitle="Time(s)",
                    ytitle="Max Freq (Hz)",
                )
            else:
                self.ph.add_ds(
                    xarr,
                    res,
                    title="Wavelet",
                    xtitle="Time(s)",
                    ytitle="Max Freq (Hz)",
                )

        self.gross_frequency = res
        # names = ["0°", "90°", "45°", "135°"]
        # for i in range(1, 4):
        #     ph.add_ds(
        #         xarr,
        #         res[:, i],
        #         title="Wavelet",
        #         xtitle="Time(s)",
        #         ytitle="Max Freq (Hz)",
        #         name=names[i],
        #     )
        self.computebutton.setEnabled(True)
        self.refinebutton.setEnabled(True)
        self.done = 1
