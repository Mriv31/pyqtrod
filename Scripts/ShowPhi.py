import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), "Helpers"))
sys.path.insert(0, os.path.dirname(sys.path[0]))

from file_chunker import *
from NIfile import NIfile
from matplotlib import pyplot as plt
import h5py

tdmspath = os.getenv("RODF")
print(tdmspath)


def phi(phi, t1, t2, i=0):
    y = phi[:]
    x = np.linspace(t1, t2, len(y))
    return x, y


file = file_chuncker(tdmspath, 10, phi, tstart=0, tmax=-1, i=1, force=1, dec=100)

hf = h5py.File(file)
data = hf["data"]
plt.plot(data[0, :], np.unwrap(data[1, :], period=np.pi))
plt.show()
