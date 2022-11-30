# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import numpy as np
from scipy.optimize import curve_fit,minimize
from functools import partial
from scipy.interpolate import interp1d


def fittpline(theta,phi,nstep=50):
    bins = np.linspace(0,2*np.pi,nstep)
    tb = []
    tbs = []
    phim = []
    for i in range(len(bins)-1):
        ind = np.where(np.logical_and(phi>bins[i],phi<bins[i+1]))[0]
        print(ind)
        tb.append(np.nanmedian(theta[ind]))
        tbs.append(np.nanmedian(np.sin(theta[ind])))

        phim.append(np.nanmean(phi[ind]))
    return np.array(phim),np.array(tb),np.array(tbs)


def density(v0,v20,var,v2ar,l=0.2):
    disphi = np.abs(v2ar-v20)
    disphi[np.where(disphi>np.pi)] = 2*np.pi - disphi[np.where(disphi>np.pi)]
    ar = np.exp(-(var-v0)**2/2/l**2-(disphi)**2/2/l**2)
    ar = ar[~np.isnan(ar)]
    return -np.sum(ar)


def fittplinedensity(theta,phi,nstep=50):
    bins = np.linspace(0,2*np.pi,nstep)
    tb = []
    tbs = []
    phiml = []
    for i in range(len(bins)-1):
        phim = bins[i]*0.5+bins[i+1]*0.5
        res = minimize(partial(density,v20=phim,var=theta,v2ar=phi), [0.7])
        tb.append(res.x[0])
        phiml.append(phim)
    return np.array(phiml),np.array(tb),None


def remove_nans_by_interpol(theta,phi,phiml,tb):
    f = interp1d(phiml,tb,kind="linear")
    ind = None


