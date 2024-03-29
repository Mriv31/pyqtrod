
import sys,os
sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]),'Helpers'))
sys.path.insert(0, os.path.dirname(sys.path[0]))

from NIfile import NIfile
import re

from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import h5py
import pynumdiff
from pathlib import Path
from scipy import ndimage
from correction_linearity import * # or whatever name you want.



tstart,tmax = 0,-1


tdmspath = os.getenv('RODF')
outfolder = os.path.dirname(tdmspath) +"/"+ Path(tdmspath).stem + "_analysis/"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
os.environ["RODFAN"] = outfolder

from file_chunker import *

if not os.path.exists(outfolder+"histograms_filtered/"):
    os.makedirs(outfolder+"histograms_filtered/")
outhist = outfolder+"histograms_filtered/"

if not os.path.exists(outfolder+"histograms_filtered_res/"):
    os.makedirs(outfolder+"histograms_filtered_res/")
outhistres = outfolder+"histograms_filtered_res/"




def phi(phi,t1,t2,i=0):
    y = phi[:]
    x = np.linspace(t1,t2,len(y))
    return None,None




def ECF(phi,t1,t2,i=0):



    phir = phi%(2*np.pi)
    phirc,phiuc =  correct_on_diff(phir,phiu):

    x_hat = ndimage.median_filter(phir,100)



    n,p = np.histogram(x_hat,bins=np.linspace(0,2*np.pi,501),density=True)
    np.save(outfolder+"histograms_filtered/hist_phi_{:.3f}_{:.3f}.npy".format(t1,t2),np.vstack((p[:-1],n)))

    return None,None


def speed_savgold(phi,t1,t2):
    params=[2,1004,1001]
    x = np.linspace(t1,t2,len(phi))
    dt = x[1]-x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat/= 2*np.pi
    return x[::10],dydt_hat[::10]


filespeed = file_chuncker(tdmspath,20,speed_savgold,tstart=tstart,tmax=tmax,force=1,dec=100)
file_chuncker(tdmspath,0.5,hist,overlap=0.25,tstart=tstart,tmax=tmax,force=1,dec=1)

hf=h5py.File(filespeed)
data1 = hf['data']



#plt.plot(data[0,:],data[1,:])
#plt.ylabel("Freq (Hz)")
#plt.xlabel("Timee (s)")
#plt.show()

files = [os.path.join(outhist, file) for file in os.listdir(outhist)]
key1 = []
key2 = []

for f in files:
    k = re.findall("\d+\.\d+", f)
    key1.append(float(k[0]))
    key2.append(float(k[1]))


files = [x for _,x in sorted(zip(key1,files))]
key1.sort()
key2.sort()





for i in range(len(files)):
    f = files[i]
    fig,(ax1,ax2) = plt.subplots(2,1)
    data = np.load(f)
    b = data[0,:]
    n = data[1,:]
    if (i != 0):
        nrolled = np.roll(n,int(len(b)/2))
        if (np.sum(nrolled*nold) > np.sum(n*nold)):
            n = nrolled
    nold = n
    data[1,:] = n
    np.save(f,data)

    ax1.bar(b,n,width=data[0,1]-data[0,0])
    ax1.set_xlim([0,2*np.pi])
    ax1.set_xticks([0,np.pi/4,np.pi/2,3*np.pi/4,np.pi,5*np.pi/4,3*np.pi/2,7*np.pi/4,2*np.pi])
    ax1.set_xticklabels(["0","$\\frac{\pi}{4}$","$\\frac{\pi}{2}$","$\\frac{3\pi}{4}$","$\pi$","$\\frac{5\pi}{4}$","$\\frac{3\pi}{2}$","$\\frac{7\pi}{4}$","$2\pi$"])
    ax2.plot(data1[0,:],data1[1,:])
    ax2.set_xlabel("Time(s)")
    ax2.set_ylabel("Freq(Hz)")
    ax3=ax2.twinx()
    print(key1[i])
    ax2.axvspan(float(key1[i]), float(key2[i]), alpha=0.5, color='red')
    fig.savefig(outhistres+"file{:d}.png".format(i),dpi=300)
    plt.close(fig)



