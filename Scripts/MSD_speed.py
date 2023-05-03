
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

if not os.path.exists(outfolder+"MSD/"):
    os.makedirs(outfolder+"MSD/")
outhist = outfolder+"MSD/"

if not os.path.exists(outfolder+"MSD_res/"):
    os.makedirs(outfolder+"MSD_res/")
outhistres = outfolder+"MSD_res/"


tstart = 0
tmax = -1

def phi(phi,t1,t2,i=0):
    y = phi[:]
    x = np.linspace(t1,t2,len(y))
    return None,None


def MSDspeed(phi,t1,t2):
    xar = np.arange(1,100,1)
    result = np.zeros(len(xar))
    meanresult = np.zeros(len(xar))
    for i in range(len(result)):
          result[i] = np.average((phi[int(xar[i]):] - phi[:-int(xar[i])])**2)
          meanresult[i] = np.average(phi[int(xar[i]):] - phi[:-int(xar[i])])
          result[i] = result[i] - meanresult[i]**2
    xar=xar/250000
    a,b=np.polyfit(xar[20:],result[20:],1)
    a1,b1=np.polyfit(xar,meanresult,1)


    params=[2,1004,1001]
    x = np.linspace(t1,t2,len(phi))
    dt = x[1]-x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat/= 2*np.pi


    return np.mean(dydt_hat),np.array([2*np.pi*a1/a])


def speed_savgold(phi,t1,t2):
    params=[2,1004,1001]
    x = np.linspace(t1,t2,len(phi))
    dt = x[1]-x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat/= 2*np.pi
    return x[::10],dydt_hat[::10]


filemsdspeed = file_chuncker(tdmspath,3,MSDspeed,overlap=3,tstart=tstart,tmax=tmax,force=1,dec=1)

hf=h5py.File(filemsdspeed)
data = hf['data']


plt.plot(data[0,:],data[1,:])


