import ruptures as rpt
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import CubicSpline

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
        plt.plot(np.linspace(0,2*np.pi,N+1),f(np.linspace(0,2*np.pi,N+1)),".-")
        plt.xlabel("$\phi_{ori}$")
        plt.ylabel("$\phi_{old}$")







    return f

