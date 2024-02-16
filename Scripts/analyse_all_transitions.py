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
    from pathlib import Path
    from scipy import ndimage
    from correction_linearity import *  # or whatever name you want.
    from transition_analysis import *
    from ECF import *
    import pandas as pd
    import itertools
    from scipy import ndimage, signal
    from sklearn.neighbors import KernelDensity

    plt.style.use(
        "Y:/Martin Rieu/Post-Doc/datoviz/PyQtRod/mr_widget.mplstyle"
    )  # my own style, can remove

    xlsx_file_path = "Y:/Martin Rieu/datasummary.xlsx"
    foldersave = "C:/Users/rieu/OneDrive - Nexus365/paper1/Fig 3/"
    dec = 1
    df = pd.read_excel(xlsx_file_path)

iex = 0
iind = 0
im = 0

plt.figure()
if __name__ == "__main__":
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    markers = ["x", ".", "^", ">"]  # Marker styles
    all_t_l = []
    # Loop through the rows and read columns using the keys in the first row
    for index, row in df.iterrows():
        # Access data in each column using the key from the first row
        if row["Transition Analysis"] != 1:
            continue
        path = "Y:/Martin Rieu/" + row["Folder"] + "/" + row["File"][:-5] + "_analysis/"

        fl = os.listdir(path)
        alth = []
        all_t_l.append(alth)

        for f in fl:
            if (f.startswith("transitions") != 1) or (f.endswith(".npz") != 1):
                continue
            print(f)
            transitions = np.load(path + f, allow_pickle=True)
            transitionar = transitions["transitionar"]
            meanall = transitions["meanall"]
            meantime = transitions["meantime"]
            meanz = transitions["meanz"]
            timess = transitions["timess"]
            durations = transitions["durations"]
            rawtr = transitions["rawtr"]

            peaks = transitions["peaks"]
            xar = transitions["xar"]
            xbound = transitions["xbound"]
            indli = transitions["indli"]
            xboundraw = transitions["xboundraw"]
            m = transitions["m"]

            all_t, all_t_up, all_t_down = summarize_transition_stats(
                peaks, timess, do_double=0
            )
            combinations = list(itertools.combinations(range(all_t.shape[0]), 2))
            for i, j in combinations:

                if len(timess[i, j]) > 10:
                    #                    if (all_t[i,j] ==0):
                    #                        print(timess[i,j])
                    plt.errorbar(
                        [iind],
                        all_t[i, j],
                        yerr=[
                            [all_t[i, j] - all_t_down[i, j]],
                            [all_t_up[i, j] - all_t[i, j]],
                        ],
                        color=color_cycle[iex % len(color_cycle)],
                        marker=markers[im % len(markers)],
                    )
                    iind += 1
                    alth.append(all_t[i, j])

                if len(timess[j, i]) > 10:
                    plt.errorbar(
                        [iind],
                        [all_t[j, i]],
                        yerr=[
                            [all_t[j, i] - all_t_down[j, i]],
                            [all_t_up[j, i] - all_t[j, i]],
                        ],
                        color=color_cycle[iex % len(color_cycle)],
                        marker=markers[im % len(markers)],
                    )
                    iind += 1
                    alth.append(all_t[i, j])

                im += 1

        iex += 1
    plt.show(block=True)
    plt.figure()
    plt.boxplot(all_t_l, bootstrap=100)
    plt.show()
