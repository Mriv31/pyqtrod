# This Python file uses the following encoding: utf-8


import numpy as np
from scipy import ndimage
from matplotlib import pyplot as plt

def dwell_times(xt,phiuc,min_a,max_a,median=0,medianparam=100,plot=0,plotresult=0):
    if (median):
        phiuh = ndimage.median_filter(phiuc,medianparam)
    else:
        phiuh = phiuc

    phirh = phiuh%(2*np.pi)
    ind = np.where(np.logical_and(phirh>min_a,phirh<max_a)) #indices of frames at a given index calue
    arr = xt[ind] #times where angle is between the value above
    n,p=np.histogram(arr,bins=np.arange(xt.min(),xt.max(),0.0008)); #histogram of the times, the larger the number of bins the more you may separate times
    arr = n

    sub_arrays = np.split(arr, np.where(arr == 0)[0]+1)  #splitting the histogram into subhistograms separated by zero (will be affected by the number of bins avove)
    if len(sub_arrays[-1]) == 0:
        sub_arrays = sub_arrays[:-1]
    result = [np.add.reduce(sub_array) for sub_array in sub_arrays if len(sub_array) > 1] #sum of consecutive bins not separated by zeros

    if (plot):
        lensub = [len(sa) for sa in sub_arrays]
        indcut = np.cumsum(lensub)
        indcut =  np.insert(indcut,0,0)
        timecut = p[indcut]
        plt.figure()
        plt.plot(xt,phiuc,".",color="orange",ms=0.6)
        plt.plot(xt[ind],phiuc[ind],".",color="red",ms=1)
        for xp in timecut:
            plt.axvline(xp)
        plt.title(f'min {min_a} max {max_a} median {median} median param {medianparam}')
    if (plotresult):
        plt.figure()
        result = np.asarray(result)
        bins = np.geomspace(result.min(), result.max(), num=20)
        #bins = np.linspace(result.min(), result.max(), num=100)
        n1,p1=np.histogram(result,bins=bins)
        n,p=np.histogram(result,bins=bins,density=True)
        plt.errorbar(p[1:]/250,n,yerr=n/np.sqrt(n1),fmt=".")
        plt.yscale("log")
    return result
