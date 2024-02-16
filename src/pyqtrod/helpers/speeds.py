import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import bottleneck as bn


def fit_single(self, idx, wxpwx, wxpwy, nobs, store, params_only, method):
    if nobs < self._min_nobs:
        return
    try:
        if (method == "inv") or not params_only:
            wxpwxi = np.linalg.inv(wxpwx)
        if method == "inv":
            params = wxpwxi @ wxpwy
        else:
            _, wy, wx, _, _ = self._get_data(idx)
            if method == "lstsq":
                params = lstsq(wx, wy)[0]
            else:  # 'pinv'
                wxpwxiwxp = np.linalg.pinv(wx)
                params = wxpwxiwxp @ wy

    except np.linalg.LinAlgError:
        return
    store.params[idx - 1] = params
    if params_only:
        return
    y, wy, wx, weights, _ = self._get_data(idx)

    wresid = wy - wx @ params
    ssr = np.sum(wresid**2, axis=0)

    store.ssr[idx - 1] = ssr


RollingOLS._fit_single = fit_single


def compute_speed_best_lin_fit(xp, sp, ws):
    exog = sm.add_constant(xp)
    rols = RollingOLS(sp, exog, window=ws)
    r = rols.fit(params_only=False)
    error = r.ssr  # you have various errors this is the closest from sum of residues
    slope = r.params[:, 1]
    interse = r.params[:, 0]
    a = bn.move_argmin(error, window=ws, min_count=1)
    a = np.arange(0, len(a), 1) - a
    al2 = np.roll(a, -ws)
    al2[np.isnan(al2)] = 0
    al2 = al2.astype("int")
    alf = slope[al2]
    blf = interse[al2]
    fitted = alf * xp + blf
    return alf, blf, fitted


def contiguous_regions(condition):
    """Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index."""

    # Find the indicies of changes in "condition"
    d = np.diff(condition)
    (idx,) = d.nonzero()

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, len(condition) - 1]

    # Reshape the result into two columns
    idx.shape = (-1, 2)
    return idx


def asymmetric_threshold_regions(x, low, high):
    """Returns an iterator over regions where "x" drops below "low" and
    doesn't rise above "high"."""

    # Start with contiguous regions over the high threshold...
    for region in contiguous_regions(x < high):
        start, stop = region

        # Find where "x" drops below low within these
        (below_start,) = np.nonzero(x[start:stop] < low)

        # If it does, start at where "x" drops below "low" instead of where
        # it drops below "high"
        if below_start.size > 0:
            start += below_start[0]
            yield start, stop


# Below Old Speeds
# lim1 = 0
# lim2 = 1000000
# sp = phiu[lim1:lim2]*180/np.pi
# xp = xtime[lim1:lim2]
# ws = 250
# ws2 = int(ws/2)
# shift = 1 #keep at 1 pleaz or won't work
# l = len(sp)
# start = 0
# al = []
# bl = []
# pl=[]
# xl = []
# se = []
# phired = np.zeros(len(sp))
# residue = []
# while start+ws < l:
#     g = np.mean(sp[start:start+ws])
#     a,b = np.polyfit(xp[start:start+ws],sp[start:start+ws],1)
#     al.append(a)
#     bl.append(b)
#     #if np.std(np.abs(sp[start:start+ws]-g)) < 0.2:
#     #    pl.append(1)
#     #    phired[start:start+ws] = sp[start:start+ws]
#     #else:
#     #    pl.append(0)
#     xl.append(xp[start])
#     se.append([0.5*xp[start]+0.5*xp[start+ws],xp[start+ws]])
#     residue.append(np.sum((sp[start:start+ws]-a*xp[start:start+ws]-b)**2)) #median here looks at the median quality of fit
#     start+=shift
#
# al = np.asarray(al)
# bl = np.asarray(bl)
# af=[]
# bf=[]
# #for each point I choose the fit that is the best:
# for i in range(l):
#     firsta = i - ws
#     if firsta<0:
#         firsta = 0
#     lasta = i
#     if i>=l-ws:
#         lasta = l-ws-1
#     apart = al[firsta:lasta+1]
#     bpart = bl[firsta:lasta+1]
#     respart = residue[firsta:lasta+1]
#     res = 0*(sp[i] - apart*xp[i]-bpart)**2 + respart
#     minres = np.argmin(res)
#
#     af.append(apart[minres])
#     bf.append(bpart[minres])
# af = np.asarray(af)
# bf = np.asarray(bf)
# fitted2 = af*xp+bf
