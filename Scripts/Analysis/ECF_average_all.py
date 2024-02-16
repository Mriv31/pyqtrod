import os
import sys
import numpy as np

from ECF import *
from sklearn import linear_model, datasets
import h5py
import re
from sklearn.utils.fixes import sp_version, parse_version

solver = "highs" if sp_version >= parse_version("1.6.0") else "interior-point"
# Définir le chemin du répertoire principal
main_dir = "../../../"
i = 0
# Parcourir tous les sous-dossiers nommés "ECF_res"
mar = np.zeros(79)
var = [0]
far = [""]
for root, dirs, files in os.walk(main_dir):
    for dir in dirs:
        if dir == "ECF":
            # Définir le chemin du sous-dossier ECF_res
            sub_dir = os.path.join(root, dir)
            # Parcourir tous les fichiers .npy dans le sous-dossier
            for file in os.listdir(
                os.path.dirname(sub_dir)
            ):  # Chercher dans le dossier au dessus les vitesses
                if file.startswith("speed_savgold"):
                    hf = h5py.File(os.path.join(os.path.dirname(sub_dir), file))
                    data1 = hf["data"]
                    xt = data1[0, :]
                    v = data1[1, :]
            for file in os.listdir(
                sub_dir
            ):  # Chercher dans le dossier au dessus les vitesses
                if file.endswith(".npy"):
                    # Charger le tableau à partir du fichier .npy
                    filepath = os.path.join(sub_dir, file)
                    array = np.load(filepath)
                    print(f"loaded {filepath}")
                    # Faire la moyenne du tableau
                    # ransac = linear_model.QuantileRegressor(quantile=0.2, alpha=0,solver=solver)
                    ransac = linear_model.RANSACRegressor()

                    x = np.log(range(1, 80))

                    xar = np.vstack((np.ones(79), x, x**2))

                    ransac.fit(np.transpose(xar), array[1, :])

                    # Predict data of estimated models
                    line_y_ransac = ransac.predict(np.transpose(xar))
                    mar = np.vstack((mar, array[1, :] / line_y_ransac))

                    k = re.findall("\d+\.\d+", file)
                    ind = np.where(np.logical_and(xt < float(k[1]), xt > float(k[0])))
                    var.append(np.mean(v[ind]))

                    far.append(filepath)


np.save("AllECF_cor.npy", mar)
np.save("AllECF_cor_v.npy", var)
np.save("AllECF_cor_f.npy", far)


# a,b,c,d=np.polyfit(xar,mar,3)
# plt.plot(xar*xar*xar*a+xar*xar*b+c*xar+d)


# nstepmax = 900000 #max number of iterations
# nwindow = 100000 #sier of window
# modemax = 80 #maximum mode to study
# modemin = 1 #minimum mode to study
# vmean = 2*np.pi/1000
# v = np.random.normal(vmean,vmean,1000000)
# dummy = np.arange(0,10000000)/10000000*400*np.pi
# dummy = np.cumsum(v)
# modelist,ftl,nstep,winlist = ECF(dummy,nstepmax=nstepmax,nwindow=nwindow,nshift=int(nwindow/2),modemin=modemin,modemax=modemax)
# plt.gca().twinx().plot(ftl)
# plt.show()
# plt.plot(dummy)
# plt.show()
