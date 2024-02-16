from pomegranate.gmm import GeneralMixtureModel
from pomegranate.distributions import Exponential
from scipy.stats import bootstrap
import numpy as np


def summarize_transition_stats(peaks, timess, do_double=0):
    all_t = np.zeros([timess.shape[0], timess.shape[1]])
    all_t_up = np.zeros([timess.shape[0], timess.shape[1]])
    all_t_down = np.zeros([timess.shape[0], timess.shape[1]])
    for i in range(len(peaks)):
        for j in range(len(peaks)):
            data = np.array(timess[i, j])
            if data.size == 0:
                continue

            if do_double:
                dl = []
                dl.append(Exponential([np.mean(data)]).double())
                dl.append(Exponential([1000 * np.mean(data)]).double())

                model = GeneralMixtureModel(dl)
                model.fit(data[:, np.newaxis])

                a = model.distributions[0].parameters()
                next(a)
                mean1 = next(a)[0].item()

                a = model.distributions[1].parameters()
                next(a)
                mean2 = next(a)[0].item()

                pred = model.predict(data[:, np.newaxis])
                print(
                    mean1,
                    mean2,
                    len(np.where(pred == 0)[0]),
                    len(np.where(pred == 1)[0]),
                )
                ii0 = np.where(pred == 0)[0]

                data2 = (data[ii0],)
            else:
                data2 = (data,)
            if len(data) > 1:
                res = bootstrap(data2, np.mean)
                all_t[i, j] = np.mean(res.bootstrap_distribution)
                all_t_up[i, j] = res.confidence_interval.high
                all_t_down[i, j] = res.confidence_interval.low
            elif len(data) == 1:
                all_t[i, j] = data2[0]
                all_t_up[i, j] = data2[0]
                all_t_down[i, j] = data2[0]
            else:
                print("data pb" + len(data))
    return all_t, all_t_up, all_t_down
