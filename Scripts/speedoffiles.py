# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass


if __name__ == "__main__":
    import sys, os, glob

    sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), "Helpers"))
    sys.path.insert(0, os.path.dirname(sys.path[0]))

    from NIfile import NIfile
    import re
    import pynumdiff
    from matplotlib import pyplot as plt
    import matplotlib.image as mpimg
    from scipy import ndimage
    from correction_linearity import *  # or whatever name you want.
    from ECF import *
    import pandas as pd
    from scipy import ndimage, signal
    from sklearn.neighbors import KernelDensity

    plt.style.use(
        "Y:/Martin Rieu/Post-Doc/datoviz/PyQtRod/mr_widget.mplstyle"
    )  # my own style, can remove
    from compute_transitions import *

    xlsx_file_path = "Y:/Martin Rieu/datasummary.xlsx"
    foldersave = "C:/Users/rieu/OneDrive - Nexus365/paper1/Figure 2/"
    dec = 100
    df = pd.read_excel(xlsx_file_path)


def loadenv(tdmspath, startt, stopt, raw=0, decaverage=0):
    global phiu, phir, xt, freq, theta1, Itot, c0, c90, c45, c135

    if decaverage:  # will laod everything and then apply a filter
        f = NIfile(tdmspath, dec=1)
    else:
        f = NIfile(tdmspath, dec=dec)
    print("File of length " + str(len(f.channels[0]) / f.freq) + "s")
    start = int(startt * f.freq)  # starting index to load file from memory
    stop = int(stopt * f.freq)
    print(stop)

    freq = f.freq

    # c0,c90,c45,c135 = f.ret_cor_channel(start,stop) #corrigées au milieu des données
    # Itot = np.mean(c0+c45+c135+c90)
    # _,theta1,_,_ = Fourkas(c0,c90,c45,c135,nw=1.33,NA=1.3)
    phiu = f.ret_phi(start, stop, raw=raw)
    if decaverage:
        window = (1.0 / dec) * np.ones(
            dec,
        )
        phiu = np.convolve(phiu, window, mode="valid")[::dec]
    phir = phiu % (2 * np.pi)
    xt = np.linspace(start, np.min([stop, len(f.channels[0])]), len(phiu)) / f.freq


def analysefile(tdmspath):
    tdmsfolder = tdmspath[:-5] + "_analysis/"
    if not os.path.isdir(tdmsfolder):
        os.mkdir(tdmsfolder)
    dec = 100
    f = NIfile(tdmspath, dec=dec, rawoptics=0, decref=5000, max_size=20000)
    print("File of length " + str(len(f.channels[0]) / f.freq) + "s")
    start, stop = 0, (len(f.channels[0]) / f.freq) - 1

    loadenv(tdmspath, start, stop, raw=1, decaverage=0)

    params = [2, 2000, 200]
    x_hat, dxdt_hat = pynumdiff.linear_model.savgoldiff(phiu, 4e-4, params)

    plt.figure(dpi=200, constrained_layout=True)
    plt.plot(xt, dxdt_hat / 2 / np.pi, color="black")
    plt.xlabel("Time (s)")
    plt.ylabel("Rotation frequency  (Hz)")
    plt.savefig(tdmsfolder + "Speed.png")


folder = "Y:/Martin Rieu/2023_02_10_MTB24/"
fl = os.listdir(folder)
for f1 in fl:
    if f1.endswith(".tdms"):
        analysefile(folder + f1)
