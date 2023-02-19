
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


tdmspath = os.getenv('RODF')
outfolder = os.path.dirname(tdmspath) +"/"+ Path(tdmspath).stem + "_analysis/"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
os.environ["RODFAN"] = outfolder

from file_chunker import *

if not os.path.exists(outfolder+"histograms/"):
    os.makedirs(outfolder+"histograms/")
outhist = outfolder+"histograms/"

if not os.path.exists(outfolder+"histograms_res/"):
    os.makedirs(outfolder+"histograms_res/")
outhistres = outfolder+"histograms_res/"



def phi(phi,t1,t2,i=0):
    y = phi[:]
    x = np.linspace(t1,t2,len(y))
    return None,None


def hist(phi,t1,t2,i=0):
    phir = phi%(2*np.pi)
    f = plt.figure()
    ax = f.gca()
    ax.hist(phir,200,density=1)
    ax.set_xlabel("Phi")
    ax.set_ylabel("Probability")
    ax.set_title("Histogram between {:.2f}s and {:.2f}s".format(t1,t2))

    f.savefig(outfolder+"histograms/hist_phi_{:.3f}_{:.3f}.png".format(t1,t2))
    return None,None


def speed_savgold(phi,t1,t2):
    params=[2,1004,1001]
    x = np.linspace(t1,t2,len(phi))
    dt = x[1]-x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat/= 2*np.pi
    return x[::10],dydt_hat[::10]


tstart,tmax = 540,600
filespeed = file_chuncker(tdmspath,20,speed_savgold,tstart=tstart,tmax=tmax,force=1,dec=100)
file_chuncker(tdmspath,2,MSD,overlap=1,tstart=tstart,tmax=tmax,force=1,dec=1)

hf=h5py.File(filespeed)
data = hf['data']



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
    ax1.imshow(mpimg.imread(f))
    ax1.axis("off")
    ax2.plot(data[0,:],data[1,:])
    ax2.set_xlabel("Time(s)")
    ax2.set_ylabel("Freq(Hz)")
    ax3=ax2.twinx()
    print(key1[i])
    ax2.axvspan(float(key1[i]), float(key2[i]), alpha=0.5, color='red')
    fig.savefig(outhistres+"file{:d}.png".format(i),dpi=300)
    plt.close(fig)



