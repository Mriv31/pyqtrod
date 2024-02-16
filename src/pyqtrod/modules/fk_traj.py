# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
import numpy as np
from ..pyqtworker import PyQtWorker
import pyqtgraph.opengl as gl
from pyqtgraph import mkColor
from functools import partial
from ..helpers.theta_phi_line import fourier_fit
import os
import importlib.resources as pkg_resources


class FKtraj(QtWidgets.QWidget):
    def __init__(self, NITab):
        super(QtWidgets.QWidget, self).__init__()
        with pkg_resources.path("pyqtrod.modules", "fk_traj.ui") as ui_path:
            uic.loadUi(ui_path, self)

        self.NITab = NITab

        self.startstopbutton.pressed.connect(self.set_start_stop_visible)
        self.computebutton.pressed.connect(self.compute_freq)
        self.playbutton.pressed.connect(self.start_animation)
        self.stopbutton.pressed.connect(self.stop_animation)
        self.convolvebutton.pressed.connect(self.do_speed_by_phi_convolve)
        self.displayphi.pressed.connect(self.display_phi_deg)
        self.show_transitions_button.pressed.connect(self.show_transitions)

        self.playbutton.setEnabled(False)
        self.stopbutton.setEnabled(False)
        self.convolvebutton.setEnabled(False)
        self.displayphi.setEnabled(False)

        self.set_start_stop_visible()
        self.startbox.setMaximum(self.NITab.NIf.xminmem)
        self.stopbox.setMaximum(self.NITab.NIf.xmaxmem)
        self.startbox.valueChanged.connect(self.updatestartstopboxes)
        self.stopbox.valueChanged.connect(self.updatestartstopboxes)

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

        self.maxlength = 1e6

        NITab.add_tool_widget(self, "FKtraj")

    def updatestartstopboxes(self):
        mi = self.NITab.NIf.xminmem
        ma = self.NITab.NIf.xmaxmem
        self.startbox.setMinimum(mi)
        self.startbox.setMaximum(min(ma, self.stopbox.value()))
        self.stopbox.setMinimum(max(mi, self.startbox.value()))
        self.stopbox.setMaximum(ma)

    def show_transitions(self):
        def extract_integer(filename):
            return int(filename.split("_")[1].split(".")[0])

        f = self.NITab.NIf
        folder = f.path[:-5] + "_analysis/transitions/"
        if os.path.isdir(folder) == 0:
            return
        fl = os.listdir(folder)
        fl = sorted(fl, key=extract_integer)
        mt = np.empty([])
        xt = np.empty([])
        for fi in fl:
            print(fi)
            tr = np.load(folder + fi)
            m = tr["m"] * 180 / np.pi

            xbound = tr["xbound"]
            indphi = int((xbound[0] - self.NITab.NIf.time_off) * self.NITab.NIf.freq)
            if (indphi < self.start) or (indphi > self.stop):
                continue
            nextvalue = (
                self.phi[(indphi - self.start) // self.NITab.NIf.dec] * 180 / np.pi
            )
            print(nextvalue, m[0])
            mh = m[0]
            i = 0
            while nextvalue - mh > 90:
                mh += 180
                i += 1
            while nextvalue - mh < -90:
                mh -= 180
                i -= 1
            m = m + 180 * i

            mt = np.hstack((mt, m))
            xt = np.hstack((xt, xbound))

        self.plotphi.add_ds(xt, mt, stepMode="left", pen="red")

    def set_conv_window(self, x):
        self.convolutionwindow = x

    def set_npoints(self, x):
        self.npoints = x

    def set_timer(self, x):
        self.timer.setInterval(x)

    def set_step(self, x):
        self.step = x

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

    def main_comp(self, progress_callback):
        self.stopbutton.setEnabled(False)
        self.timer.stop()
        self.convolvebutton.setEnabled(False)
        self.displayphi.setEnabled(False)

        print(self.start, self.stop)

        progress_callback.emit(30)

        if (self.stop - self.start) / self.NITab.NIf.dec < self.maxlength:
            (
                phi,
                theta1,
                _,
                _,
                _,
                _,
                _,
            ) = self.NITab.NIf.ret_all_var(
                self.start, self.stop, phiraw=self.rawdatabutton.isChecked()
            )
            self.theta1 = theta1
            # theta2 = np.arcsin(np.sqrt((c45-c135)/(2*Itots2thet*C*ss)))

            progress_callback.emit(70)

            self.v1 = np.column_stack(
                (
                    np.sin(theta1) * np.cos(phi),
                    np.sin(theta1) * np.sin(phi),
                    np.cos(theta1),
                )
            )
            # v2 = np.array([np.sin(theta0)*np.cos(phi0),np.sin(theta0)*np.sin(phi0),np.cos(theta0)])
            # fac = v1.transpose().dot(v2)
            # Itot = Itots2thet / np.sin(theta1)**2
            self.v1[np.isnan(self.v1)] = 0

        else:
            phi = self.NITab.NIf.ret_phi(
                self.start, self.stop, raw=self.rawdatabutton.isChecked()
            )
        self.xs = self.NITab.NIf.ret_xs(self.start, self.stop)
        self.phi = phi
        self.samplesize = len(self.phi)
        self.index = 0
        self.convolvebutton.setEnabled(True)
        self.displayphi.setEnabled(True)

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
        self.text3D.setData(
            text="{:.3f}".format(self.index / self.NITab.NIf.freq * 1000) + "ms"
        )

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
        if len(self.phi) > 0.9 * self.maxlength:
            return

        self.winpg, self.w = self.NITab.plot3D(title="3D plot - FKtraj")

        self.winpg.destroyed.connect(partial(self.wdestroyed, self.winpg))

        color = mkColor("r")
        color.setAlphaF(0.1)
        self.plt = gl.GLScatterPlotItem(
            pos=self.v1, size=0.01, pxMode=False, color=color
        )
        self.w.addItem(self.plt)
        print(len(self.v1))

        color = mkColor("w")
        # pm,tm,tms = fittpline(self.theta1,self.phi,nstep=100)
        # vh = np.column_stack((tms*np.cos(pm),tms*np.sin(pm),np.sqrt(1-tms*tms)))

        # pm,tm,tms = fittplinedensity(self.theta1,self.phi,nstep=100)

        try:
            _, pm, tm = fourier_fit(self.theta1, self.phi, nstep=100)
        except ValueError as e:
            print(f"Error while fitting line {e}")
            vh = None
        else:
            vh = np.column_stack(
                (np.sin(tm) * np.cos(pm), np.sin(tm) * np.sin(pm), np.cos(tm))
            )
            plt = gl.GLLinePlotItem(pos=vh, color=color, width=1)
            self.w.addItem(plt)

        color = mkColor("r")
        color.setAlphaF(1)
        plt = gl.GLScatterPlotItem(
            pos=np.asarray([0, 0, 0]), color=color, size=0.1, pxMode=False
        )
        self.w.addItem(plt)

        color = mkColor("b")
        plt = gl.GLLinePlotItem(
            pos=np.vstack(([0, 0, 0], [0, 0, 2])),
            color=color,
        )  # vertical line
        self.plt.setGLOptions("translucent")

        self.w.addItem(plt)

        color = mkColor("g")
        plt = gl.GLLinePlotItem(
            pos=np.vstack(([0, 0, 0], [0, 2, 0])),
            color=color,
        )  # vertical line
        self.w.addItem(plt)

        self.text3D = gl.GLTextItem(pos=[1, 1, 1], color=color)
        self.w.addItem(self.text3D)

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

    def display_convolution_speed(self):
        self.NITab.plot(
            self.xs,
            self.speed_phi * self.NITab.NIf.freq / 2 / np.pi,
            title="FIR derivative of phi",
            xtitle="Time (s)",
            ytitle="Speed ",
        )

    def display_phi_deg(self):
        self.plotphi = self.NITab.plot(
            self.xs,
            self.phi * 180 / np.pi,
            title="Phi",
            xtitle="Time (s)",
            ytitle="Degrees ",
            pen=None,
            symbolPen="black",
            symbolSize=2,
            symbol="o",
            symbolBrush="black",
        )
