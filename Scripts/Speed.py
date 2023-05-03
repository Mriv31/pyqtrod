# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass

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

tstart,tmax = 0,-1


tdmspath = os.getenv('RODF')
outfolder = os.path.dirname(tdmspath) +"/"+ Path(tdmspath).stem + "_analysis/"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
os.environ["RODFAN"] = outfolder

from file_chunker import *



def speed_savgold(phi,t1,t2):
    params=[2,1004,1001]
    x = np.linspace(t1,t2,len(phi))
    dt = x[1]-x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat/= 2*np.pi
    return x[::10],dydt_hat[::10]


filespeed = file_chuncker(tdmspath,20,speed_savgold,tstart=tstart,tmax=tmax,force=1,dec=100)

hf=h5py.File(filespeed)
data1 = hf['data']

fig = plt.figure()
plt.plot(data1[0,:],data1[1,:])
plt.xlabel("Time(s)")
plt.ylabel("Freq(Hz)")
fig.savefig(outfolder+"speed.png",dpi=300)
plt.close(fig)


