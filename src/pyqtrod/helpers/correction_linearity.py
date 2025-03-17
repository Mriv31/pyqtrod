import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import CubicSpline
from scipy import stats


def correct_on_speed_step(
    m, speeds, N=500, fftfilter=1, mfilter=7, show=1
):  # m is phir for each point, speed the value of speed
    nn, _ = np.histogram(np.array(m) % (2 * np.pi), N)  # Compute the histo of m
    # sy, _ = np.histogram(np.array(m[:-2])%(2*np.pi), N, weights=np.abs(speeds)) #Computes the sum of the value of speeds in each bin of m
    bins = np.linspace(0, 2 * np.pi, N)
    binned_std_displacement = stats.binned_statistic(m, speeds, "std", bins=bins)
    sy = binned_std_displacement.statistic

    if show:
        plt.figure()
        plt.plot(
            np.array(m[1:]) % (2 * np.pi),
            speeds,
            ".",
            markersize=1,
            label="raw points",
        )
        plt.plot(np.linspace(0, 2 * np.pi, N), sy, label="Average signal")

    if 0 in nn:  # if undersampling can not correct non linearities.
        print("Warning : I did not correct non linearities because of undersampling")
        return lambda x: x

    # Here we FFT filter the mean
    if fftfilter:
        rft = np.fft.rfft(sy)
        rft[mfilter:] = 0  # Note, rft.shape = 21
        sy = np.fft.irfft(rft)
        if show:
            plt.plot(np.linspace(0, 2 * np.pi, N), sy, label="Filtered signal")
            plt.legend()
            plt.xlabel("Phir (rad)")
            plt.ylabel("Value")

    fcor = np.cumsum(1 / sy)
    fcor = np.insert(fcor, 0, 0)
    fcor = fcor * 2 * np.pi / fcor[-1]
    f = CubicSpline(np.linspace(0, 2 * np.pi, N - 1), fcor)

    if show:
        plt.figure()
        plt.plot(
            np.linspace(0, 2 * np.pi, N - 1), f(np.linspace(0, 2 * np.pi, N - 1)), ".-"
        )
        plt.xlabel("$\phi_{ori}$")
        plt.ylabel("$\phi_{old}$")

    return f


def set_fcor_from_array(arf):
    xar = arf[0, :]
    if xar[0] != 0 or xar[-1] != 2 * np.pi or (np.all(xar[:-1] <= xar[1:]) is False):
        print("I have not set fcor, input file was not as expected")
        return
    yar = arf[1, :]
    return CubicSpline(xar, yar)


def correct_on_diff(phir, phiu, show=0, fcor=None):
    if fcor is None:
        print(len(phir))
        fcor = correct_on_speed_step(
            phir[1:1000000], np.diff(phiu[0:1000000]), show=show
        )
    phirc = fcor(phir)
    phiuc = np.unwrap(phirc)
    return phirc, phiuc, fcor
