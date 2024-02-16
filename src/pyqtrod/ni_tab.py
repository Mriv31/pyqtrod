# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from functools import partial
from .ni_visualizator import NIVisualizator
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from importlib import import_module, reload
import importlib.resources
import inspect
import importlib.resources as pkg_resources

from .module_dialog import ModuleDialog
from .matrix_dialog import MatrixDialog, MatrixChoose

from pynavgui import PngPlotRegionGrid

import numpy as np

modules_root = "pyqtrod.modules"


class NITab(QtWidgets.QMainWindow):
    def __init__(self, NIf, threadpool, png_instance=None):
        super(NITab, self).__init__()
        self.NIf = NIf
        self.png_instance = png_instance
        self.threadpool = threadpool
        with pkg_resources.path("pyqtrod", "ni_tab.ui") as ui_path:
            uic.loadUi(ui_path, self)
        # self.choose_matrix_menu()
        self.init_plot_main()

        self.set_file_properties()
        self.pols = [self.pol0, self.pol1, self.pol2, self.pol3]
        self.decimatebox.setCurrentText(str(self.NIf.dec))
        self.set_pol_decim_buttons()
        self.init_pol_from_NIf_default()
        self.init_load_as_seen()
        self.setslider()
        self.n_modules = 0
        self.set_coeffs_buttons()
        self.toolmodules = []

        self.imported_modules = []
        # Install event filter
        self.installEventFilter(self)
        self.set_memory_text()
        self.load_all_modules()

    def load_all_modules(self):
        with importlib.resources.path(modules_root, "") as modules_path:
            fl = [
                f.stem
                for f in modules_path.iterdir()
                if (
                    f.is_file()
                    and f.as_posix().endswith(".py")
                    and not f.as_posix().endswith("__.py")
                )
            ]
        fl2 = []
        for f in fl:
            if not f.endswith("beta.py"):
                fl2.append(f)
        for t in fl2:
            self.load_module(t)

    def load_module_menu(self):
        with importlib.resources.path(modules_root, "") as modules_path:
            fl = [
                f.stem
                for f in modules_path.iterdir()
                if (
                    f.is_file()
                    and f.as_posix().endswith(".py")
                    and not f.as_posix().endswith("__.py")
                )
            ]
        fl2 = []
        for f in fl:
            fl2.append(f)
        dialog = ModuleDialog("Module Dialog", stringlist=fl2)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            list_selected_modules = dialog.get_selected_modules()
        else:
            return
        for t in list_selected_modules:
            self.load_module(t)

    def edit_matrix_menu(self):
        dialog = MatrixDialog("Edit correction matrix", mat=self.NIf.matcor)
        dialog.exec()
        self.NIf.update_data_from_file(time=-2)
        self.NIv.update_series_from_file()

    def choose_matrix_menu(self):
        dialog = MatrixChoose("Choose correction matrix", file=self.NIf)
        dialog.exec()
        self.NIf.update_data_from_file(time=-2)
        self.NIv.update_series_from_file()

    def load_module(self, module):  # load or reload
        def get_class_from_module(module):
            classes = [
                member
                for member in inspect.getmembers(module, inspect.isclass)
                if member[1].__module__ == module.__name__
            ]
            if len(classes) == 1:
                return classes[0][1]  # Returns the name of the class
            elif len(classes) > 1:
                raise ValueError("Module contains more than one class.")
            else:
                raise ValueError("No classes found in the module.")

        module_name = f"{modules_root}.{module}"
        found = 0
        for i in range(len(self.imported_modules)):
            m, mn = self.imported_modules[i]
            if mn == module_name:
                found = 1
                module = reload(m)
                self.imported_modules[i][0] = module
                break
        if found == 0:
            module = import_module(module_name)
            self.imported_modules.append([module, module_name])
        try:
            # Try to get the class object from the module
            class_obj = get_class_from_module(module)

            # Create an instance of the class
            instance = class_obj(self)
            print("Created instance:", instance)
        except ValueError as e:
            print(f"Error: {e}")

    def add_tool_widget(self, widget, name):
        if self.toolmodules == []:
            self.toolbox = QtWidgets.QToolBox()
            self.dockanalysis.setWidget(self.toolbox)
        else:
            for i in range(len(self.toolmodules)):
                w, n, ind = self.toolmodules[i]
                if n == name:
                    del self.toolmodules[i]
                    # w.hide()
                    self.toolbox.removeItem(ind)
                    for j in range(len(self.toolmodules)):
                        w2, n2, ind2 = self.toolmodules[j]
                        if ind2 >= ind:
                            self.toolmodules[j][2] -= 1
                    break
        ind = self.toolbox.addItem(widget, name)
        self.toolmodules.append([widget, name, ind])

    def init_plot_main(self):
        self.colors_plot_main = ["r", "g", "b", "orange"]
        for i in range(len(self.NIf._channels)):
            if i == 0:
                self.plotmain = self.plot(
                    self.NIf.xs,
                    self.NIf.data[i],
                    no_quit=True,
                    name=f"""{self.NIf.channelnames[0]}
                    ({self.NIf.orientations[0]}°)""",
                    pen=self.colors_plot_main[i],
                )
            else:
                self.plotmain.add_ds(
                    self.NIf.xs,
                    self.NIf.data[i],
                    name=f"""{self.NIf.channelnames[i]}
                    ({self.NIf.orientations[i]}°)""",
                    pen=self.colors_plot_main[i],
                )

    def update_plot_main(self):
        self.plotmain.clear()
        for i in range(len(self.NIf._channels)):
            self.plotmain.add_ds(
                self.NIf.xs,
                self.NIf.data[i],
                name=f"""{self.NIf.channelnames[i]}
                    ({self.NIf.orientations[i]}°)""",
                pen=self.colors_plot_main[i],
            )

    def get_visible_pol_channels(self):
        xa, xb = self.plotmain.viewRange()[0]
        c0, c90, c45, c135 = self.NIf.ret_cor_channel(xa, xb)
        return c0, c90, c45, c135

    def get_visible_pol_channels_raw(self):  # return raw and decimated
        xa, xb = self.plotmain.viewRange()[0]
        c0, c90, c45, c135 = self.NIf.ret_raw_channel(xa, xb)
        return c0, c90, c45, c135

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.key() in [QtCore.Qt.Key.Key_Right, QtCore.Qt.Key.Key_Left]:
            if self.load_as_seen:
                self.update_loaded_file()
        (a, b) = self.plotmain.viewRange()[0]
        self.DataSlider.setValue((a, b))

    # def eventFilter(self, source, event):
    #     if event.type() == QtCore.QEvent.KeyRelease:
    #         # Handle the key event here

    #         if event.key() in [QtCore.Qt.Key.Key_Right, QtCore.Qt.Key.Key_Left]:
    #             if self.load_as_seen:
    #                 self.update_loaded_file()
    #     return super().eventFilter(source, event)

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
            nb.valueChanged.connect(partial(self.set_a, channel=i))
            self.abut.append(nb)

            label = QtWidgets.QLabel()
            layout2.addWidget(label)
            label.setText("b")

            nb = QtWidgets.QDoubleSpinBox()
            layout2.addWidget(nb)
            nb.setValue(self.NIf.b[i])
            nb.setMinimum(-3)
            nb.valueChanged.connect(partial(self.set_b, channel=i))
            self.bbut.append(nb)

        button = QtWidgets.QPushButton("Save coefficient to file")
        button.clicked.connect(self.NIf.save_coeff_to_file)
        layout.addWidget(button)
        self.toolBox_2.addItem(qg, "Corr coeffs")

    def set_a(self, value, channel):
        self.NIf.a[channel] = value
        self.NIf.update_data_from_file(time=-2)
        self.update_plot_main()

    def set_b(self, value, channel):
        self.NIf.b[channel] = value
        self.NIf.update_data_from_file(time=-2)
        self.update_plot_main()

    def update_coeffs_buttons(self):
        for i in range(4):
            self.abut[i].setValue(self.NIf.a[i])
            self.bbut[i].setValue(self.NIf.b[i])

    def set_file_properties(self):
        self.filepathdisplay.setText(self.NIf.path)
        self.groupnbdisplay.setText(str(self.NIf.groupnb))
        self.freqdisplay.setText(str(round(self.NIf.freq / 1000)))
        self.startTimedisplay.setDateTime(
            QtCore.QDateTime.fromSecsSinceEpoch(
                int(self.NIf.starttime.astype("int") / 1e6)
            )
        )  # trick will need to correct that if dates become incorrect
        self.lengthptsdisplay.setText("{:.3e}".format(self.NIf.datasize))
        self.lengthmindisplay.setText(
            "{:.2f}".format(self.NIf.datasize / self.NIf.freq / 60)
        )
        self.labelchannel0.setText(self.NIf.channelnames[0])
        self.labelchannel1.setText(self.NIf.channelnames[1])
        self.labelchannel2.setText(self.NIf.channelnames[2])
        self.labelchannel3.setText(self.NIf.channelnames[3])
        pass

    def set_pol_decim_buttons(self):
        for i in range(4):
            self.pols[i].currentTextChanged.connect(
                partial(self.set_pol_channel, channel=i)
            )
        self.start_load_in_mem.setValue(self.NIf.xminmem)
        self.stop_load_in_mem.setValue(self.NIf.xmaxmem)
        self.stop_load_in_mem.setMaximum(self.NIf.datasize / self.NIf.freq)
        self.stop_load_in_mem.valueChanged.connect(self.start_load_in_mem.setMaximum)
        self.start_load_in_mem.setMaximum(self.stop_load_in_mem.value())
        self.decimatebox.currentTextChanged.connect(lambda: self.indicate_loaded_size())
        self.decimatebox.currentTextChanged.connect(self.NIf.set_dec)

        self.stop_load_in_mem.valueChanged.connect(lambda: self.indicate_loaded_size())
        self.start_load_in_mem.valueChanged.connect(lambda: self.indicate_loaded_size())
        self.decimation_averaged.setChecked(self.NIf.dec_average)
        self.decimation_averaged.stateChanged.connect(self.set_dec_average)

        self.button_load_as_seen.stateChanged.connect(self.set_load_as_seen)

        self.DataSlider.setValue((self.NIf.xminmem, self.NIf.xmaxmem))

        self.loadinmem.clicked.connect(self.update_loaded_file)

    def set_dec_average(self, value):
        self.NIf.dec_average = bool(value)
        self.update_loaded_file()

    def init_load_as_seen(self):
        self.button_load_as_seen.setChecked(True)
        self.set_load_as_seen(True)

    def set_load_as_seen(self, state):
        if state == 0:
            self.load_as_seen = False
            self.NIf.max_size = int(1e9)
        else:
            self.load_as_seen = True
            self.NIf.max_size = int(self.max_size.value())
            self.NIf.init_data_share(
                int(self.decimatebox.currentText()),
                timestart=self.start_load_in_mem.value(),
                timestop=self.stop_load_in_mem.value(),
            )
            self.update_plot_main()
        self.loadinmem.setEnabled(not self.load_as_seen)

    def indicate_loaded_size(self):
        self.nb_points_to_load_in_mem.setWordWrap(True)
        nb_points = int(
            self.NIf.freq
            * (self.stop_load_in_mem.value() - self.start_load_in_mem.value())
            / int(self.decimatebox.currentText())
        )
        memory = 4 * self.NIf.data.dtype.itemsize * nb_points / 1e6
        self.nb_points_to_load_in_mem.setText(
            f"Corresponding to roughly {nb_points} points and {memory} MB of memory."
        )

    def update_loaded_file(self):
        if self.load_as_seen is False:
            timestart = self.start_load_in_mem.value()
            timestop = self.stop_load_in_mem.value()
            dec = int(self.decimatebox.currentText())
            self.NIf.init_data_share(
                dec,
                timestart=timestart,
                timestop=timestop,
            )
            self.DataSlider.setValue((self.NIf.xminmem, self.NIf.xmaxmem))
            self.update_plot_main()
        else:
            (a, b) = self.plotmain.viewRange()[0]
            self.DataSlider.setValue((a, b))
            if (b > self.NIf.xmaxmem) or (a < self.NIf.xminmem):
                self.NIf.update_data_from_file(time=0.5 * a + 0.5 * b)
                self.update_plot_main()
            (a, b) = self.plotmain.viewRange()[0]
            self.DataSlider.setValue((a, b))
        self.set_memory_text()

    def set_memory_text(self):
        self.info_data_loaded.setText(
            f""" NOW IN MEMORY: <b style="color:Tomato;">Decimation</b> : {self.NIf.dec_in_mem} \n
  <b style="color:Tomato;">Averaged</b> : {self.NIf.dec_average_in_mem} \n 
    <b style="color:Tomato;">Loaded from</b> : {round(self.NIf.xminmem,2)} s \n
  <b style="color:Tomato;">Loaded to</b> : {round(self.NIf.xmaxmem,2)} s
"""
        )

    def setslider(
        self,
    ):
        self.DataSlider.setMinimum(0)
        self.DataSlider.setMaximum(self.NIf.datasize / self.NIf.freq)
        # self.DataSlider.setHandleLabelPosition(LabelPosition.NoLabel)
        self.DataSlider.valueChanged.connect(self.sliderchanged)

    def sliderchanged(self, value):
        return
        self.plotmain.setXRange(value[0], value[1])

    def init_pol_from_NIf_default(self):
        for i in range(4):
            self.pols[i].setCurrentText(self.NIf.orientations[i])

    def set_pol_channel(self, string, channel):
        current_strings = []
        p = ["0", "45", "90", "135"]
        str_to_change = string
        for i in range(4):
            current_strings.append(str(self.pols[i].currentText()))
        for i in range(4):
            if current_strings.count(p[i]) == 2:
                str_to_change = p[i]
            if current_strings.count(p[i]) == 0:
                new_value = p[i]

        for i in range(4):
            if i != channel:
                if current_strings[i] == str_to_change:
                    self.pols[i].setCurrentText(new_value)
        self.NIf.orientations[channel] = string

    def get_current_active_widget(self):
        ac_subwindow = self.mdiArea.activeSubWindow()
        cw = ac_subwindow.widget()
        return cw

    def plot(self, x, y, title="", xtitle="", ytitle="", no_quit=False, **kwargs):
        winpg = QtWidgets.QMdiSubWindow()
        winpg.setWindowTitle(title)
        self.mdiArea.addSubWindow(winpg)
        w = PngPlotRegionGrid(title=title, png_instance=self.png_instance)
        winpg.setWidget(w)
        ph = w.addPlot(x=x, y=y, xtitle=xtitle, ytitle=ytitle, **kwargs)
        if no_quit:
            winpg.setWindowFlags(
                QtCore.Qt.WindowType.CustomizeWindowHint
                | QtCore.Qt.WindowType.WindowTitleHint
                | QtCore.Qt.WindowType.WindowMinMaxButtonsHint
                | QtCore.Qt.WindowType.SubWindow
            )
        winpg.show()
        return ph

    def plot3D(self, title="", xtitle="", ytitle=""):
        winpg = QtWidgets.QMdiSubWindow()
        winpg.setWindowTitle(title)
        self.mdiArea.addSubWindow(winpg)
        w = gl.GLViewWidget()
        w.setBackgroundColor("k")
        w.setWindowTitle(title)
        w.setCameraPosition(distance=40)
        winpg.setWidget(w)
        winpg.show()
        winpg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        return winpg, w

    def plot3D2D(self, title="", xtitle="", ytitle=""):
        winpg = QtWidgets.QMdiSubWindow()
        winpg.setWindowTitle(title)
        widget = QtWidgets.QWidget()
        winpg.setWidget(widget)
        self.mdiArea.addSubWindow(winpg)
        w = gl.GLViewWidget()
        w.setBackgroundColor("k")
        w.setWindowTitle(title)
        w.setCameraPosition(distance=40)
        layoutgb = QtWidgets.QGridLayout()
        widget.setLayout(layoutgb)
        ploth = pg.PlotWidget(title=title)
        ploth.enableAutoRange(True, True)
        layoutgb.addWidget(w, 0, 0)
        layoutgb.addWidget(ploth, 0, 1)
        winpg.show()
        winpg.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        ploth.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        w.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        w.setSizePolicy(ploth.sizePolicy())
        return winpg, w, ploth
