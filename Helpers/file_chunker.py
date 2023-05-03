# This Python file uses the following encoding: utf-8

import sys,os
import multiprocessing as mp
import numpy as np
import tables
from pathlib import Path
sys.path.insert(0, os.path.dirname(sys.path[0]))
from NIfile import NIfile
from multiprocessing.managers import SyncManager

outfolder=os.getenv("RODFAN")


def kwargs_to_string(**kwargs):
    return "_".join(f"{key}_{value}" for key, value in kwargs.items())

def worker1(c1,c2,f,func,q,**kwargs):
    phi = f.ret_phi(int(c1),int(c2))
    x,y=func(phi,c1/f.get_freq(),c2/f.get_freq(),**kwargs) #time given by the freq
    if (x is None or y is None):
        return None
    else:
        return(((x,y)))

def writef(filename,x,y):
    '''listens for messages on the q, writes to file. '''
    with tables.open_file(filename, mode='a') as fn:
        fn.root.data.append(np.vstack((x,y)))


def handler(error):
    print(f'Error: {error}', flush=True)

def file_chuncker(tdmspath,chunk_size,func,tstart=0,tmax=-1,nworker=-1,overlap=None,title="",force=0,dec=1,chunks=None,**kwargs):

    # initialize file chunker
    SyncManager.register("NIfile",NIfile)


    manager = mp.Manager()
    q = manager.Queue()
    if nworker >0:
        pool = mp.Pool(nworker)
    else:
        pool = mp.Pool(mp.cpu_count()+1)

    inst = manager.NIfile(tdmspath,dec=dec,max_size=20)
    freq = inst.get_freq()
    datasize = inst.get_size()

    lmax = datasize
    tmaxd = (datasize-1)/freq


    if tmax==-1:
        tmax = tmaxd
    if tmax>tmaxd:
        tmax = tmaxd

    if tstart<0:
        tstart=0

    if tstart > tmax:
        return



    outf = outfolder+func.__name__+"_tstart_"+str(round(tstart,3))+"_tstop_"+str(round(tmax,3))+"_"+kwargs_to_string(**kwargs)+'.h5'
    if os.path.exists(outf) and force!=1:
        print("file exist")
        return outf

    if chunks is None:
        if overlap is None:
            chunksstart = np.arange(tstart*freq,tmax*freq,chunk_size*freq)
            chunksstop =  chunksstart+chunk_size*freq
        else:
            chunksstart = np.arange(tstart*freq,tmax*freq-chunk_size,overlap*freq)
            chunksstop = chunksstart+chunk_size*freq




    else:
        chunksstart = chunks[0]
        chunksstop = chunks[1]


    fn = tables.open_file(outf, mode='w')
    atom = tables.Float64Atom()
    fn.create_earray(fn.root, 'data', atom, (2, 0),title="")
    fn.close()




    #put listener to work first
    #watcher = pool.apply_async(listener, (outf,q),error_callback=handler)

    #fire off workers
    jobs = []

    for i in range(len(chunksstart)):
        job = pool.apply_async(worker1,args=(chunksstart[i],chunksstop[i],inst,func,q),kwds=kwargs,error_callback=handler)
        jobs.append(job)
    for i in range(len(chunksstart)):
        r=jobs[i].get()
        print("Analyzing Chunk ["+str(chunksstart[i])+","+str(chunksstop[i])+"]")
        if r is not None:
            x,y=r
            writef(outf,x,y)

    #q.put(('kill',0))
    pool.close()
    pool.join()

    return outf





