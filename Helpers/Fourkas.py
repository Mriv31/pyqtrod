#standard Fourkas with tweaktheta
import numpy as np

def comp_phiu(c0,c90,c45,c135):
    phi = 0.5 * np.arctan2((c45/2-c135/2),(c0/2-c90/2))
    return np.unwrap(phi,period=np.pi)



def Fourkas(c0,c90,c45,c135,theta0=0,phi0=0,NA=1.3,nw=1.33,tweaktheta=1):
    alpha = np.arcsin(NA/nw)
    A=1/6-1/4*np.cos(alpha)+1/12*np.cos(alpha)**3
    B=1/8*np.cos(alpha)-1/8*np.cos(alpha)**3
    C = 7/48-np.cos(alpha)/16-np.cos(alpha)**2/16-np.cos(alpha)**3/48
    phi = 0.5 * np.arctan2((c45/2-c135/2),(c0/2-c90/2)) #thhis one I modified to symmetrize

    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)

    theta1 = np.arcsin(np.sqrt((c0-c90)/(2*tweaktheta*Itots2thet*C*cs)))

    Itot = Itots2thet / np.sin(theta1)**2

    return phi,theta1,Itots2thet,Itot

#standard Fourkas with tweaktheta, compute expected I135 from I0, I45, I90, but actually dins I0+I90-I45
def Fourkas_compItot(c0,c90,c45,c135,theta0=0,phi0=0,NA=1.3,nw=1.33,tweaktheta=1,A=None,B=None,C=None):
    alpha = np.arcsin(NA/nw)
    if (A == None or B == None or C == None):
        A=1/6-1/4*np.cos(alpha)+1/12*np.cos(alpha)**3
        B=1/8*np.cos(alpha)-1/8*np.cos(alpha)**3
        C = 7/48-np.cos(alpha)/16-np.cos(alpha)**2/16-np.cos(alpha)**3/48


    phi = 0.5 * np.arctan2((c45/2-c135/2),(c0/2-c90/2)) #thhis one I modified to symmetrize
    #phi = 0.5 * np.arccos((c0-c90)/(c0+c90))

    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)
    Itots2thet2 = 1/2/A*((1-B/C/ss)*c45+(1+B/C/ss)*c135)

    theta1 = np.arcsin(np.sqrt((c0-c90)/(2*tweaktheta*Itots2thet*C*cs)))
    theta2 = np.arcsin(np.sqrt((c45-c135)/(2*tweaktheta*Itots2thet2*C*ss)))

    Itot = Itots2thet / np.sin(theta1)**2
    I135 = Itots2thet*(A+B*np.sin(theta1)**2-C*np.sin(theta1)**2*ss)

    return phi,theta1,theta2,Itots2thet,Itots2thet2,Itot,I135

#return wchich phi0 theta0 minimize standard deviation of scalar product of vector with whole data
def Fourkas_find_axis(params,NA=1.3,nw=1.33,tweaktheta=1):
    phi0,theta0=params
    alpha = np.arcsin(NA/nw)
    A=1/6-1/4*np.cos(alpha)+1/12*np.cos(alpha)**3
    B=1/8*np.cos(alpha)-1/8*np.cos(alpha)**3
    C = 7/48-np.cos(alpha)/16-np.cos(alpha)**2/16-np.cos(alpha)**3/48

    phi = 0.5 * np.arctan2(c45/2-c135/2,c0/2-c90/2) #thhis one I modified to symmetrize

    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)


    stheta1sq = (c0-c90)/(2*tweaktheta*Itots2thet*C*cs)

    theta1 = np.arcsin(np.sqrt(stheta1sq))
    theta1[np.isnan(theta1)] = np.pi/2
    v1 = np.array([np.sin(theta1)*np.cos(phi),np.sin(theta1)*np.sin(phi),np.cos(theta1)])
    v2 = np.array([np.sin(theta0)*np.cos(phi0),np.sin(theta0)*np.sin(phi0),np.cos(theta0)])
    fac = np.arccos(v1.transpose().dot(v2))
    return(np.std(fac)/np.mean(fac))

def ABC(NA=1.3,nw=1.33):
    alpha=np.arcsin(NA/nw)
    A=1/6-1/4*np.cos(alpha)+1/12*np.cos(alpha)**3
    B=1/8*np.cos(alpha)-1/8*np.cos(alpha)**3
    C = 7/48-np.cos(alpha)/16-np.cos(alpha)**2/16-np.cos(alpha)**3/48
    return A,B,C

#return the angle compared to an axis defined by phi0,theta0
def scalar(params,NA=1.3,nw=1.33,tweaktheta=1):
    phi0,theta0 = params
    alpha = np.arcsin(NA/nw)

    A=1/6-1/4*np.cos(alpha)+1/12*np.cos(alpha)**3
    B=1/8*np.cos(alpha)-1/8*np.cos(alpha)**3
    C = 7/48-np.cos(alpha)/16-np.cos(alpha)**2/16-np.cos(alpha)**3/48

    phi = 0.5 * np.arctan2(c45/2-c135/2,c0/2-c90/2) #thhis one I modified to symmetrize


    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)

    stheta1sq = (c0-c90)/(2*tweaktheta*Itots2thet*C*cs)


    theta1 = np.arcsin(np.sqrt(stheta1sq))
    v1 = np.array([np.sin(theta1)*np.cos(phi),np.sin(theta1)*np.sin(phi),np.cos(theta1)])
    v2 = np.array([np.sin(theta0)*np.cos(phi0),np.sin(theta0)*np.sin(phi0),np.cos(theta0)])
    fac = v1.transpose().dot(v2)
    return(np.arccos(fac))

#add random parameters to the formula
def Fourkas_circle_2(params):
    l = params
    alpha = np.arcsin(1.3/1.33)

    A=1/6-1/4*np.cos(alpha)+1/12*np.cos(alpha)**3
    B=1/8*np.cos(alpha)-1/8*np.cos(alpha)**3
    C = 7/48-np.cos(alpha)/16-np.cos(alpha)**2/16-np.cos(alpha)**3/48

    phi = 0.5 * np.arctan2(c45/2-c135/2,c0/2-c90/2) #thhis one I modified to symmetrize

    phi0, theta0 = -0.3488509 ,  0.24252733

    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)
    Itots2thet2 = 1/2/A*((1-B/C/ss)*c45+(1+B/C/ss)*c135)

    stheta1sq = (l[0]*c0-l[1]*c90+l[2]*c45+l[3]*c135)/(2*Itots2thet*C*cs)
    theta1 = np.arcsin(np.sqrt(stheta1sq))
    theta1= theta1[~np.isnan(theta1)]
    v1 = np.array([np.sin(theta1)*np.cos(phi),np.sin(theta1)*np.sin(phi),np.cos(theta1)])
    v2 = np.array([np.sin(theta0)*np.cos(phi0),np.sin(theta0)*np.sin(phi0),np.cos(theta0)])
    fac = np.arccos(v1.transpose().dot(v2))
    return(np.std(fac)/np.mean(fac))

#find best A,B,C to remove difference between two Itots2theta.
def Fourkas_ABC(params,c0=None,c45=None,c90=None,c135=None):
    A,B,C=params


    phi = 0.5 * np.arctan2(c45/2-c135/2,c0/2-c90/2) #thhis one I modified to symmetrize

    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)
    Itots2thet2 = 1/2/A*((1-B/C/ss)*c45+(1+B/C/ss)*c135) #will be automatically equal to the one above si I0+I90 = I45+I135

    return np.nansum((Itots2thet2-Itots2thet)**2)/np.abs(np.nanmean(Itots2thet2)) #this is bullshit,

def Fourkas_ABC_calc(params,c0=None,c45=None,c90=None,c135=None):
    A,B,C=params


    phi = 0.5 * np.arctan2(c45/2-c135/2,c0/2-c90/2) #thhis one I modified to symmetrize

    cs = np.cos(2*phi)
    ss = np.sin(2*phi)
    Itots2thet = 1/2/A*((1-B/C/cs)*c0+(1+B/C/cs)*c90)
    Itots2thet2 = 1/2/A*((1-B/C/ss)*c45+(1+B/C/ss)*c135) #will be automatically equal to the one above si I0+I90 = I45+I135

    Itots2thet[np.isnan(Itots2thet)] = 0
    Itots2thet2[np.isnan(Itots2thet2)] = 0

    return Itots2thet,Itots2thet2 #this is bullshit
