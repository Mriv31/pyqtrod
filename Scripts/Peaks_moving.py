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
from scipy.signal import find_peaks
import numpy as np


tdmspath = os.getenv("RODF")
outfolder = os.path.dirname(tdmspath) + "/" + Path(tdmspath).stem + "_analysis/"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
os.environ["RODFAN"] = outfolder

from file_chunker import *

if not os.path.exists(outfolder + "histograms/"):
    os.makedirs(outfolder + "histograms/")
outhist = outfolder + "histograms/"

if not os.path.exists(outfolder + "histograms_peaks/"):
    os.makedirs(outfolder + "histograms_peaks/")
outhistrespeaks = outfolder + "histograms_peaks/"


hf = h5py.File(outfolder + "speed_savgold_tstart_540_tstop_600_.h5")
data1 = hf["data"]

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


def peaks_by_fit(peaks, n, width):
    r = []
    x = []
    sig = []
    for p in peaks:
        if p - width < 0:
            continue
        if p + width > len(n):
            continue
        xar = range(p - width, p + width)
        a, b, c = np.polyfit(xar, n[p - width : p + width], 2)
        # plt.plot(xar,a*xar*xar+b*xar+c)

        r.append(c - b * b / 4 / a)
        x.append(-b / 2 / a)
        sig.append(1 / 2 / a)  # sigsquare
    return x, r, sig


def find_peakkk(n2):
    n1 = np.log(n2)
    for j in range(3):
        ind = find_peaks(n1, prominence=0.1)
        ind = ind[0]
        xp, rp, sig = peaks_by_fit(ind, n1, int(len(n) / 100))
        ind = np.asarray(xp).astype("int")
    return xp, np.exp(rp), sig


pl = []
sigs = []
tp = []
for i in range(len(files)):
    f = files[i]
    data = np.load(f)
    b = data[0, :] * 360 / 2 / np.pi
    n = data[1, :]
    ph = find_peakkk(n)

    tp.extend(
        [0.5 * float(key1[i]) + 0.5 * float(key2[i])] * len(ph[0])
    )  # time of each peak
    peaks = np.array(ph[0]) * (b[1] - b[0])
    peaks = peaks.tolist()
    s = np.array(ph[2]) * (b[1] - b[0]) ** 2
    s = s.tolist()
    sigs.extend(s)
    pl.extend(peaks)

    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.bar(b, n, width=b[1] - b[0])
    ax1.plot(peaks, ph[1], ".", color="red")
    ax1.set_xlim([0, 360])
    ax2.plot(data1[0, :], data1[1, :])
    ax2.set_xlabel("Time(s)")
    ax2.set_ylabel("Freq(Hz)")
    ax3 = ax2.twinx()
    ax2.axvspan(float(key1[i]), float(key2[i]), alpha=0.5, color="red")
    fig.savefig(outhistrespeaks + "file{:d}.png".format(i), dpi=300)
    plt.close(fig)


res = np.zeros([3, len(sigs)])
res[2, :] = sigs  # degré
res[1, :] = pl  # degré
res[0, :] = tp  # temps (s)
for i in range(len(files)):
    plt.plot(res[0, :], res[1, :], ".")
np.save(outfolder + "peaks.npy", res)
plt.show()
