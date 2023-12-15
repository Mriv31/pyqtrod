from step_helpers import * # or whatever name you want.
import numpy as np
from sklearn.neighbors import KernelDensity
from scipy import signal

def replace_with_closest(X, L):
    Li = np.argmin(np.abs(L[:, np.newaxis] - X%(2*np.pi)), axis=0)
    closest_values = L[Li] + np.round((X - L[Li]) / (2 * np.pi)) * (2 * np.pi)
    return closest_values,Li


def compute_transitions(output,xi,zi,xar,peaks,pen=0.1,min_segment_size=5):

    if (xar is None):


        window = (1.0 / 100) * np.ones(100)
        X = np.convolve(zi, window, mode='valid')[::100]


        X = X%(2*np.pi)
        X=X[:,np.newaxis]
        sh = 0
        sth = 2*np.pi
        kde = KernelDensity(kernel='gaussian', bandwidth=0.012).fit(X)
        xar = np.arange(sh,sth,0.01)
        fit = np.exp(kde.score_samples(xar[:,np.newaxis]))
        peaks = signal.find_peaks(fit,prominence=0.01)
        peaks = peaks[0]



    xboundori,mori,xboundrawori = get_ruptures_mm(xi,zi,min_size=min_segment_size,min_deg_size=5,penalty_value=pen,show=0,showstepvalue=0,showstep=0,dpi=100)
    mh,indlih = replace_with_closest(np.array(mori), xar[peaks])
    inda = np.where(np.diff(indlih) == 0)[0]
    indlih = np.delete(indlih,inda)
    mh = np.delete(mh,inda)
    xboundh = np.delete(xboundori,inda)
    xboundrawh = np.delete(xboundrawori,inda)
    diss = []
    for i in range(len(xboundh)-1):
        inds =xboundrawh[i]
        inde = xboundrawh[i+1]
        ma = np.mean(zi[inds:inde]-mh[i+1])
        diss.append(ma)
    diss = []
    transitionarh = np.empty([len(peaks),len(peaks)],dtype=object)
    xbounddiffh = np.diff(xboundh)

    #transitionar contain list of times when transition from I to J happens
    for i in range(len(peaks)):
        for j in range(len(peaks)):
            transitionarh[i, j] = []

    for i in range(1,len(indlih)-1): #I don't consider the first transition
        transitionarh[indlih[i]][indlih[i+1]].append(xboundh[i]) #contains  all transitions and times

    timessh = np.empty([len(peaks),len(peaks)],dtype=object)
    for i in range(len(peaks)):
        for j in range(len(peaks)):
            timessh[i, j] = [0]

    #timess contain list of times spent in state I between each occurrence of a given transition from state I to J

    for i in range(1,len(indlih)):
        for j in range(len(peaks)):
            timessh[indlih[i],j][-1] += xbounddiffh[i-1]

        if i!=len(indlih)-1:

            timessh[indlih[i],indlih[i+1]].append(0)



    #rawtr contains lists of indices of start and stop corresponding to timess[i][j][k] (ie the indices corresponding of the time spent in state [i] before times[i][j][k]
    #meanz contains lists of mean values then modulo two pi corresponding to times
    #durations are the durations of those

    rawtrh = np.empty([len(peaks),len(peaks)],dtype=object)
    meanzh = np.empty([len(peaks),len(peaks)],dtype=object)
    durationsh = np.empty([len(peaks),len(peaks)],dtype=object)
    for i in range(len(peaks)):
        for j in range(len(peaks)):
            rawtrh[i, j] = [np.empty([],dtype=int)]
            meanzh[i, j] = [[]]
            durationsh[i, j] = [[]]
    for i in range(1,len(indlih)):
        for j in range(len(peaks)):

            if rawtrh[indlih[i],j][-1].size == 1:

                rawtrh[indlih[i],j][-1] = np.arange(xboundrawh[i-1],xboundrawh[i],dtype=int)


            else:
                rawtrh[indlih[i],j][-1] = np.hstack((rawtrh[indlih[i],j][-1],np.arange(xboundrawh[i-1],xboundrawh[i],dtype=int)))
            meanzh[indlih[i], j][-1].append(np.mean(zi[xboundrawh[i-1]:xboundrawh[i]])%(2*np.pi))
            durationsh[indlih[i],j][-1].append(xboundrawh[i]-xboundrawh[i-1])

        if i!=len(indlih)-1:
            rawtrh[indlih[i],indlih[i+1]].append(np.empty([],dtype=int))
            meanzh[indlih[i],indlih[i+1]].append([])
            durationsh[indlih[i],indlih[i+1]].append([])

    #here I remove the last time of each list because it belongs to no transition but if I where to divided the whole time spent there by the number of events I should put it back

    for i, j in np.ndindex(timessh.shape):
        timessh[i,j].pop()
        meanzh[i,j].pop()
        durationsh[i,j].pop()
        rawtrh[i,j].pop()

    meanallh = np.empty([len(peaks),len(peaks)],dtype=object)
    meantimeh = np.empty([len(peaks),len(peaks)],dtype=object)

    for i in range(len(peaks)):
        for j in range(len(peaks)):
            meanallh[i, j]=[]
            meantimeh[i, j]=[]
            for k in range(len(meanzh[i,j])):
                if len(durationsh[i,j][k])>0:
                    meanallh[i, j].append(np.average(meanzh[i,j][k],weights=durationsh[i,j][k]))
                    meantimeh[i, j].append(np.average(xi[rawtrh[i,j][k]]))
    # plt.plot(xi,zi,".",ms=)
    # plt.step(xboundh,mh,color="red",linewidth=1)
    # plt.show()
    np.savez(output,transitionar=transitionarh,fit=fit,meanall=meanallh,meantime=meantimeh,meanz=meanzh,timess=timessh,durations=durationsh,rawtr=rawtrh,peaks=peaks,xar=xar,xbound=xboundh,indli=indlih,xboundraw=xboundrawh,m=mh)
