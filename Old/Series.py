# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QCoreApplication, Qt, QPointF
from PyQt6.QtCharts import QChartView, QChart, QScatterSeries, QLineSeries
from PyQt6.QtGui import QPolygonF
import numpy as np
import ctypes
import time

QT_API = "pyqt6"

if QT_API == "pyside2":
    import shiboken2 as shiboken
    import ctypes
elif QT_API == "pyside6":
    import shiboken6 as shiboken
    import ctypes



def series_to_polyline(xMap, yMap, series, from_, to):
    """
    Convert series data to QPolygon(F) polyline
    """
    xdata = xMap.transform(series.xData()[from_ : to + 1])
    ydata = yMap.transform(series.yData()[from_ : to + 1])
    return array2d_to_qpolygonf(xdata, ydata)


ar = np.arange(1e7,dtype=np.float32)
ar2 = np.arange(1e7,dtype=np.float32)

series = QLineSeries(chart)
series2 = QLineSeries(chart)

#for i in np.arange(0,1,1e-6):
#     series.append(i,i)
#     series2.append(i,i**2)

series.setUseOpenGL(1)
series2.setUseOpenGL(1)
tic = time.perf_counter()
polygon = array2d_to_qpolygonf(ar, ar2)
toc = time.perf_counter()
print(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")


tic = time.perf_counter()
chart = window.mainview.chart()


series << polygon
toc = time.perf_counter()


print(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")


tic = time.perf_counter()


for i in range(10000000):
    series.append(QPointF(i,i))
toc = time.perf_counter()


print(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")


chart.addSeries(series)


chart.addSeries(series2)
