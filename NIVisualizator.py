# This Python file uses the following encoding: utf-8
from PyQt6.QtCore import  Qt
from PyQt6.QtCharts import  QScatterSeries, QLineSeries, QValueAxis
from PyQt6.QtGui import  QShortcut,QKeySequence
from qPolygonF import array2d_to_qpolygonf
import numpy as np
import os
class NIVisualizator():
    def __init__(self,view,NIf,DataSlider):
        self.zoomfac = 0.1

        self.view = view
        self.DataSlider = DataSlider


        self.NIf = NIf
        chart = view.chart()
        self.chart = chart
        self.series = []
        axisX = QValueAxis()
        axisX.setRange(0, 5)
        axisX.setLabelFormat("%.3f")
        axisX.setTickCount(7)

        axisY = QValueAxis()
        axisY.setRange(0, 3)
        axisY.setLabelFormat("%.3f")
        axisY.setMinorTickCount(5)

        self.axisX = axisX
        self.axisY = axisY


        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)

        self.init_series_from_file()
        self.define_shortcuts()

    def define_shortcuts(self):
        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.view)
        #self.shortcut.setAutoRepeat(0)
        self.shortcut.activated.connect(self.auto_zoom)
        self.shortcut = QShortcut(QKeySequence("Up"), self.view)
        #self.shortcut.setAutoRepeat(0)
        self.shortcut.activated.connect(self.zoom_in)
        self.shortcut = QShortcut(QKeySequence("Down"), self.view)
        #self.shortcut.setAutoRepeat(0)
        self.shortcut.activated.connect(self.zoom_out)
        self.shortcut = QShortcut(QKeySequence("Left"), self.view)
        #self.shortcut.setAutoRepeat(0)
        self.shortcut.activated.connect(self.go_left)
        self.shortcut = QShortcut(QKeySequence("Right"), self.view)
        #self.shortcut.setAutoRepeat(0)
        self.shortcut.activated.connect(self.go_right)


    def get_visible_pol_channels(self):
         xa,ya,xb,yb = self.get_lim()
         inds = self.NIf.time_to_index_in_mem([xa,xb])
         inda = inds[0]
         indb = inds[1]
         pol_ind = self.NIf.get_pol_ind(["0","90","45","135"])
         c0,c90,c45,c135 = [self.NIf.data[pol_ind[i],:] for i in range(len(pol_ind))]
         return c0[inda:indb],c90[inda:indb],c45[inda:indb],c135[inda:indb]



    def get_visible_pol_channels_raw(self): #return raw and decimated
          xa,ya,xb,yb = self.get_lim()
          inds = self.NIf.time_to_index_in_file([xa,xb])
          inda = inds[0]
          indb = inds[1]
          pol_ind = self.NIf.get_pol_ind(["0","90","45","135"])
          c0,c90,c45,c135 = [self.NIf.channels[pol_ind[i]][inda:indb:self.NIf.dec] for i in range(len(pol_ind))]
          return c0,c90,c45,c135


    def set_visible_channel(self,status,channel):
        if status == 0:
            status = 0
        else:
            status = 1
        if channel >= len(self.series):
            return
        self.series[channel].setVisible(status)


    def change_decimation(self,string):
        new_dec = int(string)
        self.NIf.init_data_share(new_dec,time=self.axisX.min()/2+self.axisX.max()/2)
        self.update_series_from_file()


    def set_a(self,value,channel):
        self.NIf.a[channel] = value
        self.NIf.update_data_from_file(time=-2)
        self.update_series_from_file()
    def set_b(self,value,channel):
        self.NIf.b[channel] = value
        self.NIf.update_data_from_file(time=-2)
        self.update_series_from_file()


    def init_series_from_file(self):
        chart = self.chart

        for i in range(4):

            series = QLineSeries(chart)
            series.setUseOpenGL(1)
            self.series.append(series)
            polygon = array2d_to_qpolygonf(self.NIf.xs, self.NIf.data[i,:])
            series << polygon
            chart.addSeries(series)
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)


            newminx = np.min(self.NIf.xs)
            if i == 0 or newminx < self.minx:
                self.minx = newminx
            newmaxx = np.max(self.NIf.xs)
            if i == 0 or newmaxx > self.maxx:
                 self.maxx = newmaxx

            newminy = np.min(self.NIf.data[i,:])
            if i == 0 or newminy < self.miny:
                        self.miny = newminy
            newmaxy = np.max(self.NIf.data[i,:])
            if i == 0 or newmaxy > self.maxy:
                        self.maxy = newmaxy

        self.auto_zoom()


    def sliderchanged(self,limslider):
        xa,ya,xb,yb = self.get_lim()
        self.set_lim(limslider[0],ya,limslider[1],yb)
        self.auto_zoom_y()


    def update_series_from_file(self):
        for i in range(4):
            series = self.series[i]



            xar = self.NIf.xs
            yar = self.NIf.data[i,:]


            polygon = array2d_to_qpolygonf(xar,yar)

            if len(xar) == self.series[i].count():
                self.series[i].replace(polygon)
            else:
                self.series[i].detachAxis(self.axisX)
                self.series[i].detachAxis(self.axisY)
                self.chart.removeSeries(self.series[i])
                self.series[i].clear()
                self.series[i]<<polygon
                self.chart.addSeries(series)
                self.series[i].attachAxis(self.axisX)
                self.series[i].attachAxis(self.axisY)
            newminx = np.min(xar)
            if i == 0 or newminx < self.minx:
                self.minx = newminx
            newmaxx = np.max(xar)
            if i == 0 or newmaxx > self.maxx:
                 self.maxx = newmaxx

            newminy = np.min(yar)
            if i == 0 or newminy < self.miny:
                        self.miny = newminy
            newmaxy = np.max(yar)
            if i == 0 or newmaxy > self.maxy:
                        self.maxy = newmaxy
        #print(self.minx,self.maxx,self.miny,self.maxy)

        #self.auto_zoom()



    def auto_zoom(self):
                fac = self.zoomfac
                ymin,ymax,xmin,xmax = self.miny,self.maxy,self.minx,self.maxx
                diffy = ymax-ymin
                diffx = xmax-xmin
                self.set_lim(xmin-fac*diffx,ymin-fac*diffy,xmax+fac*diffx,ymax+fac*diffy)



    def auto_zoom_y(self):
            xa,ymin,xb,ymax = self.get_lim()
            fac = self.zoomfac
            ymin,ymax = self.NIf.get_min_max_partial([xa,xb])
            diffy = ymax-ymin
            self.set_lim(xa,ymin-fac*diffy,xb,ymax+fac*diffy)

    def get_lim(self):
        return self.axisX.min(),self.axisY.min(),self.axisX.max(),self.axisY.max()
    def set_lim(self,xa,ya,xb,yb):
        self.axisX.setRange(xa,xb)
        self.axisY.setRange(ya,yb)
        self.DataSlider.setSliderPosition((xa,xb))
        ind= self.NIf.time_to_index_in_file([xa,xb])
        filename = os.path.basename(self.NIf.path)

        self.chart.setTitle(filename + ", [ "+str(ind[0]) + " ... " + str(ind[1]) +"]" + ", Decimation " + str(self.NIf.dec))



        return
    def zoom_in(self):
                xmin,ya,xmax,yb = self.get_lim()
                xcenter = xmin/2 + xmax/2
                diffx = xmax-xmin
                self.set_lim(xcenter-diffx/4,ya,xcenter+diffx/4,yb)
                self.auto_zoom_y()

    def zoom_out(self):
                    xmin,ya,xmax,yb = self.get_lim()
                    xcenter = xmin/2 + xmax/2
                    diffx = xmax-xmin
                    self.set_lim(xcenter-diffx,ya,xcenter+diffx,yb)
                    self.auto_zoom_y()
    def go_to(self,x):
                    xmin,ya,xmax,yb = self.get_lim()
                    diffx = xmax - xmin
                    self.set_lim(x-diffx/2,ya,x+diffx/2,yb)
                    self.auto_zoom_y()


    def go_right(self):
                    xmin,ya,xmax,yb = self.get_lim()
                    diffx = xmax-xmin
                    self.set_lim(xmin+diffx/8,ya,xmax+diffx/8,yb)
                    self.check_NIFile_lim()


    def go_left(self):
                    xmin,ya,xmax,yb = self.get_lim()
                    diffx = xmax-xmin
                    self.set_lim(xmin-diffx/8,ya,xmax-diffx/8,yb)
                    self.check_NIFile_lim()


    def check_NIFile_lim(self):
        xa,ya,xb,yb = self.get_lim()
        mid = xb/2 + xa/2
        if (xb >= self.NIf.maxxmem):
            if (self.NIf.update_data_from_file(mid,norep=1)):
                return
        elif (xa <= self.NIf.minxmem):
            if (self.NIf.update_data_from_file(mid,norep=1)):
                return
        else:
            return
        self.update_series_from_file()
