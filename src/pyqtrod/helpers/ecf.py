# import ray
import numpy as np
from tqdm import tqdm

# what are your inputs, and what operation do you want to
# perform on each input. For example.


def ECF_func(phi, winlist, i):
    ftl_res = 0
    for win in winlist:
        start, stop = win[0], win[1]
        ftl_res += np.abs(np.sum(np.exp(1.0j * phi[start:stop] * i)))
    return ftl_res, i


def ECF_simple(
    phi, nstepmax=1000, nwindow=100, start=0, nshift=50, modemin=1, modemax=50
):
    N = len(phi)
    modelist = np.arange(modemin, modemax, 1)
    ftl = np.zeros(len(modelist))

    nstep = int((N - nwindow - start) / nshift) + 1
    if nstep > nstepmax:
        nstep = nstepmax

    winlist = []
    for r in range(nstep):
        winlist.append([r * nshift + start, start + r * nshift + nwindow])

    results = [ECF_func(phi, winlist, i) for i in modelist]

    for i in range(len(results)):
        ind = np.where(np.array(modelist) == results[i][1])[0]
        ftl[ind] = results[i][0]

    # print(results)
    return modelist, ftl, nstep, winlist


# @ray.remote
def processInput(phir, winlist, i):
    ftl_res = 0
    for win in winlist:
        start, stop = win[0], win[1]
        ftl_res += np.abs(np.sum(np.exp(1.0j * phir[start:stop] * i)))
    return ftl_res, i


def to_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        yield ray.get(done[0])


def ECF(phir, nstepmax=1000, nwindow=100, start=0, nshift=50, modemin=1, modemax=50):
    ray.shutdown()
    ray.init()
    phi_id = ray.put(phir)
    N = len(phir)
    modelist = range(modemin, modemax)
    ftl = np.zeros(len(modelist))

    nstep = int((N - nwindow - start) / nshift) + 1
    if nstep > nstepmax:
        nstep = nstepmax

    winlist = []
    for r in range(nstep):
        winlist.append([r * nshift + start, start + r * nshift + nwindow])

    result_ids = [processInput.remote(phi_id, winlist, i) for i in modelist]
    results = []

    for x in tqdm(to_iterator(result_ids), total=len(result_ids)):
        results.append(x)
    # results = ray.get(result_ids)

    for i in range(len(results)):
        ind = np.where(np.array(modelist) == results[i][1])[0]
        ftl[ind] = results[i][0]

    # print(results)
    ray.shutdown()
    return modelist, ftl, nstep, winlist
