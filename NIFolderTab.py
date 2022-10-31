# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets, uic, QtGui
from PyQtGraph import PyQtGraph,PyQtGraphGrid
import os, glob
import numpy as np
from PyQtFunc import *
from NIfile import NIfile

class NIFolderTab(QtWidgets.QMainWindow):
    def __init__(self,NIfolder):
        super(NIFolderTab, self).__init__()
        self.nexti = 0
        self.nextj = 0

        self.fold = NIfolder
        self.layout = QtWidgets.QGridLayout()

        self.scrolled = QtWidgets.QScrollArea()

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(self.scrolled)
        self.scrolled.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrolled.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrolled.setWidgetResizable(True)
        self.scrolled.setWidget(widget)
        self.maxcol = 1
        os.chdir(self.fold)
        self.files = glob.glob("*.tdms")
        self.displayFiles()
        pass

    def displayFiles(self):
        for f in self.files:
            self.addGridWidget(f)

    def addGridWidget(self,file):
        w = PyQtGraphGrid(title=file)
        if self.displayNIfileSum(file,w):
            return
        self.layout.addWidget(w,self.nexti,self.nextj)

        self.increment_grid()

    def increment_grid(self):
        if self.nextj>=self.maxcol:
            self.nextj=0
            self.nexti+=1
            return
        else:
            self.nextj+=1

    def displayNIfileSum(self,file,w):
        try:
            Nif = NIfile(file,dec=1)
        except:
            print("Error loading file "+file)
            return 1
        c0,c90,c45,c135=Nif.full_ordered_pol()
        x,y = anisotropies(c0,c45,c90,c135)
        w.addPlot(x,y,xtitle="Anisotropy 0/90",ytitle="Anisotropy 45/135")
        x,y = PSF(c0)
        w.addPlot(x,y,logx=1,logy=1,xtitle="Freq (Hz)",ytitle="PSD (V²/Hz)")
        w.addPlot(c0,c90,xtitle="c0",ytitle="c90")
        w.addPlot(c45,c135,xtitle="c45",ytitle="c135")
        return 0



