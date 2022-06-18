# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
from PyQt6.QtGui import QPolygonF
from PyQt6.QtCore import QCoreApplication, Qt, QPointF
import numpy as np

QT_API = "pyqt6"

if QT_API == "pyside2":
    import shiboken2 as shiboken
    import ctypes
elif QT_API == "pyside6":
    import shiboken6 as shiboken
    import ctypes
def array2d_to_qpolygonf(xdata, ydata):
    """
    Utility function to convert two 1D-NumPy arrays representing curve data
    (X-axis, Y-axis data) into a single polyline (QtGui.PolygonF object).
    This feature is compatible with PyQt4, PyQt5 and PySide2 (requires QtPy).
    License/copyright: MIT License © Pierre Raybaut 2020-2021.
    :param numpy.ndarray xdata: 1D-NumPy array
    :param numpy.ndarray ydata: 1D-NumPy array
    :return: Polyline
    :rtype: QtGui.QPolygonF
    """
    if not (xdata.size == ydata.size == xdata.shape[0] == ydata.shape[0]):
        raise ValueError("Arguments must be 1D NumPy arrays with same size")
    size = xdata.size
    if QT_API.startswith("pyside"):  # PySide (obviously...)
        if QT_API == "pyside2":
            polyline = QPolygonF(size)
        else:
            polyline = QPolygonF()
            polyline.resize(size)
        address = shiboken.getCppPointer(polyline.data())[0]
        buffer = (ctypes.c_double * 2 * size).from_address(address)
    else:  # PyQt4, PyQt5
        if QT_API == "pyqt6":
            polyline = QPolygonF([QPointF(0, 0)])
            polyline.fill(QPointF(0, 0),size)
        else:
            polyline = QPolygonF(size)
        buffer = polyline.data()
        buffer.setsize(16 * size)  # 16 bytes per point: 8 bytes per X,Y value (float64)
    memory = np.frombuffer(buffer, np.float64)
    memory[: (size - 1) * 2 + 1 : 2] = np.array(xdata, dtype=np.float64, copy=False)
    memory[1 : (size - 1) * 2 + 2 : 2] = np.array(ydata, dtype=np.float64, copy=False)
    return polyline
