# This Python file uses the following encoding: utf-8
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets, uic, QtGui
from PyMRGraph import *
import os, glob
import numpy as np
from PyQtFunc import *
from NIfile import NIfile
from PIL import Image

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
        self.files = glob.glob(self.fold+"/*.tdms")
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
            Nif = NIfile(file,dec=1,max_size=100000)
        except:
            print("Error loading file "+file)
            return 1
        c0,c90,c45,c135=Nif.full_ordered_pol()
        x,y = anisotropies(c0,c45,c90,c135)
        w.addScatterPlot(x=x[:40000],y=y[:40000],xtitle="Anisotropy 0/90",ytitle="Anisotropy 45/135")
        x,y = PSD(c0+c45+c90+c135,nperseg=10000,nfft=40000,noverlap=5000)
        w.addPlot(x=x,y=y,legend=1,dsdes="Sum",logx=1,logy=1,xtitle="Freq (Hz)",ytitle="PSD (V²/Hz)")
        #w.addPlot(c0,c90,xtitle="c0",ytitle="c90")
        #w.addPlot(c45,c135,xtitle="c45",ytitle="c135")

        try:
            im = np.asarray(Image.open(file[:-4]+"tiff"))
            w.addImage(im)
        except:
            print("No Image file associated to file")

        I0 = (c0 - c90) / (c0 + c90)
        I1 = (c45 - c135) / (c45 + c135)
        x = I0 + 1.j * I1
        x,y = PSD(x,nperseg=10000,nfft=40000,noverlap=5000)
        ind = np.where(np.logical_and(x<1500,x>-1500))
        w.addPlot(x=x[ind],y=y[ind],logx=0,logy=1,xtitle="Freq (Hz)",ytitle="PSD (V²/Hz)")


        return 0



