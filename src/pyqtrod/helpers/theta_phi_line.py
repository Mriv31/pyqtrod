# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import numpy as np
from scipy.optimize import minimize
from functools import partial
from sklearn.linear_model import LinearRegression
from multiprocessing import Pool


def fittpline(theta, phi, nstep=50):
    bins = np.linspace(0, 2 * np.pi, nstep)
    tb = []
    tbs = []
    phim = []
    for i in range(len(bins) - 1):
        ind = np.where(np.logical_and(phi > bins[i], phi < bins[i + 1]))[0]
        print(ind)
        tb.append(np.nanmedian(theta[ind]))
        tbs.append(np.nanmedian(np.sin(theta[ind])))

        phim.append(np.nanmean(phi[ind]))
    return np.array(phim), np.array(tb), np.array(tbs)


def density(v0, v20, var, v2ar, L=0.2):
    disphi = np.abs(v2ar - v20)
    disphi[np.where(disphi > np.pi)] = 2 * np.pi - disphi[np.where(disphi > np.pi)]
    ar = np.exp(-((var - v0) ** 2) / 2 / L**2 - (disphi) ** 2 / 2 / L**2)
    ar = ar[~np.isnan(ar)]
    return -np.sum(ar)


def fittplinedensity(theta, phi, nstep=50):
    bins = np.linspace(0, 2 * np.pi, nstep)
    tb = []
    phiml = []
    for i in range(len(bins) - 1):
        phim = bins[i] * 0.5 + bins[i + 1] * 0.5
        res = minimize(partial(density, v20=phim, var=theta, v2ar=phi), [0.7])
        tb.append(res.x[0])
        phiml.append(phim)
    return np.array(phiml), np.array(tb), None


def fourier_fit(theta, phi, nstep=100, nmodes=10):
    X = np.ones([len(phi), 2 * nmodes + 1])
    for n in range(nmodes):
        X[:, 2 * n] = np.cos((n + 1) * phi)
        X[:, 2 * n + 1] = np.sin((n + 1) * phi)
    reg = LinearRegression(fit_intercept=False).fit(X, theta)

    xar = np.arange(0, 2 * np.pi, 2 * np.pi / nstep)
    X = np.ones([len(xar), 2 * nmodes + 1])

    for n in range(nmodes):
        X[:, 2 * n] = np.cos((n + 1) * xar)
        X[:, 2 * n + 1] = np.sin((n + 1) * xar)

    return reg.coef_, xar, reg.predict(X)


def fourier(x, coefficients):
    n = len(coefficients) // 2
    freqs = np.arange(1, n + 1)
    result = coefficients[2 * n] + np.sum(
        coefficients[: 2 * n : 2] * np.cos(freqs * x)
        + coefficients[1::2] * np.sin(freqs * x)
    )
    return result


def f_prime(x, coefficients):
    n = len(coefficients) // 2
    freqs = np.arange(1, n + 1)
    result = -coefficients[: 2 * n : 2] * freqs * np.sin(
        freqs * x
    ) + freqs * coefficients[1::2] * np.cos(freqs * x)
    return result


# Define the objective function to minimize (distance between (X, Y) and (X0, f(X0)))
def objective(coefficients, x, X, Y):
    return (X - x) ** 2 + (Y - fourier(x, coefficients)) ** 2


def optimize_point(coefficients, point):
    x, y = point
    result = minimize(lambda x0: objective(coefficients, x0, x, y), x0=x)

    return result.x[0]


def phi_from_fourier(theta, phir):
    coefficients, _, _ = fourier_fit(theta, phir)
    coefficients = np.array(coefficients)
    with Pool(8) as pool:
        phif = pool.map(partial(optimize_point, coefficients), list(zip(phir, theta)))
    return phif
