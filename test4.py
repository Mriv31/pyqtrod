import pyqtgraph as pg
import numpy as np

pg.mkQApp()
pw = pg.PlotWidget()
pw.setClipToView(True)
pw.enableAutoRange(False)
pw.setDownsampling(ds=None, auto=1, mode="subsample")
data = np.arange(10000000)+np.random.normal(0,10,10000000)
pw.plot(data, title="Simplest possible plotting example")
pw.show()
pg.exec()
