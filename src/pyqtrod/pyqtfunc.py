from scipy import signal
import numpy as np


def anisotropies(c0, c45, c90, c135):
    Anis090 = (c0 - c90) / (c0 + c90)
    Anis45135 = (c45 - c135) / (c45 + c135)
    return Anis090, Anis45135


def PSD(c0, nperseg=2**18, noverlap=-1, nfft=-1, freq=250e3):
    nperseg = np.min(
        [len(c0), nperseg]
    )  # Number of points in a window. If larger than the number of point in Data the spectrum is not averaged
    if noverlap == -1:
        noverlap = nperseg / 2
    if nfft == -1:
        nfft = nperseg
    f, PSF = signal.welch(c0, freq, nperseg=nperseg, nfft=nfft, noverlap=noverlap)
    return f, PSF
