import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), "Helpers"))
sys.path.insert(0, os.path.dirname(sys.path[0]))

from NIfile import NIfile
import re

from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import h5py
import pynumdiff
from pathlib import Path


tdmspath = os.getenv("RODF")
outfolder = os.path.dirname(tdmspath) + "/" + Path(tdmspath).stem + "_analysis/"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
os.environ["RODFAN"] = outfolder

from file_chunker import *

if not os.path.exists(outfolder + "MSD/"):
    os.makedirs(outfolder + "MSD/")
outhist = outfolder + "MSD/"

if not os.path.exists(outfolder + "MSD_res/"):
    os.makedirs(outfolder + "MSD_res/")
outhistres = outfolder + "MSD_res/"


def phi(phi, t1, t2, i=0):
    y = phi[:]
    x = np.linspace(t1, t2, len(y))
    return None, None


def MSD(phi, t1, t2):
    xar = np.arange(1, 200, 1)
    result = np.zeros(len(xar))
    meanresult = np.zeros(len(xar))
    for i in range(len(result)):
        result[i] = np.average((phi[int(xar[i]) :] - phi[: -int(xar[i])]) ** 2)
        meanresult[i] = np.average(phi[int(xar[i]) :] - phi[: -int(xar[i])])
        result[i] = result[i] - meanresult[i] ** 2
    xar = xar / 250000
    a, b = np.polyfit(xar[20:], result[20:], 1)
    a1, b1 = np.polyfit(xar, meanresult, 1)

    f = plt.figure()
    ax = f.gca()
    ax.plot(xar, result)
    ax.plot(
        xar, a * xar + b, label=str(round(2 * np.pi * a1 / a, 1)) + "steps per turn"
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Variance (rad²)")
    plt.legend()
    f.savefig(outfolder + "MSD/MSD_phi_{:.3f}_{:.3f}.png".format(t1, t2))
    plt.close(f)
    return np.array([t1 * 0.5 + t2 * 0.5]), np.array([2 * np.pi * a1 / a])


def speed_savgold(phi, t1, t2):
    params = [2, 1004, 1001]
    x = np.linspace(t1, t2, len(phi))
    dt = x[1] - x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat /= 2 * np.pi
    return x[::10], dydt_hat[::10]


tstart, tmax = 300, 1200
filespeed = file_chuncker(
    tdmspath, 20, speed_savgold, tstart=tstart, tmax=tmax, force=1, dec=100
)
filemsd = file_chuncker(
    tdmspath, 3, MSD, overlap=3, tstart=tstart, tmax=tmax, force=1, dec=1
)

hf = h5py.File(filespeed)
data = hf["data"]


hf = h5py.File(filemsd)
datamsd = hf["data"]

# plt.plot(data[0,:],data[1,:])
# plt.ylabel("Freq (Hz)")
# plt.xlabel("Timee (s)")
# plt.show()

files = [os.path.join(outhist, file) for file in os.listdir(outhist)]
key1 = []
key2 = []

for f in files:
    k = re.findall("\d+\.\d+", f)
    key1.append(float(k[0]))
    key2.append(float(k[1]))


files = [x for _, x in sorted(zip(key1, files))]
key1.sort()
key2.sort()


for i in range(len(files)):
    f = files[i]
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.imshow(mpimg.imread(f))
    ax1.axis("off")
    ax2.plot(data[0, :], data[1, :])
    ax2.set_xlabel("Time(s)")
    ax2.set_ylabel("Freq(Hz)")
    ax3 = ax2.twinx()
    print(key1[i])
    ax2.axvspan(float(key1[i]), float(key2[i]), alpha=0.5, color="red")
    ax3.plot(datamsd[0, :], datamsd[1, :], ".", c="r", markersize=1)
    ax3.set_ylabel("Number of steps per turn")
    ax3.set_ylim([0, 120])
    fig.savefig(outhistres + "file{:d}.png".format(i), dpi=300)
    plt.close(fig)
