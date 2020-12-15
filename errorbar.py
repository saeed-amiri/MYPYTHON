#!/usr/bin/env python
import sys
import glob
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt

itemp  = [0.032, 0.065, 0.131, 0.262]
itype  = ['tau*', 't0*', 'alpha*']
iseed  = ['s1', 's2', 's3', 's4', 's5', 's5b' ]
itimes = [0.9, 0.8, 0.7, 0.6] 
ntimes = int(len(itimes))

colorlist = ['b', 'r', 'g', 'm', 'y', 'c']


def get_files(file_type):
    unsorted_files = (glob.glob(file_type))
    files = sorted(unsorted_files, key=lambda x: str(x.split('_')[2]))
    return files

def files_info(file_name):
    file_id = file_name.split('_')[0]
    temp = file_name.split('_')[1]
    system = file_name.split('_')[2]
    return file_id,temp,system

#!reading  files
def read_files(file_name):
    df=pd.read_csv(file_name,delim_whitespace=True,header=None)
    m, n = df.shape
    datas = np.zeros([m, n])
    for i in range(ntimes+1):
        datas[:,i] = np.asarray(df[i],dtype=float)
    return datas


def write_ave(types,temp,speed,ydata):
    speeds = np.asarray(speed)
    outarr = np.vstack([speeds,ydata]).T
    out_file = "ave_" + types  + "_" + str(temp) 
    np.savetxt(out_file, outarr, delimiter='\t')

bb_ave = np.zeros((ntimes,17))
llist = len(get_files("tau_*"))
for t in itype:
    for j in range(ntimes):
        bb=[0]*17;vk=[0]*17
        i = 0
        for f in get_files(t):
            b1 = read_files(f) 
            ids,temp,system = files_info(f)
            plt.plot(b1[:,0],b1[:,j+1],':',c=colorlist[i],lw = 0.5)
            bb = np.add(bb, b1[:,j+1])
            vk = np.add(vk, b1[:,0])
            i+=1
        plt.plot(vk/llist,bb/llist,'.-',c=colorlist[j],lw = 1.2, label=itimes[j])
        bb_ave[j] = bb/llist       
        plt.title(r"T = {}, ({} sys)".format(temp,llist))
        plt.xlabel("VK");plt.ylabel(r"${}$".format(ids))
    plt.legend()
    outpic = "{}_{}.png".format(temp,ids)
    plt.savefig(outpic,bbox_inches='tight')
    plt.close()
    write_ave(ids,temp,vk/llist,bb_ave)

plt.close()
exit()
'''
for i in itype:
    for j in range(ntimes):
        bb=[0]*17;vk=[0]*17
        for f in get_files(t):
            ids,temp,_=files_info(f)
            b1 = read_files(f)
            bb = np.add(bb, b1[:,j+1])
            vk = np.add(vk, b1[:,0])
        plt.plot(vk/llist,bb/llist,label=temp)
        plt.xlabel("VK"); plt.ylabel(ids)
        plt.title("fit from {} VK".format(itimes[j]))
        plt.legend()
        outpic = "{}_{}.png".format(itimes[j],ids)
        plt.savefig(outpic,bbox_inches='tight')
        plt.close()


#plt.show()'''