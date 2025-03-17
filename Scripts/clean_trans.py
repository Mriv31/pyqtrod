import numpy as np
import shutil
from pyqtrod.ni_file import NIfile
from pyqtrod.helpers.compute_transitions import compute_transition_arrays
import os

import pandas as pd


def clean_file(file, nifile, output_folder, raw=1, freq=250e3):

    data = np.load(file, allow_pickle=True)
    peaks = data["peaks"]
    xbound = data["xbound"]
    m = data["m"]
    indli = data["indli"]
    xboundraw = data["xboundraw"]

    filename = os.path.basename(file)

    start_time_phiu = int(filename.split("_")[1].split(".")[0])
    end_time_phiu = int(filename.split("_")[3].split(".")[0])

    phiu = nifile.ret_phi(
        int(start_time_phiu * freq), int(end_time_phiu * freq), raw=raw
    )

    time = np.linspace(start_time_phiu, start_time_phiu + len(phiu) / freq, len(phiu))

    i = 0
    nb_non_significant = 0  # Number of non significant transitions
    while i < len(xbound) - 2:
        if m[i + 2] == m[i]:  # go back to same point
            istart = int((xbound[i] - start_time_phiu) * freq)
            iend = int((xbound[i + 1] - start_time_phiu) * freq)
            segment = phiu[istart:iend]
            istart2 = int((2 * xbound[i] - xbound[i + 1] - start_time_phiu) * freq)
            if istart2 >= 10:
                segment_before = phiu[istart2 - 10 : istart - 10]
            else:
                i += 1
                continue
            if iend + iend - istart < len(phiu):
                segment_after = phiu[iend + 10 : iend + iend - istart + 10]
            else:
                i += 1
                continue

            whole = np.hstack((segment_before, segment, segment_after))

            mean_segment = np.mean(segment)
            mean_segment_before = np.mean(segment_before)
            mean_segment_after = np.mean(segment_after)
            assert len(whole) == len(segment) + len(segment_before) + len(segment_after)

            mean_whole = np.mean(whole)

            var = (
                np.var(segment) * len(segment)
                + np.var(segment_before) * len(segment_before)
                + np.var(segment_after) * len(segment_after)
            )
            var = var / (len(segment) + len(segment_before) + len(segment_after))

            var_whole = np.var(whole)

            log_likelihood_no_change = -0.5 * np.sum(
                (whole - mean_whole) ** 2 / var_whole + np.log(2 * np.pi * var_whole)
            )
            log_likelihood_change = (
                -0.5
                * np.sum((segment - mean_segment) ** 2 / var + np.log(2 * np.pi * var))
                - 0.5
                * np.sum(
                    (segment_before - mean_segment_before) ** 2 / var
                    + np.log(2 * np.pi * var)
                )
                - 0.5
                * np.sum(
                    (segment_after - mean_segment_after) ** 2 / var
                    + np.log(2 * np.pi * var)
                )
            )

            proba_ratio_change = np.exp(
                log_likelihood_change - log_likelihood_no_change
            )

            n = len(whole)  # Total number of data points
            k1 = 1  # One parameter (mean1)
            k2 = 2  # Two parameters (mean1 and mean2)

            bic1 = k1 * np.log(n) - 2 * log_likelihood_no_change
            bic2 = k2 * np.log(n) - 2 * log_likelihood_change

            delta_bic = bic1 - bic2  # Positive ΔBIC favors the two-means model
            if proba_ratio_change < 90 or delta_bic < 2:
                nb_non_significant += 1
                xbound = np.delete(xbound, [i, i + 1])
                m = np.delete(m, [i + 1, i + 2])
                indli = np.delete(indli, [i + 1, i + 2])
                xboundraw = np.delete(xboundraw, [i, i + 1])
                i -= 1
        i += 1
    new_data = {key: data[key] for key in data}
    new_data["xbound"] = xbound
    new_data["m"] = m
    new_data["indli"] = indli
    new_data["xboundraw"] = xboundraw
    print(xboundraw[-1], time[-1], xbound[-1], len(time))
    transitionarh, meanallh, meantimeh, meanzh, timessh, durationsh, rawtrh = (
        compute_transition_arrays(
            xbound,
            xboundraw,
            indli,
            peaks,
            phiu,
            time,
        )
    )
    new_data["transitionarh"] = transitionarh
    new_data["meanallh"] = meanallh
    new_data["meantimeh"] = meantimeh
    new_data["meanzh"] = meanzh
    new_data["timessh"] = timessh
    new_data["durationsh"] = durationsh
    new_data["rawtrh"] = rawtrh
    new_file_path = os.path.join(output_folder, filename)
    print(new_file_path)

    np.savez(new_file_path, **new_data)
    print("Removed ", nb_non_significant, " transitions from ", file)


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
    read_folder = (
        "Y:/Martin Rieu/"
        + row["Folder"]
        + "/"
        + row["File"][:-5]
        + "_analysis/transitions/"
    )
    save_folder = read_folder + "quality_checked_BIC/"
    if os.path.isdir(save_folder) == 0:
        os.mkdir(save_folder)

    f = NIfile(tdmspath)

    if row["c2"] == "PotAb cell 1":
        raw = 0
    else:
        raw = 1

    for file in os.listdir(read_folder):
        if file.endswith(".npz") and file.startswith("trans_"):
            if os.path.exists(os.path.join(save_folder, file)):
                continue
            try:
                clean_file(os.path.join(read_folder, file), f, save_folder, raw=raw)
            except Exception as e:
                print(
                    f"Failed to clean file: {file}, got error: {e}, copying original file"
                )
                shutil.copy(os.path.join(read_folder, file), save_folder)
