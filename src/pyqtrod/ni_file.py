# -*- coding: utf-8 -*-
import numpy as np
from nptdms import TdmsFile
from .helpers.corr_matrix import T_Icor_Matrix, find_best_coeff_using_mat
from .helpers.fourkas import Fourkas, comp_phiu
from .helpers.correction_linearity import correct_on_diff, set_fcor_from_array
import os
import threading


class NIfile:
    n_signals = 4

    def __init__(
        self,
        path,
        max_size=1000000000,
        dec=1,
        rawoptics=0,
        decref=200,
        ignore_correction=0,
    ):
        self.path = path
        self.tdms_lock = threading.Lock()

        self.max_size = max_size
        self.indstart = 0
        self.tdms_file = TdmsFile.open(self.path)

        self.group = self.tdms_file.groups()[0]

        try:
            self._channels = self.group.channels()
            self.channelnames = [i.name for i in self._channels]
            self.orientations = ["90", "45", "135", "0"]
            self.groupnb = len(self.tdms_file.groups())
            try:
                self.time_inc = self._channels[0].properties["wf_increment"]
                self.time_off = self._channels[0].properties["wf_start_offset"]
                self.starttime = self._channels[0].properties["wf_start_time"]
                self.freq = 1 / self.time_inc

            except KeyError:
                self.time_inc = 4e-6
                self.freq = 1 / self.time_inc
                self.time_off = 0
                self.starttime = np.array([0])
                print("Warning : metadata broken, added time_inc manually")
        except ValueError:
            TdmsFile.close(self.path)
            raise ValueError("Problem loading file " + path)
        self.center = -1
        self.dec_average = False
        self.a = [1, 1.2, 1, 1]
        self.b = [0, 0, 0, 0]

        self.fcor = None  # defaut correction function is one

        if rawoptics:
            self.init_unitary_matrix()
        else:
            self.init_optics_matrix()

        self.init_data_share(dec)

        if not ignore_correction:
            self.correct_channels(1000, 100000)
        self.init_phi_ref(decref)

    # The functions in this section do not depend on data share function and
    # preallocated self.data variable used for visualization. Note that decimation

    def get_pol_ind(self, listpol):
        # return a list of indices corresponding to the orientations in listpol
        indlist = []
        for i in range(len(listpol)):
            for j in range(len(self.orientations)):
                if self.orientations[j] == listpol[i]:
                    indlist.append(j)
                    break
        return indlist

    def init_phi_ref(self, decref):
        """
        Initialize the reference for the phase unwrapping
        """
        if os.path.isfile(self.path[:-5] + "_phiref.npy"):
            res = np.load(self.path[:-5] + "_phiref.npy")
            self.phi_ref = res[1, :]
            self.ind_ref = res[0, :]
        else:  # initialize reference for the whole file to be sure there is no pi error
            old_dec = self.dec
            self.dec = decref
            self.ind_ref = np.arange(0, self.datasize, self.dec)
            self.phi_ref = self.ret_phi(0, self.datasize, raw=1, init=1)
            self.dec = old_dec
            np.save(
                self.path[:-5] + "_phiref.npy", np.vstack((self.ind_ref, self.phi_ref))
            )

    def ret_index_by_pol(self, pol):
        """
        Return the index of the channel corresponding to the orientation pol
        """
        for i in range(len(self.orientations)):
            if self.orientations[i] == pol:
                return i
            if self.orientations[i] == pol:
                return i
            if self.orientations[i] == pol:
                return i
            if self.orientations[i] == pol:
                return i

    def set_dec(self, value):
        dec = int(value)
        if dec in [1, 2, 5, 10, 20, 50, 100]:
            self.dec = dec

    def save_coeff_to_file(self):
        np.save(self.path[:-5] + "_chcor.npy", self.a)
        print("Channel corrections SAVED TO file")

    def correct_channels(self, start, stop, force=False):  # No decimation or data share
        """
        Correct the channels using the matrix matcorb
        It directly reads the data from the file
        """
        c0, c90, c45, c135 = self.ret_raw_channels(start, stop)
        if os.path.isfile(self.path[:-5] + "_chcor.npy") and not force:
            arf = np.load(self.path[:-5] + "_chcor.npy")
            self.a = arf
            # rfprint("Channel corrections set FROM file",a[0],a[1],a[2],a[3])
        else:
            par = find_best_coeff_using_mat(c0, c90, c45, c135, self.matcorb)
            # must be used on raw data since apply
            # matrix matcorb is the matrix in the 0,90,45,135 base

            l90, l45, l135 = par.x

            self.a[self.ret_index_by_pol("90")] = l90
            self.a[self.ret_index_by_pol("45")] = l45
            self.a[self.ret_index_by_pol("135")] = l135
            self.save_coeff_to_file()

        self.update_data_from_file(time=-2)

    def ret_cor_channel_in_file(
        self,
        start,
        stop,
        ordl=["0", "90", "45", "135"],
        average=False,
        average_window=100,
        dec=None,
    ):
        """
        Correct the channels using the matrix matcor
        and the corrections a and b
        It directly reads the data from the file
        """
        if dec is None:
            dec = self.dec
        self.tdms_lock.acquire()
        # to avoid several threads to access the tdms file at the same time
        if average is False:
            m1 = self.b[0] + self.a[0] * self._channels[0][start:stop:dec]
            data = np.zeros([4, len(m1)])
            data[0, :] = m1

            for i in range(1, self.n_signals):
                data[i, :] = self.b[i] + self.a[i] * self._channels[i][start:stop:dec]
        else:
            m1 = (
                self.b[0]
                + self.a[0]
                * np.convolve(
                    self._channels[0][start:stop],
                    np.ones((average_window,)) / average_window,
                    mode="valid",
                )[::dec]
            )
            data = np.zeros([4, len(m1)])
            data[0, :] = m1

            for i in range(1, self.n_signals):
                data[i, :] = (
                    self.b[i]
                    + self.a[i]
                    * np.convolve(
                        self._channels[i][start:stop],
                        np.ones((average_window,)) / average_window,
                        mode="valid",
                    )[::dec]
                )

        self.tdms_lock.release()

        data = np.dot(self.matcor, data)
        index = self.get_pol_ind(ordl)
        return (
            data[index[0], :],
            data[index[1], :],
            data[index[2], :],
            data[index[3], :],
        )

    def ret_cor_channel(self, start, stop, ordl=["0", "90", "45", "135"]):
        """
        Correct the channels using the matrix matcor
        and the corrections a and b
        It reads the data from the DATA SHARE
        """
        stindex, stopindex = self.time_to_index_in_mem([start, stop])
        data = self.data[:, stindex:stopindex]
        index = self.get_pol_ind(ordl)
        return (
            data[index[0], :],
            data[index[1], :],
            data[index[2], :],
            data[index[3], :],
        )

    def ret_xs(self, start, stop):
        stindex, stopindex = self.time_to_index_in_mem([start, stop])
        return self.xs[stindex:stopindex]

    def ret_raw_channel(self, start, stop, ordl=["0", "90", "45", "135"]):
        """
        Return the raw channels without any correction
        Directly reads the data from the file
        """
        stindex = self.time_to_index_in_file([start, stop])
        staindex = stindex[0]
        stopindex = stindex[1]
        index = self.get_pol_ind(ordl)

        return (
            self._channels[index[0]][staindex:stopindex],
            self._channels[index[1]][staindex:stopindex],
            self._channels[index[2]][staindex:stopindex],
            self._channels[index[3]][staindex:stopindex],
        )

    def set_fcor(self, phiu, force=0):
        if (
            os.path.isfile(self.path[:-5] + "_fcor.npy")
            and os.path.isfile(self.path[:-5] + "_phiref.npy")
            and force == 0
        ):
            arf = np.load(self.path[:-5] + "_fcor.npy")

            self.fcor = set_fcor_from_array(arf)
            print("Linearity correction function set FROM file")

        elif phiu is not None:
            _, _, self.fcor = correct_on_diff(
                phiu % (2 * np.pi), phiu, show=0, fcor=None
            )
            xar = np.linspace(0, 2 * np.pi, 200)
            yar = self.fcor(xar)
            arf = np.vstack((xar, yar))
            np.save(self.path[:-5] + "_fcor.npy", arf)
            print("Linearity correction SAVED TO file")

    def ret_phi(
        self,
        start,
        stop,
        raw=0,
        init=0,
        cutwindow=None,
        force_ref=0,
        average_before=False,
        average_before_window=100,
        average_before_dec=1,
    ):
        """
        Reads the unwrapped phase from the file
        Uses matrix matcor to correct the channels and correction a and b
        Corrected for linearity if raw=0
        """
        if cutwindow is not None:
            phiu = np.empty([])
            windowrange = np.arange(start, stop, cutwindow).astype("int")
            for w in windowrange:
                c0, c90, c45, c135 = self.ret_cor_channel_in_file(
                    w,
                    np.min([w + cutwindow, stop]),
                    average=average_before,
                    average_window=average_before_window,
                    dec=average_before_dec if average_before else None,
                )

                phiu = np.hstack((phiu, comp_phiu(c0, c90, c45, c135)))
        else:
            c0, c90, c45, c135 = self.ret_cor_channel_in_file(
                start,
                stop,
                average=average_before,
                average_window=average_before_window,
                dec=average_before_dec if average_before else None,
            )
            phiu = comp_phiu(c0, c90, c45, c135)

        if (
            init == 0
        ):  # if not the first loading I do have a reference so that I can compare to that one
            ref = np.interp(start, self.ind_ref, self.phi_ref)
            print(np.abs(phiu[0] % (2 * np.pi) - ref % (2 * np.pi)))
            if np.abs(phiu[0] % (2 * np.pi) - ref % (2 * np.pi)) > np.pi / 2:
                phiu += np.pi

        if raw == 0:  # this is the non linearity
            self.set_fcor(phiu=phiu, force=force_ref)
            phir = phiu % (2 * np.pi)
            phirc = self.fcor(phir)
            phiu = np.unwrap(phirc, period=np.pi)
        if cutwindow is not None:
            phir = phiu % (2 * np.pi)
            phiu = np.unwrap(phir, period=np.pi)
        return phiu

    def ret_all_var(self, start, stop, phiraw=0):
        """
        Return the unwrapped phase, the theta1
        Reads from loaded data
        """
        c0, c90, c45, c135 = self.ret_cor_channel(start, stop)
        phiu, theta1 = Fourkas(c0, c90, c45, c135, NA=1.3, nw=1.33)
        ref = np.interp(start, self.ind_ref, self.phi_ref)
        print(np.abs(phiu[0] % (2 * np.pi) - ref % (2 * np.pi)))
        if np.abs(phiu[0] % (2 * np.pi) - ref % (2 * np.pi)) > np.pi / 2:
            phiu += np.pi

        if phiraw == 0:
            if self.fcor is None:
                self.set_fcor(phiu=phiu)
            phir = phiu % (2 * np.pi)
            phirc = self.fcor(phir)
            phiu = np.unwrap(phirc, period=np.pi)
        else:
            phiu = np.unwrap(phiu, period=np.pi)

        return phiu, theta1

    def ret_raw_channels(
        self, start, stop, ordl=["0", "90", "45", "135"], data=None
    ):  # No decimation or data share
        if data is None:
            data = np.zeros([4, stop - start])
        for i in range(self.n_signals):
            data[i, :] = self._channels[i][start:stop]
        index = self.get_pol_ind(ordl)
        return (
            data[index[0], :],
            data[index[1], :],
            data[index[2], :],
            data[index[3], :],
        )

    def full_ordered_pol(self):
        pol_ind = self.get_pol_ind(["0", "90", "45", "135"])
        c0, c90, c45, c135 = [self.data[pol_ind[i], :] for i in range(len(pol_ind))]
        return c0, c90, c45, c135

    def time_to_index_in_file(self, xl):
        if isinstance(xl, list):
            xar = np.asarray(xl)
        else:  # if it is not a list
            xar = np.asarray([xl])
        ret = (xar - self.time_off) / self.time_inc
        ret = ret.astype("int")
        ret[ret < 0] = 0
        ret[ret >= self.datasize] = self.datasize - 1
        if isinstance(xl, list):
            return ret
        else:
            return ret[0]

    def index_in_file_to_time(self, xl):
        if isinstance(xl, list):
            xar = np.asarray(xl)
        else:
            xar = np.asarray([xl])

        xar[xar < 0] = 0
        xar[xar >= self.datasize] = self.datasize - 1
        ret = self.time_off + self.time_inc * xar
        if isinstance(xl, list):
            return ret
        else:
            return ret[0]

    def init_optics_matrix(self):
        self.matcorb = T_Icor_Matrix()  # 0,90,45,135 (45 is reflected)

        inds = self.get_pol_ind(["0", "90", "45", "135"])
        P = np.zeros([4, 4])
        for i in range(4):
            P[i, inds[i]] = 1
        self.matcor = np.dot(np.linalg.inv(P), np.dot(self.matcorb, P))

    def init_unitary_matrix(self):
        self.matcor = np.identity(4)
        self.matcorb = np.identity(4)

    def get_freq(self):
        return self.freq

    def get_size(self):
        return self.datasize

    # Below the functions depend on data share and the self.data preallocated

    def init_data_share(
        self,
        dec,
        timestart=0.0,
        timestop=10.0,
    ):  # called at the beginning or when change dec
        self.dec = 1
        if dec in [1, 2, 5, 10, 20, 50, 100]:
            self.dec = dec
        else:
            raise ValueError("Bad decimation value")

        lengths = [len(c) for c in self._channels]
        for L in lengths:
            if L != lengths[0]:
                raise RuntimeError("Channels do not have equal sizes")
        self.datasize = lengths[0]
        self.ld = np.min(
            [
                int(self.datasize / dec),
                self.max_size,
                int(
                    (
                        self.time_to_index_in_file(timestop)
                        - self.time_to_index_in_file(timestart)
                    )
                    / dec
                ),
            ]
        )
        if self.ld % 2 == 1:
            self.ld -= 1  # always even
        if self.ld < 0:
            self.ld = 0  # always and larger than 200

        self.data = np.zeros(
            [self.n_signals, self.ld]
        )  # references to the whole data that correspond to the channels
        self.update_data_from_file(0.5 * timestart + 0.5 * timestop)

    def update_data_from_file(self, time=-2, norep=0):
        center = self.time_to_index_in_file([time])[0]
        if center < self.ld / 2 * self.dec:
            center = self.ld / 2 * self.dec
        if center + self.dec * self.ld / 2 > self.datasize:
            center = self.datasize - self.ld / 2 * self.dec
        if center == self.center and norep == 1:
            return 1

        if time == -2:
            center = self.center

        self.center = center
        imin = int(center - self.ld / 2 * self.dec)
        for i in range(self.n_signals):
            if self.dec == 1:
                self.data[i, :] = (
                    self.b[i] + self.a[i] * self._channels[i][imin : imin + self.ld]
                )
            elif self.dec_average:
                self.data[i, :] = self.b[i] + self.a[i] * np.mean(
                    self._channels[i][imin : imin + self.ld * self.dec].reshape(
                        [self.ld, self.dec]
                    ),
                    axis=1,
                )
            else:
                self.data[i, :] = (
                    self.b[i]
                    + self.a[i]
                    * self._channels[i][imin : imin + self.ld * self.dec : self.dec]
                )
        self.data = np.dot(self.matcor, self.data)

        self.indstart = imin  # starting index of the file where the signal is read
        self.iminmem = imin  # starting index of the file in mem
        self.imaxmem = imin + int(
            self.dec * (len(self.data[0, :]) - 1)
        )  # stop index of the file in mem
        self.xminmem = self.index_in_file_to_time(self.iminmem)
        self.xmaxmem = self.index_in_file_to_time(self.imaxmem)
        self.xs = self.index_in_file_to_time(
            np.arange(self.iminmem, self.imaxmem + 1, self.dec)
        )
        self.dec_in_mem = self.dec
        self.dec_average_in_mem = self.dec_average
        return 0

    def ret_loaded_data(self, ordl=["0", "90", "45", "135"]):
        index = self.get_pol_ind(ordl)
        return (
            self.data[index[0], :],
            self.data[index[1], :],
            self.data[index[2], :],
            self.data[index[3], :],
        )

    def time_to_index_in_mem(self, xl):
        if isinstance(xl, list):
            xar = np.asarray(xl)
        else:
            xar = np.asarray([xl])
        ret = (xar - self.time_off) / self.time_inc
        print(ret)
        ret = ret.astype("int")
        ret -= self.indstart
        ret = ret / self.dec
        ret = ret.astype("int")
        ret[ret < 0] = 0
        ret[ret >= self.ld] = self.ld - 1  # index in mem can not be larger than ld
        if isinstance(xl, list):
            return ret
        else:
            return ret[0]

    def get_min_max_partial(self, xl):
        inds = self.time_to_index_in_mem(xl)
        mins = [np.min(self.data[i, inds[0] : inds[1]]) for i in range(self.n_signals)]
        maxs = [np.max(self.data[i, inds[0] : inds[1]]) for i in range(self.n_signals)]
        return np.min(mins), np.max(maxs)


#    def update_data_from_file_old(self,time,norep=0):


#        center = self.time_to_index_in_file([time])[0]
#        if (center < self.ld/2*self.dec):
#            center = self.ld/2*self.dec
#        if (center + self.dec*self.ld/2 > self.datasize):
#            center = self.datasize - self.ld/2*self.dec
#        if (center == self.center and norep == 1):
#            return 1

#        if time == -2:
#            center = self.center


#        self.center = center
#        imin = int(center - self.ld/2*self.dec)
#        imax = int(center + self.ld/2*self.dec)
#        for i in range(self.n_signals):
#                if self.dec == 1:
#                    self.data[i,:] = self.b[i]+self.a[i]*self._channels[i][imin:imin+self.ld]
#                elif self.dec_average:
#                    self.data[i,:] = self.b[i]+self.a[i]*np.mean(self._channels[i][imin:imin+self.ld*self.dec].reshape([self.ld,self.dec]),axis=1)
#                else:
#                    self.data[i,:] = self.b[i]+self.a[i]*self._channels[i][imin:imin+self.ld*self.dec:self.dec]
#        self.xs[:] = self.time_off + self.time_inc * np.arange(imin,imin+self.ld*self.dec,self.dec)
#        self.indstart = imin  #starting index of the file where the signal is read
#        self.minymem = np.min(np.asarray(self.data[i,:]))
#        self.maxymem = np.max(np.asarray(self.data[i,:]))
#        self.minxmem = np.min(np.asarray(self.xs))
#        self.maxxmem = np.max(np.asarray(self.xs))
#        return 0
