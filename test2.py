import pyqtgraph as pg
import numpy as np

pg.mkQApp()

pw = pg.PlotWidget()
pw.show()

pw.setClipToView(True)
pw.enableAutoRange(False)
pw.setDownsampling(ds=None, auto=True, mode="subsample")
data = np.sin(np.arange(100000000)) + np.random.normal(0, 10, 100000000)
np.save("test.npy", data)
pdi = pw.plot()
pdi.setData(data)

pg.exec()
