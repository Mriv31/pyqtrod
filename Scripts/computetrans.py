import numpy as np
import multiprocessing


if __name__ == "__main__":
    import sys, os, glob

    sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), "Helpers"))
    sys.path.insert(0, os.path.dirname(sys.path[0]))

    from NIfile import NIfile
    import re

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
    dec = 1
    df = pd.read_excel(xlsx_file_path)


for index, row in df.iterrows():
    # Access data in each column using the key from the first row
    if row["Transition Analysis"] != 1:
        continue
    path = "Y:/Martin Rieu/" + row["Folder"] + "/" + row["File"][:-5] + "_analysis/"
    tdmspath = "Y:/Martin Rieu/" + row["Folder"] + "/" + row["File"]
    save_folder = (
        "Y:/Martin Rieu/"
        + row["Folder"]
        + "/"
        + row["File"][:-5]
        + "_analysis/transitions/"
    )
    if os.path.isdir(save_folder) == 0:
        os.mkdir(save_folder)
    f = NIfile(tdmspath, dec=1)
    lt = len(f.channels[0]) / f.freq - 5
    win = 10
    start = row["Start"]
    stop = win
    while stop < lt:
        print(tdmspath, start, stop)
        phiu = f.ret_phi(int(start * f.freq), int(stop * f.freq), raw=1)
        xt = np.linspace(start, np.min([stop, len(f.channels[0])]), len(phiu))
        of = save_folder + f"trans_{start}_to_{stop}.npz"
        compute_transitions(of, xt, phiu, None, None, pen=0.1, min_segment_size=5)
        start += win
        stop += win
