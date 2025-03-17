import os
import numpy as np
from PyQt6.QtWidgets import QProgressDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QEventLoop
from ..ni_file import NIfile
from ..modules.freq_wavelet import FreqWT
import time
from PyQt6.QtWidgets import QInputDialog


def compute_all_phi(path):
    """
    Compute the phi values for all the files in a folder.
    """
    # path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a folder", "")
    # if path == ("", ""):
    #     return
    # path = path[0]
    # print(path)
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".tdms")]
    avg_amount = None
    decimate_amount = None

    reply = QMessageBox.question(
        None,
        "Averaging",
        "Do you want to apply an average to the signal before cmoputing phi?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )

    average = reply == QMessageBox.StandardButton.Yes
    if average:
        avg_amount, ok = QInputDialog.getInt(
            None,
            "Average Amount",
            "How much do you want to average the signal?",
            value=100,
            min=2,
            max=10000,
        )
        if not ok:
            return

        decimate_amount, ok = QInputDialog.getInt(
            None,
            "Decimate Amount",
            "How much do you want to decimate the signal?",
            value=1,
            min=1,
            max=avg_amount,
        )
        if not ok:
            return

    progress_dialog = QProgressDialog("Processing files...", "Cancel", 0, len(files))
    progress_dialog.setWindowTitle("Batch Analysis")
    progress_dialog.show()
    progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    progress_dialog.setMinimumDuration(0)
    files_with_error = []
    for fn in files:

        if os.path.exists(os.path.join(path, fn[:-5] + "_phiu.npy")):
            continue

        progress_dialog.setValue(files.index(fn))
        if progress_dialog.wasCanceled():
            break
        try:
            f = NIfile(os.path.join(path, fn), ignore_correction=0)
            # f.a = [1, 1.2, 1, 1] only if ignore_correction=1
            stoptime = f.datasize / f.freq
            start = 0
            stop = stoptime
            phiu = f.ret_phi(
                int(start * f.freq),
                int(stop * f.freq),
                raw=1,
                cutwindow=1000000,
                average_before=average,
                average_before_window=avg_amount,
                average_before_dec=decimate_amount,
            )
            print(fn, f.a)
            xt = np.linspace(start, stop, len(phiu))
            np.save(
                os.path.join(path, fn[:-5] + "_phiu.npy"),
                np.array([xt, phiu]),
            )
        except Exception as e:
            print(e)
            files_with_error.append(fn)
    progress_dialog.close()
    if files_with_error:
        error_message = "The following files encountered errors during processing:\n"
        error_message += "\n".join(files_with_error)
        QMessageBox.critical(None, "Processing Errors", error_message)
    else:
        QMessageBox.information(None, "Success", "All files processed successfully.")
    return


def compute_all_speeds(path, threadpool=None):
    """
    Compute the phi values for all the files in a folder.
    """
    # path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a folder", "")
    # if path == ("", ""):
    #     return
    # path = path[0]
    # print(path)
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".tdms")]
    progress_dialog = QProgressDialog("Processing files...", "Cancel", 0, len(files))
    progress_dialog.setWindowTitle("Batch Analysis")
    progress_dialog.show()
    progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    progress_dialog.setMinimumDuration(0)
    files_with_error = []
    for fn in files:

        if os.path.exists(os.path.join(path, fn[:-5] + "_speed_wt.npy")):
            continue

        progress_dialog.setValue(files.index(fn))
        if progress_dialog.wasCanceled():
            break
        try:
            f = NIfile(os.path.join(path, fn), ignore_correction=0)
            # f.a = [1, 1.2, 1, 1] only if ignore_correction=1
            stoptime = f.datasize / f.freq
            start = 0
            stop = stoptime
            stop = min(stop, 100)
            freq_wt = FreqWT(NIfile=f, threadpool=threadpool)
            freq_wt.start = start
            freq_wt.stop = stop
            freq_wt.windowsize = 1000
            freq_wt.min_estimated_frequency = 40
            freq_wt.max_estimated_frequency = 250
            freq_wt.frequency_step = 3
            freq_wt.save = True
            freq_wt.compute_freq()

            def wait_until_done(freq_wt, timeout_ms=30 * 60 * 1000):  # 20 minutes max
                loop = QEventLoop()
                count = [0]

                def check_done():
                    if freq_wt.done:
                        loop.quit()  # Exit the event loop when done
                    else:
                        count[0] += 1
                        if count[0] * 1000 >= timeout_ms:
                            print("Timeout: 20 minutes exceeded")
                            loop.quit()  # Exit loop on timeout
                        else:
                            QTimer.singleShot(1000, check_done)  # Check again in 100 ms

                check_done()
                loop.exec()

            wait_until_done(freq_wt)
            # Start the event loop
        except Exception as e:
            print(e)
            files_with_error.append(fn)
    progress_dialog.close()
    if files_with_error:
        error_message = "The following files encountered errors during processing:\n"
        error_message += "\n".join(files_with_error)
        QMessageBox.critical(None, "Processing Errors", error_message)
    else:
        QMessageBox.information(None, "Success", "All files processed successfully.")
    return
