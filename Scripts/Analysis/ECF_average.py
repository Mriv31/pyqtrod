import os, sys
import numpy as np
from matplotlib import pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.path[0])),'Helpers'))
from ECF import *
from sklearn import linear_model, datasets
import h5py
import re
from sklearn.utils.fixes import sp_version, parse_version
solver = "highs" if sp_version >= parse_version("1.6.0") else "interior-point"
# Définir le chemin du répertoire principal
main_dir = '../../../'
i = 0
# Parcourir tous les sous-dossiers nommés "ECF_res"
mar = np.zeros(79)

for root, dirs, files in os.walk(main_dir):
    for dir in dirs:
        if dir == 'ECF':
            # Définir le chemin du sous-dossier ECF_res
            sub_dir = os.path.join(root, dir)
            # Parcourir tous les fichiers .npy dans le sous-dossier
            for file in os.listdir(os.path.dirname(sub_dir)): # Chercher dans le dossier au dessus les vitesses
                if file.startswith("speed_savgold"):
                    hf=h5py.File(os.path.join(os.path.dirname(sub_dir), file))
                    data1 = hf['data']
                    xt = data1[0,:]
                    v = data1[1,:]
            for file in os.listdir(sub_dir): # Chercher dans le dossier au dessus les vitesses
                if file.endswith('.npy'):
                    # Charger le tableau à partir du fichier .npy
                    filepath = os.path.join(sub_dir, file)
                    array = np.load(filepath)
                    k = re.findall("\d+\.\d+", file)
                    ind = np.where(np.logical_and(xt<float(k[1]),xt>float(k[0])))
                    vt = np.mean(v[ind])
                    if np.abs(vt) < 5:
                        continue
                    print(f'loaded {filepath}')
                    # Faire la moyenne du tableau
                    #ransac = linear_model.QuantileRegressor(quantile=0.2, alpha=0,solver=solver)


                    mar += array[1,:]
                    i+=1


mar/=i
plt.xlabel("Mode")
plt.ylabel("ECF intensity")
plt.plot(range(1,80),mar)
plt.show()

nstepmax = 900000 #max number of iterations
nwindow = 100000 #sier of window
modemax = 80 #maximum mode to study
modemin = 1 #minimum mode to study
vmean = 2*np.pi/950
v = np.random.normal(vmean,vmean/2,1000000)
dummy = np.arange(0,10000000)/10000000*400*np.pi
dummy = np.cumsum(v)
modelist,ftl,nstep,winlist = ECF(dummy,nstepmax=nstepmax,nwindow=nwindow,nshift=int(nwindow/2),modemin=modemin,modemax=modemax)
plt.gca().twinx().plot(ftl)
plt.show()
plt.plot(dummy)
plt.show()
