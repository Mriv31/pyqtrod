from scipy import stats
from scipy.stats import bootstrap
import numpy as np
from matplotlib import pyplot as plt

def loghisto(y,bins=10,logx=1,logy=1):
    m1 = np.min(y)
    m2 = np.max(y)
    bins = np.geomspace(m1,m2,bins+1)
    x = stats.binned_statistic(y,y, statistic='mean',bins=bins)
    x = x[0]
    n,p = np.histogram(y,bins=bins,density=True)
    ntrue,p = np.histogram(y,bins=bins,density=False)
    n = n[ntrue != 0]
    x = x[ntrue !=0]

    ntrue = ntrue[ntrue != 0]
    plt.xlabel("Time (s)")
    if (logx):
        plt.xscale('log')
    if (logy):
        plt.yscale('log')
    plt.errorbar(x,n,yerr=n/np.sqrt(ntrue))


def bsmr(y):
        res =  bootstrap(y, np.mean)
        all_t = np.mean(res.bootstrap_distribution)
        all_t_up = res.confidence_interval.high
        all_t_down = res.confidence_interval.low
        return all_t, all_t_down, all_t_up
