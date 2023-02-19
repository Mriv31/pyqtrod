import numpy as np
from scipy.optimize import curve_fit,minimize
from functools import partial
from scipy.stats import linregress

def Icor_matrix(a=0,b=0,c=0,d=0,inv=1):
    return Icor_matrix_par(a,b,c,d,inv)

def T_Icor_Matrix(): #ordre 0,90,45,135, with 45 reflected
    ret = np.zeros([4,4])
    ret[0][0] = 0.152 #transmitted
    ret[0][1] = 0
    ret[1][0] = 0
    ret[1][1] = 0.148 #reflected
    alpha = 0.455
    beta = 0.009 #This is quite critical
    t = 0.757 #transmited in PBS
    r = 0.741 #reflected
    ret[2][0] = -alpha*beta*r #Reflected
    ret[2][1] = alpha*beta*r
    ret[2][2] = alpha*alpha*r
    ret[2][3] = beta*beta*r
    ret[3][0] = -alpha*beta*t  #Transmitted
    ret[3][1] = alpha*beta*t
    ret[3][2] = beta*beta*t
    ret[3][3] = alpha*alpha*t
    return np.linalg.inv(ret)/8

def correct_with_matrix(c0,c90,c45,c135):
    ac = np.asarray(np.vstack((c0,c90,c45,c135)))
    ac = np.dot(T_Icor_Matrix(),ac)
    c0 = ac[0,:]
    c90 = ac[1,:]
    c45 = ac[2,:]
    c135 = ac[3,:]
    return c0,c90,c45,c135



def Icor_matrix_par(a,b,c,d,inv):
    ret = np.zeros([4,4])
    sq = np.sqrt((1-a)*(1-b))
    alpha = 1-(a+b)/2-sq
    beta  =  1-(a+b)/2+sq
    ret[0][0] = (1+a)*(1-c*c)/2
    ret[0][1] = (1+b)*d*d/2
    ret[1][0] = c*c*(1+a)/2
    ret[1][1] = (1+b)*(1-d*d)/2
    c2 = d
    d2 = c
    ret[2][0] = (b-a)*(1-c2*c2+d2*d2)/8
    ret[2][1] = -(b-a)*(1-c2*c2+d2*d2)/8
    ret[2][2] = 0.25*(1-c2*c2)*beta + 0.25*d2*d2*alpha
    ret[2][3] = 0.25*(1-c2*c2)*alpha + 0.25*d2*d2*beta
    ret[3][0] = (b-a)*(1-d2*d2+c2*c2)/8
    ret[3][1] = -(b-a)*(1-d2*d2+c2*c2)/8
    ret[3][2] = 0.25*c2*c2*beta + 0.25*(1-d2*d2)*alpha
    ret[3][3] = 0.25*c2*c2*alpha + 0.25*(1-d2*d2)*beta
    if (inv):
        return np.linalg.inv(ret)
    return ret

def Icor_matrix_par_full(a,b,c,d,c2,d2,a0,a45,inv):
    ret = np.zeros([4,4])
    sq = np.sqrt((1-a)*(1-b))
    alpha = 1-(a+b)/2-sq
    beta  =  1-(a+b)/2+sq
    ret[0][0] = a0*(1+a)*(1-c*c)/2
    ret[0][1] = a0*(1+b)*d*d/2
    ret[1][0] = c*c*(1+a)/2
    ret[1][1] = (1+b)*(1-d*d)/2

    ret[2][0] = a45*(b-a)*(1-c2*c2+d2*d2)/8
    ret[2][1] = -a45*(b-a)*(1-c2*c2+d2*d2)/8
    ret[2][2] = a45*0.25*(1-c2*c2)*beta + a45*0.25*d2*d2*alpha
    ret[2][3] = a45*0.25*(1-c2*c2)*alpha + a45*0.25*d2*d2*beta
    ret[3][0] = (b-a)*(1-d2*d2+c2*c2)/8
    ret[3][1] = -(b-a)*(1-d2*d2+c2*c2)/8
    ret[3][2] = 0.25*c2*c2*beta + 0.25*(1-d2*d2)*alpha
    ret[3][3] = 0.25*c2*c2*alpha + 0.25*(1-d2*d2)*beta
    if (inv):
        return np.linalg.inv(ret)
    return ret

def best_matrix_func(par,ac):
    a,b = par
    bc = np.dot(Icor_matrix_par(a,b,0,0,1),ac)
    c0 = bc[0,:]
    c90 = bc[1,:]
    c45 = bc[2,:]
    c135 = bc[3,:]
    return np.sum((c0 +c90 - c45 - c135)**2)

def best_matrix_func_full(par,ac):
    a,b,a0,a45 = par
    bc = np.dot(Icor_matrix_par_full(a,b,0,0,a0,a45,1),ac)
    c0 = bc[0,:]
    c90 = bc[1,:]
    c45 = bc[2,:]
    c135 = bc[3,:]
    return np.sum((c0 +c90 - c45 - c135)**4)
    slope, intercept, r_value, p_value, std_err = linregress(c0+c90, c45+c135)
    return -r_value

def find_best_matrix(c0,c90,c45,c135):
    ac = np.asarray(np.vstack((c0,c90,c45,c135)))
    result = minimize(partial(best_matrix_func,ac=ac), [-0.1,-0.1])
    return result

def find_best_matrix_full(c0,c90,c45,c135):
    ac = np.asarray(np.vstack((c0,c90,c45,c135)))
    bounds = [(-0.3,0.3),(-0.3,0.3),(0.7,1.3),(0.7,1.3)]
    result = minimize(partial(best_matrix_func_full,ac=ac), [-0.1,-0.1,1,1],bounds=bounds)
    return result

def best_coeff_func(params,ac):
    a90,a45,a135 = params
    c0 = ac[0,:]
    c90 = ac[1,:]
    c45 = ac[2,:]
    c135 = ac[3,:]
    return np.sum((c0 + a90*c90 - c45*a45-c135*a135)**2)

def true_best_coeff_func_mat(params,ac,mat):
    a90,a45,a135 = params
    ap = np.copy(ac)
    ap[1,:]*=a90
    ap[2,:]*=a45
    ap[3,:]*=a135
    bc = np.dot(mat,ap)
    c0 = bc[0,:]
    c90 = bc[1,:]
    c45 = bc[2,:]
    c135 = bc[3,:]
    return np.sum((c0 + c90 - c45-c135)**2)

def find_best_coeff_using_mat(c0,c90,c45,c135,mat):
    ac = np.asarray(np.vstack((c0,c90,c45,c135)))
    result = minimize(partial(true_best_coeff_func_mat,ac=ac,mat=mat), [1,1,1])

    return result

#def true_best_coeff_func(params,ac):
#    a90,a45,a135 = params
#    ap = np.copy(ac)
#    ap[1,:]*=a90
#    ap[2,:]*=a45
#    ap[3,:]*=a135
#    bc = np.dot(T_Icor_Matrix(),ap)
#    c0 = bc[0,:]
#    c90 = bc[1,:]
#    c45 = bc[2,:]
#    c135 = bc[3,:]
#    return np.sum((c0 + c90 - c45-c135)**2)

#def find_best_coeff_using_matrix(c0,c90,c45,c135):
#    ac = np.asarray(np.vstack((c0,c90,c45,c135)))
#    result = minimize(partial(true_best_coeff_func,ac=ac), [1,1,1])

#    return result


def find_best_coeff(c0,c90,c45,c135):
    ac = np.asarray(np.vstack((c0,c90,c45,c135)))
    result = minimize(partial(best_coeff_func,ac=ac), [1,1,1])

    return result
