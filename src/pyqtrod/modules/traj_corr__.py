# This Python file uses the following encoding: utf-8


from ..pyqtworker import PyQtWorker
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
import numpy as np
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from pyqtgraph import mkColor
from functools import partial
from ..helpers.corr_matrix import Icor_matrix
from ..helpers.fourkas import Fourkas


import importlib.resources as pkg_resources


class Traj_corr(QtWidgets.QWidget):
    def __init__(self, NITab):
        super(QtWidgets.QWidget, self).__init__()
        with pkg_resources.path("pyqtrod.modules", "traj_corr.ui") as ui_path:
            uic.loadUi(ui_path, self)

        self.NITab = NITab

        self.startstopbutton.pressed.connect(self.set_start_stop_visible)
        self.computebutton.pressed.connect(self.compute_freq)
        self.playbutton.pressed.connect(self.start_animation)
        self.stopbutton.pressed.connect(self.stop_animation)
        self.convolvebutton.pressed.connect(self.do_speed_by_phi_convolve)

        self.playbutton.setEnabled(False)
        self.stopbutton.setEnabled(False)
        self.convolvebutton.setEnabled(False)

        self.set_start_stop_visible()
        self.stopbox.setMaximum(self.NITab.NIf.datasize / self.NITab.NIf.freq)
        self.startbox.setMaximum(self.NITab.NIf.datasize / self.NITab.NIf.freq)

        self.acorrslider.setMaximum(0.5)
        self.acorrslider.setMinimum(-0.5)
        self.acorrslider.valueChanged.connect(self.update_a)
        self.bcorrslider.setMaximum(0.5)
        self.bcorrslider.setMinimum(-0.5)
        self.bcorrslider.valueChanged.connect(self.update_b)
        self.ccorrslider.setMaximum(0.5)
        self.ccorrslider.setMinimum(-0.5)
        self.ccorrslider.valueChanged.connect(self.update_c)

        self.dcorrslider.setMaximum(0.5)
        self.dcorrslider.setMinimum(-0.5)
        self.dcorrslider.valueChanged.connect(self.update_d)

        self.acorr = 0
        self.bcorr = 0
        self.ccorr = 0
        self.dcorr = 0

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_rod)

        self.startbox.valueChanged.connect(self.set_start)
        self.stopbox.valueChanged.connect(self.set_stop)

        self.timerslider.valueChanged.connect(self.set_timer)
        self.npointsslider.valueChanged.connect(self.set_npoints)
        self.stepslider.valueChanged.connect(self.set_step)

        self.step = 10
        self.npoints = 100
        self.updatetimer = 10
        self.index = 0
        self.convolutionwindow = 1000

        self.convolutionwindowbox.valueChanged.connect(self.set_conv_window)
        self.convolutionwindowbox.setValue(self.convolutionwindow)

        self.timerslider.setValue(self.updatetimer)
        self.npointsslider.setValue(self.npoints)
        self.stepslider.setValue(self.step)

        NITab.add_tool_widget(self, "Traj_corr")

    def update_a(self, x):
        self.acorr = x
        self.update_freq()

    def update_b(self, x):
        self.bcorr = x
        self.update_freq()

    def update_c(self, x):
        self.ccorr = x
        self.update_freq()

    def update_d(self, x):
        self.dcorr = x
        self.update_freq()

    def set_conv_window(self, x):
        self.convolutionwindow = x

    def set_npoints(self, x):
        self.npoints = x

    def set_timer(self, x):
        self.timer.setInterval(x)

    def set_step(self, x):
        self.step = x

    def set_start(self, x):
        self.start = int((x - self.NITab.NIf.time_off) * self.NITab.NIf.freq)
        if self.start < 0:
            self.start = 0

    def set_stop(self, x):
        self.stop = int((x - self.NITab.NIf.time_off) * self.NITab.NIf.freq)
        if self.stop >= self.NITab.NIf.datasize:
            self.stop = self.NITab.NIf.datasize - 1

    def set_start_stop_visible(self):
        (xa, xb) = self.NITab.plotmain.viewRange()[0]
        self.startbox.setValue(xa)
        self.stopbox.setValue(xb)
        self.set_start(xa)
        self.set_stop(xb)

    def do_speed_by_phi_convolve(self):
        worker = PyQtWorker(
            self.convolve
        )  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_convolution_speed)
        # worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.NITab.threadpool.start(worker)

    def convolve(self, progress_callback):
        self.speed_phi = np.convolve(
            np.diff(self.phi),
            np.ones(self.convolutionwindow) / self.convolutionwindow,
            mode="valid",
        )
        # idx = np.arange(self.convolutionwindow) + np.arange(len(self.phi)-self.convolutionwindow+1)[:,None]
        # self.speed_phi = np.std(self.phi[idx],axis=1)

    def compute_freq(self):
        worker = PyQtWorker(
            self.main_comp
        )  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_result)
        # worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.NITab.threadpool.start(worker)

    def update_freq(self):
        worker = PyQtWorker(
            self.main_comp
        )  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.update_cloud)
        # worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.NITab.threadpool.start(worker)

    def main_comp(self, progress_callback):
        self.stopbutton.setEnabled(False)
        self.timer.stop()
        self.convolvebutton.setEnabled(False)
        channels = []
        print(self.start, self.stop)

        for i in range(4):
            channels.append(self.NITab.NIf.channels[i][self.start : self.stop])
        pol_ind = self.NITab.NIf.get_pol_ind(["0", "90", "45", "135"])
        c0, c90, c45, c135 = [channels[pol_ind[i]] for i in range(len(pol_ind))]

        # res = find_best_matrix(c0,c90,c45,c135)
        ac = np.asarray(np.vstack((c0, c90, c45, c135)))
        bc = np.dot(
            Icor_matrix(a=self.acorr, b=self.bcorr, c=self.ccorr, d=self.dcorr), ac
        )
        c0 = bc[0, :]
        c90 = bc[1, :]
        c45 = bc[2, :]
        c135 = bc[3, :]

        phi, theta1 = Fourkas(c0, c90, c45, c135, NA=1.3, nw=1.33)

        self.theta1 = theta1

        phi = np.unwrap(phi, period=np.pi)
        progress_callback.emit(70)

        self.v1 = np.column_stack(
            (np.sin(theta1) * np.cos(phi), np.sin(theta1) * np.sin(phi), np.cos(theta1))
        )
        self.v1[np.isnan(self.v1)] = 0
        self.phi = phi
        self.phiu = np.unwrap(self.phi, period=np.pi)
        self.phir = self.phiu % (2 * np.pi)
        self.samplesize = len(self.phi)
        self.index = 0
        self.convolvebutton.setEnabled(True)
        progress_callback.emit(100)
        return self.v1

    def update_rod(self):
        self.index += self.step
        self.index = self.index % self.samplesize
        self.rodline.setData(
            pos=np.vstack(
                (
                    [0, 0, 0],
                    np.average(self.v1[self.index : self.index + self.npoints], axis=0),
                )
            )
        )
        self.scatter.setData(pos=self.v1[self.index : self.index + self.npoints])
        self.elapsedtime.setText(
            "{:.3f}".format(self.index / self.NITab.NIf.freq * 1000) + "ms"
        )

    def update_cloud(self):
        self.plt.setData(pos=self.v1)
        y, x = np.histogram(self.phir, 100)
        self.curve.setData(x, y)

    def stop_animation(self):
        self.stopbutton.setEnabled(False)
        self.timer.stop()
        self.playbutton.setEnabled(True)

    def start_animation(self):
        self.playbutton.setEnabled(False)
        self.timer.start(self.updatetimer)
        self.stopbutton.setEnabled(True)

    def progress_fn(self, number):
        self.progressBar.setValue(number)

    def wdestroyed(self, wpg):
        if self.winpg == wpg:  # if destroyed current window
            self.timer.stop()
            self.stopbutton.setEnabled(False)

    def display_result(self, res):
        if len(self.phi) > 2e6:
            return

        self.winpg, self.w, self.ploth = self.NITab.plot3D2D(title="3D plot - FKtraj")

        self.winpg.destroyed.connect(partial(self.wdestroyed, self.winpg))

        color = mkColor("r")
        color.setAlphaF(0.1)
        self.plt = gl.GLScatterPlotItem(
            pos=self.v1, size=0.01, pxMode=False, color=color
        )
        self.w.addItem(self.plt)
        color = mkColor("r")
        color.setAlphaF(1)
        plt = gl.GLScatterPlotItem(
            pos=np.asarray([0, 0, 0]), color=color, size=0.1, pxMode=False
        )
        self.plt.setGLOptions("translucent")

        self.w.addItem(plt)
        self.rodline = gl.GLLinePlotItem(pos=np.vstack(([0, 0, 0], self.v1[0])))
        self.w.addItem(self.rodline)
        color = mkColor("w")
        color.setAlphaF(1)
        self.scatter = gl.GLScatterPlotItem(
            pos=self.v1[: self.npoints], color=color, size=0.03, pxMode=False
        )
        self.w.addItem(self.scatter)
        # y = np.convolve(np.diff(res), np.ones(1000)/1000, mode='valid')
        # self.NITab.plot(np.arange(len(y))*self.NITab.NIf.freq,y)
        self.playbutton.setEnabled(True)
        y, x = np.histogram(self.phir, 100)
        self.curve = pg.PlotCurveItem(
            x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80)
        )
        self.ploth.addItem(self.curve)

    def display_convolution_speed(self):
        self.NITab.plot(
            np.linspace(
                (self.start - self.NITab.NIf.time_off) / self.NITab.NIf.freq,
                (self.stop - self.NITab.NIf.time_off) / self.NITab.NIf.freq,
                len(self.speed_phi),
            ),
            self.speed_phi * self.NITab.NIf.freq / 2 / np.pi,
            title="FIR derivative of phi",
            xtitle="Time (s)",
            ytitle="Speed ",
        )
