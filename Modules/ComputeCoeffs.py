# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
import numpy as np
import scipy.optimize as optimize
import corr_matrix
import importlib
importlib.reload(corr_matrix)
from corr_matrix import *



class ComputeCoeffs(QtWidgets.QWidget):
    def __init__(self,NITab):
        super(QtWidgets.QWidget, self).__init__()
        uic.loadUi('Modules/ComputeCoeffs.ui', self)
        NITab.add_tool_widget(self,"ComputeCoeffs")
        self.NITab = NITab

        pass


    def compute_coeffs(self):


        self.c0,self.c90,self.c45,self.c135 = self.NITab.NIv.get_visible_pol_channels()
        self.NITab.plot(self.c0+self.c90,self.c45+self.c135,title="Before correction",xtitle="C0 + C90",ytitle="C45+C135")





        self.c0,self.c90,self.c45,self.c135 = self.NITab.NIv.get_visible_pol_channels_raw()

        par =  find_best_coeff_using_mat(self.c0,self.c90,self.c45,self.c135,self.NITab.NIf.matcorb) #must be used on raw data since apply matrix matcorb is the matrix in the 0,90,45,135 base

        l90,l45,l135 = par.x

        self.NITab.NIf.a[self.NITab.NIf.ret_index_by_pol("90")] = l90
        self.NITab.NIf.a[self.NITab.NIf.ret_index_by_pol("45")] = l45
        self.NITab.NIf.a[self.NITab.NIf.ret_index_by_pol("135")] = l135

        self.NITab.NIf.update_data_from_file(time=-2)
        self.c0,self.c90,self.c45,self.c135 = self.NITab.NIv.get_visible_pol_channels()


        self.NITab.plot(self.c0+self.c90,self.c45+self.c135,title="After correction",xtitle="C0 + C90",ytitle="C45+C135")
        self.NITab.update_coeffs_buttons()
