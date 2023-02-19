# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import ruptures as rpt
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import CubicSpline

pen = 0.02
min_size_deg = 0.2

xbound,m = get_ruptures(xi,zi,min_size=min_size_deg/180*np.pi,penalty_value=pen,show=1,showstepvalue=0,showstep=0,dpi=100)
stepsize, stepsizeup,stepsizedown,dwelltime, dwelltimeup, dwelltimedown,xup,xdown = step_properties(xbound,m)
f = correct_on_speed_step(m,np.abs(stepsize))
phirc = f(phir)
phiuc = np.unwrap(phirc)

def get_ruptures(xt,ar,min_size=0.2,penalty_value=20,show=1,showstepvalue=0,showstep=1,dpi=100):
    algo_c = rpt.KernelCPD(kernel="linear", min_size=min_size).fit(ar) #"rbf"
    #c = rpt.costs.CostRbf(gamma=1/min_size/min_size)
    #algo_c = rpt.BottomUp(custom_cost=c, jump=10).fit(ar) #"rbf"

    result = algo_c.predict(pen=penalty_value)
    print("Change points found, now splitting data")

    m = [np.mean(a) for a in np.hsplit(ar, result)]
    m = m[:-2]
    xbound=xt[result[:-1]]

    print("Finished. Now showing")

    if (show):
        plt.figure(dpi=dpi)
        plt.plot(xt,ar)
        if (showstep):
            plt.step(xbound,m)
            plt.title("penalty = "+str(penalty_value)+"; min_value = "+"{:.2e}".format(min_size*180/np.pi)+"°")

        plt.ylabel("Rotation angle (rad)")
        plt.xlabel("Time (s)")

    if (showstepvalue):
        stepsize = np.diff(m)*180/np.pi
        for j in range(len(xbound)-1):
            plt.text(xbound[j],m[j],str(round(stepsize[j],1))+"°",fontsize=10)

    return xbound,m


def step_properties(xbound,m):
    stepsize = np.diff(m)
    dwelltime = np.diff(xbound) #first dwell time corresponds to time before second step_size #last dwell time correspond to nothing
    stepsize = stepsize[1:]
    dwelltime = dwelltime[:-1] #now first dweel time corresponds to first stepsize

    indup = np.where(stepsize>0)
    inddown = np.where(stepsize<0)
    xup = np.array(xbound)[np.array(indup)+1]
    xdown = np.array(xbound)[np.array(inddown)+1]

    xup=xup[0]
    xdown=xdown[0]

    dwelltimeup = np.diff(xup)
    dwelltimedown = np.diff(xdown)


    return stepsize, stepsize[indup],stepsize[inddown],dwelltime, dwelltimeup, dwelltimedown,xup,xdown


def correct_on_speed_step(m,speeds,N=100,fftfilter=1,mfilter=7,show=1): #m is phir for each point, speed the value of speed

    nn, _ = np.histogram(np.array(m[:-2])%(2*np.pi), N) #Compute the histo of m
    sy, _ = np.histogram(np.array(m[:-2])%(2*np.pi), N, weights=np.abs(speeds)) #Computes the sum of the value of speeds in each bin of m
    sy = sy/nn #Mean speed of in each bin
    if (show):
        plt.figure()
        plt.plot(np.array(m[:-2])%(2*np.pi),speeds,'.',markersize=1,label="raw points")
        plt.plot(np.linspace(0,2*np.pi,N),sy,label="Average signal")



    #Here we FFT filter the mean
    if (fftfilter):
        rft = np.fft.rfft(sy)
        rft[mfilter:] = 0   # Note, rft.shape = 21
        sy = np.fft.irfft(rft)
        if (show):
            plt.plot(np.linspace(0,2*np.pi,N),sy,label="Filtered signal")
            plt.legend()
            plt.xlabel("Phir (rad)")
            plt.ylabel("Value")


    fcor = np.cumsum(1/sy)
    fcor = np.insert(fcor,0,0)
    fcor = fcor*2*np.pi/fcor[-1]
    f = CubicSpline(np.linspace(0,2*np.pi,N+1),fcor)

    if show:
        plt.figure()
        plt.plot(np.linspace(0,2*np.pi,N+1),fcor,".-")
        plt.xlabel("$\phi_{ori}$")
        plt.ylabel("$\phi_{old}$")







    return f
