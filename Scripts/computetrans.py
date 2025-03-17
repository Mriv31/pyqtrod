import numpy as np
from pyqtrod.ni_file import NIfile
from pyqtrod.helpers.compute_transitions import compute_transitions
import os

import pandas as pd

if __name__ == "__main__":
    xlsx_file_path = "Y:/Martin Rieu/datasummary.xlsx"
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
    xar = None
    peaks = None
    fit = None
    raw = 1
    if row["c2"] == "PotAb cell 1":
        data = np.load("C:/Users/rieu/OneDrive - Nexus365/paper1/PotAB_cell1_peaks.npz")
        xar = data["xar"]
        peaks = data["peaks"]
        raw = 0
        fit = data["fit"]
    else:
        continue
    f = NIfile(tdmspath, dec=1)
    lt = f.datasize / f.freq - 5
    win = 10
    start = row["Start"]
    stop = start + win
    while stop < lt:
        print(tdmspath, start, stop)
        phiu = f.ret_phi(int(start * f.freq), int(stop * f.freq), raw=raw)
        xt = np.linspace(start, np.min([stop, f.datasize / f.freq]), len(phiu))
        of = save_folder + f"trans_{start}_to_{stop}.npz"
        compute_transitions(
            of, xt, phiu, xar=xar, peaks=peaks, fit=fit, pen=0.1, min_segment_size=5
        )
        start += win
        stop += win
