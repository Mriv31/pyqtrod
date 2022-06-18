# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
import numpy as np
import scipy.optimize as optimize




class ComputeCoeffs(QtWidgets.QWidget):
    def __init__(self,NITab):
        super(QtWidgets.QWidget, self).__init__()
        uic.loadUi('Modules/ComputeCoeffs.ui', self)
        NITab.add_tool_widget(self,"ComputeCoeffs")
        self.NITab = NITab
        pass

    def func_to_min(self,params):
        a90,a45,a135 = params
        return np.sum((self.c0 + a90*self.c90 - self.c45*a45-self.c135*a135)**2)

    def compute_coeffs(self):
        self.c0,self.c90,self.c45,self.c135 = self.NITab.NIv.get_visible_pol_channels()
        minb = 0
        maxb = 1.5
        initial_guess = [1, 1, 1]
        bounds = [(minb,maxb)]*3
        result = optimize.minimize(self.func_to_min, initial_guess,bounds=bounds)
        if result.success:
            fitted_params = result.x
            print(fitted_params)
        else:
            raise ValueError(result.message)
        l90,l45,l135 = fitted_params
        self.NITab.plot(self.c0+self.c90,self.c45+self.c135,title="Before correction",xtitle="C0 + C90",ytitle="C45+C135")
        self.NITab.plot(self.c0+l90*self.c90,self.c45*l45+self.c135*l135,title="After correction",xtitle="C0 + C90",ytitle="C45+C135")
        self.NITab.NIf.a[self.NITab.NIf.ret_index_by_pol("90")] *= l90
        self.NITab.NIf.a[self.NITab.NIf.ret_index_by_pol("45")] *= l45
        self.NITab.NIf.a[self.NITab.NIf.ret_index_by_pol("135")] *= l135
        self.NITab.update_coeffs_buttons()
