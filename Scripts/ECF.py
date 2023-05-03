
import sys,os,glob
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
from ECF import *


tstart,tmax = 0,-1


tdmspath = os.getenv('RODF')
outfolder = os.path.dirname(tdmspath) +"/"+ Path(tdmspath).stem + "_analysis/"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)
os.environ["RODFAN"] = outfolder

from file_chunker import *

if not os.path.exists(outfolder+"ECF/"):
    os.makedirs(outfolder+"ECF/")
outecf = outfolder+"ECF/"

if not os.path.exists(outfolder+"ECF_res/"):
    os.makedirs(outfolder+"ECF_res/")
outecfres = outfolder+"ECF_res/"



if not os.path.exists(outfolder+"COR/"):
    os.makedirs(outfolder+"COR/")
outcorres = outfolder+"COR/"



if len(os.listdir(outecfres)) == 0:
    folders=[outecf,outcorres]
    for fold in folders:
        files = os.listdir(fold)
        for f in files:
            os.remove(fold+f)
else:
    sys.exit()




def ECFsc(phi,t1,t2,i=0):

    phir = phi%(2*np.pi)
    phirc,phiuc,fcor =  correct_on_diff(phir,phi)


    x_hat = ndimage.median_filter(phiuc[:],200)
    nstepmax = 900000 #max number of iterations
    nwindow = 100000 #sier of window
    modemax = 80 #maximum mode to study
    modemin = 1 #minimum mode to study
    modelist,ftl,nstep,winlist = ECF_simple(x_hat,nstepmax=nstepmax,nwindow=nwindow,nshift=int(nwindow/2),modemin=modemin,modemax=modemax)
    np.save(outecf+"ECF_phi_{:.3f}_{:.3f}_{:d}.npy".format(t1,t2,nwindow),np.vstack((modelist,ftl)))

    xr = np.linspace(0,2*np.pi,90)
    yr = fcor(xr)

    np.save(outcorres+"COR_phi_{:.3f}_{:.3f}.npy".format(t1,t2),np.diff(yr))

    return None,None


def speed_savgold(phi,t1,t2):
    params=[2,1004,1001]
    x = np.linspace(t1,t2,len(phi))
    dt = x[1]-x[0]
    y_hat, dydt_hat = pynumdiff.linear_model.savgoldiff(phi[:], dt, params)
    dydt_hat/= 2*np.pi
    return x[::10],dydt_hat[::10]


filespeed = file_chuncker(tdmspath,20,speed_savgold,tstart=tstart,tmax=tmax,force=1,dec=100)
file_chuncker(tdmspath,10,ECFsc,overlap=5,tstart=tstart,tmax=tmax,force=1,dec=1)

hf=h5py.File(filespeed)
data1 = hf['data']



#plt.plot(data[0,:],data[1,:])
#plt.ylabel("Freq (Hz)")
#plt.xlabel("Timee (s)")
#plt.show()

files = [os.path.join(outecf, file) for file in os.listdir(outecf)]
key1 = []
key2 = []
for f in files:
    k = re.findall("\d+\.\d+", f)
    key1.append(float(k[0]))
    key2.append(float(k[1]))
files = [x for _,x in sorted(zip(key1,files))]
key1.sort()
key2.sort()

files2 = [os.path.join(outcorres, file) for file in os.listdir(outcorres)]
key12 = []
key22 = []
for f in files2:
    k = re.findall("\d+\.\d+", f)
    key12.append(float(k[0]))
    key22.append(float(k[1]))
files2 = [x for _,x in sorted(zip(key1,files2))]
key12.sort()
key22.sort()





for i in range(len(files)):
    f = files[i]
    f2=files2[i]
    plt.figure()

    plt.subplot(2,1,2)
    plt.plot(data1[0,:],data1[1,:])
    plt.xlabel("Time(s)")
    plt.ylabel("Freq(Hz)")
    plt.axvspan(float(key1[i]), float(key2[i]), alpha=0.5, color='red')

    plt.subplot(2,2,1)
    data = np.load(f)
    b = data[0,:]
    n = data[1,:]
    plt.plot(b,n)
    plt.xlabel("ECF mode")
    plt.ylabel("ECF value")

    plt.subplot(2,2,2)
    data2 = np.load(f2)

    plt.plot(data2)
    plt.xlabel("Angle (O..2pi)")
    plt.ylabel("Derivative of corr func")

    plt.savefig(outecfres+"file{:d}.png".format(i),dpi=300)
    plt.close()

    print(i)



