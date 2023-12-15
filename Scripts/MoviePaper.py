#Generic Modules
from matplotlib import pyplot as plt
import matplotlib as mpl
from scipy import signal
import numpy as np
from scipy.optimize import curve_fit,minimize
#Martin's style
import sys
sys.path.insert(0, '../PyQtRod/Helpers') #insert PyQtRod path to use the reader module NIfile. Change to the location of PyQtRod.

sys.path.insert(0, '../PyQtRod') #insert PyQtRod path to use the reader module NIfile. Change to the location of PyQtRod.
plt.style.use('../PyQtRod/mr_widget.mplstyle') #my own style, can remove
from MR_jupyter import *
import Helpers
#Rod's functions
from NIfile import NIfile
from functools import partial

import os


tdmspath = "Y:/Martin Rieu/2023_02_10_MTB24/file6.tdms"
ec = 1
f = NIfile(tdmspath,dec=dec,rawoptics=0,decref=5000,max_size=20000)
print("File of length "+str(len(f.channels[0])/f.freq)+"s")
start,stop = 0,380
def spherical_to_cartesian(radius, theta, phi):
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return x, y, z
starth=0
stoph=250000*171
phiuhdec = np.convolve(phiuh,np.ones(10)/10)[::10]
xthdec = np.convolve(xth,np.ones(10)/10)[::10]
theta1dec = np.convolve(theta1,np.ones(10)/10)[::10]
c0dec = np.convolve(c0,np.ones(10)/10)[::10]
c90dec = np.convolve(c90,np.ones(10)/10)[::10]
c45dec = np.convolve(c45,np.ones(10)/10)[::10]
c135dec = np.convolve(c135,np.ones(10)/10)[::10]
num_meridians = 15
radius = 1
theta_values = np.linspace(0, 2 * np.pi, num_meridians*10)
phi_values = np.linspace(0, np.pi/2, num_meridians)  # Restrict phi to [0, pi/2]
import pynumdiff
import pynumdiff.optimize


def init_fig(dec=0):
    global time,scat3now,quiver,linenow,scatnow,wdisplayms,xth,phiuh,wreds,redscat,xs,ys,zs,ws,wdisplayfr,scats,linephi,speed
    xth = xt[starth:stoph]*1000-xt[starth]*1000
    scats = []
    phiuh = (phiu[starth:stoph]-phiu[starth]-7605.35)
    params=[2,1500,2000]
    x_hat, dxdt_hat = pynumdiff.linear_model.savgoldiff(phiuh, 4e-6, params)
    dxdt_hat/=2*np.pi
    params=[2,150,200]
    x_hat2, dxdt_hat2 = pynumdiff.linear_model.savgoldiff(phiuh[::100], 4e-4, params)
    dxdt_hat2/=2*np.pi
    wdisplayms = 10
    wdisplayfr = int(wdisplayms*250)
    stop = int(0.02/4e-6)
    wreds=100000
    %matplotlib widget
    #ax.plot_surface(x, y, z, color='b', alpha=0.01)

    # Create a grid of points for the meridians
    theta_grid, phi_grid = np.meshgrid(theta_values, phi_values)

    # Convert spherical coordinates to Cartesian coordinates for the grid
    x_grid, y_grid, z_grid = spherical_to_cartesian(1, theta_grid, phi_grid)

    # Plot wireframe meridians
    ax.plot_wireframe(1.8*x_grid, 1.8*y_grid, 1.8*z_grid, color='grey',linewidth=0.5 ,alpha=1)

    # Set labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_axis_off()
    # Show the plot
    ax.set_box_aspect([1, 1, 0.5])
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([0, 1])

    # Define the endpoints of the arrows
    arrow_length = 1
    arrow_tip_length = 0.1
    arw = 1

    # X-axis arrow
    #ax.quiver(0, 0, 0, arrow_length, 0, 0, color='k',linewidth=arw, arrow_length_ratio=arrow_tip_length)
    # Y-axis arrow
    #ax.quiver(0, 0, 0, 0, arrow_length, 0, color='k', linewidth=arw,arrow_length_ratio=arrow_tip_length)
    # Z-axis arrow
    #ax.quiver(0, 0, 0, 0, arrow_length, 0, color='k',linewidth=arw, arrow_length_ratio=arrow_tip_length)

    # Scatter plot
    arw = 3
    arrow_tip_length = 0

    xs = 1.8*np.sin(theta1[max(0,starth):starth+wreds//2])*np.cos(phiuh[max(0,-wreds//2):wreds//2])
    ys = 1.8*np.sin(theta1[max(0,starth):starth+wreds//2])*np.sin(phiuh[max(0,-wreds//2):wreds//2])
    zs = 1.8*np.cos(theta1[max(0,starth):starth+wreds//2])

    #ax.scatter(xs[:10],ys[:10],zs[:10],s=10,c="blue")
    redscat = ax.scatter(xs[:wreds],ys[:wreds],zs[:wreds],s=1,c="red",alpha=1,zorder=1)
    ws = 50
    scat3now = ax.scatter(xs[:ws],ys[:ws],zs[:ws],s=10,c="white",alpha=1,zorder=2)

    #ax.scatter([0],[0],[0],c="red")
    #ax.plot([0,xs[0]],[0,ys[0]],[0,zs[0]],c="red")
    #quiver = ax.quiver(0, 0, 0, xs[0], ys[0], zs[0], color='gold',linewidth=arw, arrow_length_ratio=arrow_tip_length,zorder=0)

    time = fig.text(0.5, 0.48, format_milliseconds(0), ha='center', va='center', fontsize=25, color='black')

    speed = fig.text(0.5, 0.95, f"Average speed", ha='center', va='center', fontsize=25, color='black')

    plt.sca(ax1)
    s=2
    scats.append(ax1.scatter(xth[0:wdisplayfr],c0[starth:starth+wdisplayfr],label="0°",s=s))
    scats.append(ax1.scatter(xth[0:wdisplayfr],c45[starth:starth+wdisplayfr],label="45°",s=s))
    scats.append(ax1.scatter(xth[0:wdisplayfr],c90[starth:starth+wdisplayfr],label="90°",s=s))
    scats.append(ax1.scatter(xth[0:wdisplayfr],c135[starth:starth+wdisplayfr],label="135°",s=s))

    linenow = ax1.axvline(xth[0],linewidth=2,color="red")
    lgnd = plt.legend(loc='upper left')
    lgnd.legendHandles[0]._sizes = [30]
    lgnd.legendHandles[2]._sizes = [30]
    lgnd.legendHandles[3]._sizes = [30]
    lgnd.legendHandles[1]._sizes = [30]



    plt.ylabel("APD voltage (V)")
    plt.xlabel("Time (ms)")
    ax1.set_xlim([xth[0]-wdisplayms,xth[0]+wdisplayms])
    plt.sca(ax3)

    if (dec):
        plt.scatter(xthdec-time0,phiuhdec/2/np.pi,s=s,c="black")
    else:
        plt.scatter(xth-time0,phiuh/2/np.pi,s=s,c="black")


    scatnow, = plt.plot(xth[0]-time0,phiuh[0]/2/np.pi,".",markersize=10,color="red")
    ax3.set_xlim([xth[0]-wdisplayms,xth[0]+wdisplayms])
    ax.view_init(elev=30, azim=-30+np.average(phiuh[:100])*180/np.pi)
    plt.sca(ax3)
    plt.ylabel("$\phi$ (number of revolutions)")
    plt.xlabel("Time (ms)")
    ind = np.where((xth>xth[0]-wdisplayms) & (xth<xth[0]+wdisplayms))[0]
    ymin = np.min(phiuh[ind]/2/np.pi)
    ymax = np.max(phiuh[ind]/2/np.pi)
    ax3.set_ylim([ymin,ymax])
    linephi =  ax4.axvline(phiuh[0],ymin=0,ymax=1,color="red")
    ax4.set_title("$\phi$")



from mpl_toolkits.mplot3d.art3d import juggle_axes
def update_plot(timef):
    global quiver,wdisplayms,xth,aziut,linephi
    i = np.argmin(np.abs(timef*1000-xth-xt[starth]*1000))

    linenow.set_xdata([xth[i]-time0])
    #scat3now.set_offsets(np.column_stack((xs[i:i+ws],ys[i:i+ws],zs[i:i+ws])))
    xs = 1.8*np.sin(theta1[max(0,starth+i-wreds//2):starth+i+wreds//2])*np.cos(phiuh[max(0,i-wreds//2):i+wreds//2])
    ys = 1.8*np.sin(theta1[max(0,starth+i-wreds//2):starth+i+wreds//2])*np.sin(phiuh[max(0,i-wreds//2):i+wreds//2])
    zs = 1.8*np.cos(theta1[max(0,starth+i-wreds//2):starth+i+wreds//2])
    scat3now._offsets3d = juggle_axes(xs[-wreds//2:-wreds//2+ws],ys[-wreds//2:-wreds//2+ws],zs[-wreds//2:-wreds//2+ws],'z')
    redscat._offsets3d = juggle_axes(xs,ys,zs,'z')
    #quiver.remove()
    #quiver = ax.quiver(0, 0, 0, xs[i], ys[i], zs[i], color='gold',linewidth=arw, arrow_length_ratio=arrow_tip_length,zorder=0)
    ax.view_init(elev=40, azim=-20+x_hat[i]*180/np.pi)
    scatnow.set_xdata([xth[i]-time0])
    scatnow.set_ydata([phiuh[i]/2/np.pi])
    for ii,c in enumerate([c0,c45,c90,c135]):
        scats[ii].set_offsets(np.column_stack((xth[max(0,i-wdisplayfr):i+wdisplayfr]-time0,c[max(0,i+starth-wdisplayfr):i+starth+wdisplayfr])))
        #scats[i].set_ydata(c[max(0,i+starth-wdisplayfr):i+starth+wdisplayfr])
    time.set_text(format_milliseconds(xth[i]*1000-time0*1000))
    speed.set_text(f"Rotation speed {round(dxdt_hat2[i//100])} Hz")

    ax3.set_xlim([xth[i]-wdisplayms-time0,xth[i]+wdisplayms-time0])
    ax1.set_xlim([xth[i]-wdisplayms-time0,xth[i]+wdisplayms-time0])
    ax1.set_ylim([0,3.2])
    if (i%100) != -1:
        ind = np.where((xth>xth[i]-wdisplayms) & (xth<xth[i]+wdisplayms))[0]
        ymin = np.min(phiuh[ind]/2/np.pi)
        ymax = np.max(phiuh[ind]/2/np.pi)
        y2 = (ymax - ymin)/2
        ax3.set_ylim([x_hat[i]/2/np.pi-y2,x_hat[i]/2/np.pi+y2])
    linephi.set_xdata(phiuh[i])

    plt.draw()

def update_plot_dec(timef):
    global quiver,wdisplayms,xth,aziut,linephi
    i = np.argmin(np.abs(timef*1000-xthdec-xt[starth]*1000))

    linenow.set_xdata([xthdec[i]-time0])
    #scat3now.set_offsets(np.column_stack((xs[i:i+ws],ys[i:i+ws],zs[i:i+ws])))
    xs = 1.8*np.sin(theta1dec[max(0,starth+i-wreds//2):starth+i+wreds//2])*np.cos(phiuhdec[max(0,i-wreds//2):i+wreds//2])
    ys = 1.8*np.sin(theta1dec[max(0,starth+i-wreds//2):starth+i+wreds//2])*np.sin(phiuhdec[max(0,i-wreds//2):i+wreds//2])
    zs = 1.8*np.cos(theta1dec[max(0,starth+i-wreds//2):starth+i+wreds//2])
    scat3now._offsets3d = juggle_axes(xs[-wreds//2:-wreds//2+ws],ys[-wreds//2:-wreds//2+ws],zs[-wreds//2:-wreds//2+ws],'z')
    redscat._offsets3d = juggle_axes(xs,ys,zs,'z')
    #quiver.remove()
    #quiver = ax.quiver(0, 0, 0, xs[i], ys[i], zs[i], color='gold',linewidth=arw, arrow_length_ratio=arrow_tip_length,zorder=0)
    ax.view_init(elev=40, azim=230+phiuhdec[-1]*180/np.pi)
    scatnow.set_xdata([xthdec[i]-time0])
    scatnow.set_ydata([phiuhdec[i]/2/np.pi])
    for ii,c in enumerate([c0dec,c45dec,c90dec,c135dec]):
        scats[ii].set_offsets(np.column_stack((xthdec[max(0,i-wdisplayfr):i+wdisplayfr]-time0,c[max(0,i+starth-wdisplayfr):i+starth+wdisplayfr])))
        #scats[i].set_ydata(c[max(0,i+starth-wdisplayfr):i+starth+wdisplayfr])
    time.set_text(format_milliseconds(xthdec[i]*1000-time0*1000))
    ax3.set_xlim([xthdec[i]-wdisplayms-time0,xthdec[i]+wdisplayms-time0])
    ax1.set_xlim([xthdec[i]-wdisplayms-time0,xthdec[i]+wdisplayms-time0])
    ax1.set_ylim([0,3.2])
    if (i%100) != -1:
        ind = np.where((xthdec>xthdec[i]-wdisplayms) & (xthdec<xthdec[i]+wdisplayms))[0]
        ymin = np.min(phiuhdec[ind]/2/np.pi)
        ymax = np.max(phiuhdec[ind]/2/np.pi)
        ax3.set_ylim([ymin,ymax])
    linephi.set_xdata(phiuhdec[i])

    plt.draw()

def format_milliseconds(microseconds):
    minutes, microseconds = divmod(microseconds, 60000000)
    seconds, microseconds = divmod(microseconds, 1000000)
    milliseconds, microseconds = divmod(microseconds, 1000)

    formatted_time = f"{int(minutes):01d} min {int(seconds):02d} sec {int(milliseconds):03d} ms {int(round(microseconds)):03d} μs"
    return formatted_time
