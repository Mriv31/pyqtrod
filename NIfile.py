# -*- coding: utf-8 -*-
import numpy as np
from nptdms import TdmsWriter, ChannelObject, TdmsFile
from corr_matrix import *
#import cupy as cp




class NIfile:
    n_signals = 4
    def __init__(self,path,max_size=20000,dec=100,indstart=0,raw=0):
        self.path = path
        self.max_size = max_size
        self.indstart = 0
        try:
            self.tdms_file = TdmsFile.open(self.path)
        except:
            raise ValueError("Problem opening file "+path)
        self.group = self.tdms_file.groups()[0]

        try:

            self.channels = self.group.channels()
            self.channelnames = [i.name for i in self.channels]
            self.orientations = ["90","45","135","0"]
            self.groupnb = len(self.tdms_file.groups())

            self.time_inc = self.channels[0].properties['wf_increment']
            self.time_off = self.channels[0].properties['wf_start_offset']
            self.starttime = self.channels[0].properties['wf_start_time']
            self.freq = 1/self.time_inc
        except:
            TdmsFile.close(self.path)
            raise ValueError("Problem loading file "+path)
        self.center = -1
        self.dec_average = 1
        self.a=[1,1,1,1]
        self.b=[0,0,0,0]


        if (raw):
            self.matcor=np.identity(4)
        else:
            self.matcor = T_Icor_Matrix() #0,90,45,135 (45 is reflected)

            inds = self.get_pol_ind(["0","90","45","135"])
            P = np.zeros([4,4])
            for i in range(4):
                P[i,inds[i]]=1
            self.matcor = np.dot(np.linalg.inv(P),np.dot(self.matcor,P))

        self.init_data_share(dec)


    def init_data_share(self,dec,time=-1): #called at the beginning or when change dec
        self.dec = 1
        if dec in [1,2,5,10,20,50,100]:
             self.dec = dec
        else:
             print("bad dec")

        lengths = [len(c) for c in self.channels]
        for l in lengths:
            if l != lengths[0]:
                print("No equal sizes")
        self.datasize = lengths[0]
        self.ld = np.min([int(self.datasize/dec),self.max_size])
        if self.ld % 2 ==1:
            self.ld -= 1 #always even

        self.data = np.zeros([self.n_signals,self.ld]) #references to the whole data that correspond to the channels
        self.xs = np.zeros(self.ld)
        self.update_data_from_file(time)

    def get_pol_ind(self,listpol):
        indlist = []
        for i in range(len(listpol)):
            for j in range(len(self.orientations)):
                if self.orientations[j] == listpol[i]:
                    indlist.append(j)
                    break
        return indlist


    def ret_index_by_pol(self,pol):
        for i in range(len(self.orientations)):
            if self.orientations[i] == pol:
                return i
            if self.orientations[i] == pol:
                return i
            if self.orientations[i] == pol:
                return i
            if self.orientations[i] == pol:
                return i



    def update_data_from_file_old(self,time,norep=0):


        center = self.time_to_index_in_file([time])[0]
        if (center < self.ld/2*self.dec):
            center = self.ld/2*self.dec
        if (center + self.dec*self.ld/2 > self.datasize):
            center = self.datasize - self.ld/2*self.dec
        if (center == self.center and norep == 1):
            return 1

        if time == -2:
            center = self.center


        self.center = center
        imin = int(center - self.ld/2*self.dec)
        imax = int(center + self.ld/2*self.dec)
        for i in range(self.n_signals):
                if self.dec == 1:
                    self.data[i,:] = self.b[i]+self.a[i]*self.channels[i][imin:imin+self.ld]
                elif self.dec_average:
                    self.data[i,:] = self.b[i]+self.a[i]*np.mean(self.channels[i][imin:imin+self.ld*self.dec].reshape([self.ld,self.dec]),axis=1)
                else:
                    self.data[i,:] = self.b[i]+self.a[i]*self.channels[i][imin:imin+self.ld*self.dec:self.dec]
        self.xs[:] = self.time_off + self.time_inc * np.arange(imin,imin+self.ld*self.dec,self.dec)
        self.indstart = imin  #starting index of the file where the signal is read
        self.minymem = np.min(np.asarray(self.data[i,:]))
        self.maxymem = np.max(np.asarray(self.data[i,:]))
        self.minxmem = np.min(np.asarray(self.xs))
        self.maxxmem = np.max(np.asarray(self.xs))
        return 0

    def ret_cor_channel(self,start,stop,ordl=["0","90","45","135"]):
        data = np.zeros([4,stop-start])
        for i in range(self.n_signals):
                data[i,:] = self.b[i]+self.a[i]*self.channels[i][start:stop]
        data = np.dot(self.matcor,data)
        index = self.get_pol_ind(ordl)
        return data[index[0],:],data[index[1],:],data[index[2],:],data[index[3],:]

    def ret_raw_channels(self,start,stop,ordl=["0","90","45","135"],data=None):
        for i in range(self.n_signals):
                data[i,:] = self.channels[i][start:stop]
        index = self.get_pol_ind(ordl)
        return data[index[0],:],data[index[1],:],data[index[2],:],data[index[3],:]

    def ret_loaded_data(self,ordl=["0","90","45","135"]):
        index = self.get_pol_ind(ordl)
        return self.data[index[0],:],self.data[index[1],:],self.data[index[2],:],self.data[index[3],:]

    def update_data_from_file(self,time,norep=0):
        center = self.time_to_index_in_file([time])[0]
        if (center < self.ld/2*self.dec):
            center = self.ld/2*self.dec
        if (center + self.dec*self.ld/2 > self.datasize):
            center = self.datasize - self.ld/2*self.dec
        if (center == self.center and norep == 1):
            return 1

        if time == -2:
            center = self.center


        self.center = center
        imin = int(center - self.ld/2*self.dec)
        imax = int(center + self.ld/2*self.dec)
        for i in range(self.n_signals):
                if self.dec == 1:
                    self.data[i,:] = self.b[i]+self.a[i]*self.channels[i][imin:imin+self.ld]
                elif self.dec_average:
                    self.data[i,:] = self.b[i]+self.a[i]*np.mean(self.channels[i][imin:imin+self.ld*self.dec].reshape([self.ld,self.dec]),axis=1)
                else:
                    self.data[i,:] = self.b[i]+self.a[i]*self.channels[i][imin:imin+self.ld*self.dec:self.dec]
        self.xs[:] = self.time_off + self.time_inc * np.arange(imin,imin+self.ld*self.dec,self.dec)
        self.data = np.dot(self.matcor,self.data)
        self.indstart = imin  #starting index of the file where the signal is read
        self.minymem = np.min(np.asarray(self.data[i,:]))
        self.maxymem = np.max(np.asarray(self.data[i,:]))
        self.minxmem = np.min(np.asarray(self.xs))
        self.maxxmem = np.max(np.asarray(self.xs))
        return 0

    def full_ordered_pol(self):
        pol_ind = self.get_pol_ind(["0","90","45","135"])
        c0,c90,c45,c135 = [self.data[pol_ind[i],:] for i in range(len(pol_ind))]
        return c0,c90,c45,c135



    def time_to_index_in_mem(self,xl):
        xar = np.asarray(xl)
        ret = (xar - self.time_off)/self.time_inc
        ret = ret.astype("int")
        ret -= self.indstart
        ret=ret / self.dec
        ret = ret.astype("int")
        ret[ret<0] = 0
        ret[ret>=self.ld] = self.ld-1 # index in mem can not be larger than ld
        return ret
    def time_to_index_in_file(self,xl):
        xar = np.asarray(xl)
        ret = (xar - self.time_off)/self.time_inc
        ret = ret.astype("int")
        ret[ret<0] = 0
        ret[ret>=self.datasize] = self.datasize-1
        return ret
    def get_min_max_partial(self,xl):
        inds = self.time_to_index_in_mem(xl)
        mins = [np.min(self.data[i,inds[0]:inds[1]]) for i in range(self.n_signals)]
        maxs = [np.max(self.data[i,inds[0]:inds[1]]) for i in range(self.n_signals)]
        return np.min(mins),np.max(maxs)
