import ruptures as rpt
import numpy as np
from matplotlib import pyplot as plt





def get_ruptures(xt,ar,min_size=10,penalty_value=20,show=1,showstepvalue=0,showstep=1,dpi=100):
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

def get_ruptures_mm(xt,ar,min_size=10,min_deg_size=10,penalty_value=20,show=1,showstepvalue=0,showstep=1,dpi=100):
    algo_c = rpt.KernelCPD(kernel="linear", min_size=min_size).fit(ar) #"rbf"
    #c = rpt.costs.CostRbf(gamma=1/min_size/min_size)
    #algo_c = rpt.BottomUp(custom_cost=c, jump=10).fit(ar) #"rbf"

    result = algo_c.predict(pen=penalty_value)
    print("Change points found, now splitting data")

    m = [np.mean(a) for a in np.hsplit(ar, result)]
    m = m[:-2]
    xbound=xt[result[:-1]]

    stepsize = np.diff(m)*180/np.pi


    intbg = np.where(np.abs(stepsize)<min_deg_size)
    result = np.delete(result,intbg)


    m = [np.mean(a) for a in np.hsplit(ar, result)]
    m = m[:-2]
    xbound=xt[result[:-1]]

    print("Finished. Now showing")

    if (show):
        plt.figure(dpi=dpi)
        plt.plot(xt,ar)
        if (showstep):
            plt.step(xbound,m)
            plt.title("penalty = "+str(penalty_value)+"; min_value = "+"{:.2e}".format(min_deg_size)+"°")

        plt.ylabel("Rotation angle (rad)")
        plt.xlabel("Time (s)")

    if (showstepvalue):
        stepsize = np.diff(m)*180/np.pi
        for j in range(len(xbound)-1):
            plt.text(xbound[j],m[j],str(round(stepsize[j],1))+"°",fontsize=10)

    return xbound,m,result[:-1]



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

def step_vs_param(xt,ar,pen_ar,plot=1):
    upl = []
    upd = []
    dtu = []
    dtd = []

    for pen in pen_ar:
        xbound,m = get_ruptures(xt,ar,min_size=0.2,penalty_value=pen,show=0,showstepvalue=0,showstep=0,dpi=100)
        stepsize, stepsizeup,stepsizedown,dwelltime, dwelltimeup, dwelltimedown,xup,xdown = step_properties(xbound,m)
        upl.append(np.mean(stepsizeup)*180/3.14)
        upd.append(-np.mean(stepsizedown)*180/3.14)

        dtu.append(np.mean(dwelltimeup)*1000)
        dtd.append(np.mean(dwelltimedown)*1000)

    if (plot):
        plt.legend()
        plt.close(2)
        plt.figure(2)
        plt.plot(pen_ar,upl,label="Size step up")
        plt.plot(pen_ar,upd,label="Size step down")
        plt.legend()
        plt.xlabel("Penalty value (rad)")
        plt.ylabel("Average step size (deg)")

        plt.figure()
        plt.plot(pen_ar,dtu,label="Mean time up (ms)")
        plt.plot(pen_ar,dtd,label="Mean time down (ms)")
        plt.legend()
        plt.xlabel("Penalty value (rad)")
        plt.ylabel("Average dwell times")


    return pen_ar, upl, upd
