

import numpy as np
import multiprocessing


if __name__ == '__main__':
    import sys,os,glob
    sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]),'Helpers'))
    sys.path.insert(0, os.path.dirname(sys.path[0]))

    from NIfile import NIfile
    import re

    from matplotlib import pyplot as plt
    import matplotlib.image as mpimg
    import pynumdiff
    from pathlib import Path
    from scipy import ndimage
    from correction_linearity import * # or whatever name you want.
    from ECF import *
    import pandas as pd
    from scipy import ndimage, signal
    from sklearn.neighbors import KernelDensity
    plt.style.use("Y:/Martin Rieu/Post-Doc/datoviz/PyQtRod/mr_widget.mplstyle") #my own style, can remove


    xlsx_file_path = "Y:/Martin Rieu/datasummary.xlsx"
    foldersave = "C:/Users/rieu/OneDrive - Nexus365/paper1/Figure 2/"
    dec = 1
    df = pd.read_excel(xlsx_file_path)


def ECFsc(phi):

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

def parrallel_score_samples(kde, samples, thread_count=7):
    with multiprocessing.Pool(thread_count) as p:
        return np.concatenate(p.map(kde.score_samples, np.array_split(samples, thread_count)))

if __name__ == '__main__':

# Loop through the rows and read columns using the keys in the first row
    for index, row in df.iterrows():
        # Access data in each column using the key from the first row
        if row["Analyze"] != 1:
            continue
        path = "Y:/Martin Rieu/"+row["Folder"]+"/"+row["File"]
        xstart =  row["Start"]*250000
        xstop =  row["Stop"]*250000
        f = NIfile(path,dec=dec,rawoptics=0,decref=5000,max_size=20000)

        if np.isnan(xstart):
            xstart = 0
        if np.isnan(xstop):
            xstop = len(f.channels[0])
        xstart = int(xstart)
        xstopfull = int(xstop)
        windowsize = 10*250000
        xstop = xstart + windowsize
        xstop = np.min([xstop,xstopfull])
        stopnext = 0
        if True:
            strain = row["Strain"]
            print("Loading phi ...")
            print(row["File"])
            print(xstart/250000,xstop/250000)

            xt = np.arange(xstart,np.min([xstop,len(f.channels[0])]),dec)/250e3
            folder = "C:/Users/rieu/OneDrive - Nexus365/paper1/Figure 2/all_ECF/"
            isExist = os.path.exists(folder)
            if not isExist:
               os.makedirs(folder)
            #if os.path.exists(folder+row["File"]+"_ECF_{:.3f}_{:.3f}.npy".format(xstart/250000,xstop/250000)) == 0:
            if True:

                plt.figure()
                phiu = f.ret_phi(xstart,xstart+1000000,raw=0)
                phir = phiu%(2*np.pi)
                #X = ndimage.median_filter(phiu[:],50)%(2*np.pi)
                X = phir
                X=X[:,np.newaxis]
                sh = 0
                sth = 2*np.pi
                print("Entering Kernel density")
                kde = KernelDensity(kernel='gaussian', bandwidth=0.015).fit(X)
                xar = np.arange(sh,sth,0.01)
                print("Entering Fit density")
                fit = parrallel_score_samples(kde, xar[:,np.newaxis])
                fit = np.exp(fit)
                peaks = signal.find_peaks(fit,distance=10)[0]
                print("peaks nb : ",len(peaks))
                plt.hist(X,400,color="lightseagreen",label="Raw histogram",density=True);
                plt.plot(xar,fit)
                plt.plot(xar[peaks],fit[peaks],".",color="red")
                plt.ylabel("Probability density (UA)")
                plt.xlabel("Angle (rad)")

                plt.savefig(folder+row["File"]+"histo_fit.png")
                plt.close()
    #            phiu = f.ret_phi(xstart,xstop,raw=0)

    #            nstepmax = 900000 #max number of iterations
    #            nwindow = 100000 #sier of window
    #            modemax = 60 #maximum mode to study
    #            modemin = 1 #minimum mode to study
    #            modelist,ftl,nstep,winlist = ECF(phiu,nstepmax=nstepmax,nwindow=nwindow,nshift=int(nwindow/2),modemin=modemin,modemax=modemax)
    #            np.save(folder+row["File"]+"_ECF_{:.3f}_{:.3f}.npy".format(xstart/250000,xstop/250000),np.vstack((modelist,ftl)))
    #        xstart += windowsize
    #        xstop += windowsize
    #        if (stopnext):
    #            break
    #        if (xstop >= xstopfull):
    #            xstop = xstopfull
    #            stopnext = 1



    #    plt.figure(dpi=200,constrained_layout=True)
    #    xr = np.linspace(0,2*np.pi,90)
    #    yr = f.fcor(xr)
    #    plt.plot(xr[1:],np.diff(yr))
    #    plt.savefig(folder+row["File"]+"_Corr.png")
    #    plt.close()


        # filtered and correlation
        #try:
    #        xhat = ndimage.median_filter(phiu[:],200)

    #        plt.hist(xhat%(2*np.pi),400,color="lightseagreen",label="Raw histogram");
    #        plt.ylabel("Probability density (UA)")
    #        plt.xlabel("Angle (rad)")

    #        plt.savefig(folder+row["File"]+"filtered_200.png")
    #        plt.close()
            #xhat = xhat/(2*np.pi)
    #        xhat = ndimage.median_filter(phiu[:],100)/(2*np.pi)

    #        xhat = phiu/(2*np.pi)
    #        step = 0.05
    #        step = step/(2*np.pi)
    #        bins = np.arange(xhat.min(),xhat.max(),step)
    #        n,p = np.histogram(xhat,bins=bins)
    #        xar = 0.5*p[1:]+0.5*p[:-1]

    #        n = n - np.mean(n)
    #        correlation = signal.correlate(n, n, mode="full")

    #        lags = signal.correlation_lags(xar.size, xar.size, mode="full")

    #        lags = lags*step

    #        N = len(lags)
    #        lags = lags[N//2+1:]
    #        correlation = correlation[N//2+1:]

    #        plt.figure(dpi=200,constrained_layout=True)
    #        fft = np.abs(np.fft.rfft(correlation[100:]))
    #        freq = np.fft.rfftfreq(len(correlation[100:]),step)
    #        freq,fft = signal.welch(correlation,1/step,nperseg=2**14)
    #        startazer = np.where(freq>35)[0][0]
    #        plt.plot(freq[:startazer],fft[:startazer])

    #        plt.yscale("log")
    #        plt.xlabel("Mode")
    #        #plt.xscale("log")
    #        #plt.title(f"file {tdmspath} \n FFT of the spatial correlation of times spent in bins of size {round(step,4)} and median filter size {filter} \n start {start} s ; stop {stop} s")
    #        plt.savefig(folder+row["File"]+"CC_filtered_200.png")
    #        np.save(folder+row["File"]+"CC.npy",np.vstack((freq,fft)))
    #     plt.close()
    #    except:
    #        continue







    #    xhat = ndimage.median_filter(phiu[:],200)%(2*np.pi)




    #    plt.figure(dpi=200,constrained_layout=True)
    #    plt.hist(phir,500)
    #    plt.savefig(folder+row["File"][:-4]+"_med_200"+".png")
    #    plt.close()







        # Perform operations with key1_value, key2_value, etc.
        # For example, you can print the values:
