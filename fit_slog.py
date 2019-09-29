#!/usr/bin/env python
import sys
import csv
import glob
import inspect
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt

system = sys.argv[1]
ftime = 800
itimes = [0.9, 0.8, 0.7, 0.6]

unsorted_files = (glob.glob('SLOG_*'))
files = sorted(unsorted_files, key=lambda x: float(x.split('_')[1]))

#!reading "PARAM.base" file
def read_PARAM(param):
    with open(param, 'r') as f:
        mlines = f.readlines()
    tmp_line = mlines[0].split("#")
    ang_line = mlines[1].split("#")
    temperature = tmp_line[1].split("=")[1]
    angle = ang_line[1].split("=")[1]
    return temperature.strip(), angle.strip()

#!reading "SLOG.VK" files
def read(file_name):
    df=pd.read_csv(file_name,delim_whitespace=True,header=None)
    t  = np.asarray((df[0]-df[0][0])*0.001,dtype=float)
    ux = np.asarray(df[1],dtype=float)
    uy = np.asarray(df[2],dtype=float)
    vv = np.sqrt(ux*ux + uy*uy)
    tstep = t[:ftime]
    v     = vv[:ftime]
    return tstep, v

#!plotting raw speed decay
def plot_speed():
    sfig = plt.figure()
    sax=sfig.add_subplot(1,1,1)
    sax.set_title(TITELS)
    sax.set_xlim(0,300)
    for f in files:
        labeler=f.split("_")
        t,v = read(f)
        sax.plot(t,v,label=labeler[1])
    sax.set_xlabel("time")
    sax.set_ylabel("speed")
    sfig.savefig("speed.png",bbox_inches='tight')

#!plotting log of raw speed decay
def plot_logspeed():
    logfig = plt.figure()
    logax=logfig.add_subplot(1,1,1)
    logax.set_title(TITELS)
    logax.set_xlim(0,300)
    logax.set_ylim(0.01,2)
    logax.set_yscale("log")
    for f in files:
        labeler=f.split("_")
        t,v = read(f)
        logax.plot(t,v,label=labeler[1])
    logax.legend()
    logax.set_xlabel("time")
    logax.set_ylabel("log(speed)")
    logfig.savefig("speed_log.png",bbox_inches='tight')


#!reurning the name of an array as a string
#https://stackoverflow.com/
# questions/18425225/getting-the-name-of-a-variable-as-a-string
def retrieve_name(var):
    """
    Gets the name of var. Does it from the out most frame inner-wards.
    :param var: variable to get name from.
    :return: string
    """
    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if 
                var_val is var]
        if len(names) > 0:
            return names[0]


#!fitting function
def myfunc(x,a,b):
    return a*np.exp(-x/b)

#!finding the closest value of a list to a certain value

#!https://www.geeksforgeeks.org/
# python-find-closest-number-to-k-in-given-list/
def closest(list, k):
    lst = np.asanyarray(list)
    idx = (np.abs(lst - k)).argmin()
    return idx

#!plotting the speed decay with fitting lines
def plot_all(tau,a):
    allfig = plt.figure()
    allax=allfig.add_subplot(1,1,1)
    allax.set_title(TITELS)
    i=0
    for f in files:
        time,v=read(f)
        labeler=f.split("_")
        itime=closest(v,v[0]*itimes[-1])
        t = time[itime:]
        allax.plot(time,v,label=labeler[1])
        allax.plot(t,myfunc(t,a[i],tau[i]),'k',ls='--')
        i+=1
    allax.set_xlabel("time")
    allax.set_ylabel("speed")
    allax.set_xlim(0,ftime)
    allfig.savefig("fit.png",bbox_inches='tight')

#!plot all the information from fitting the SLOGs
def plot_fit_coeff(type,ydata,n):
    fig = plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax.set_title(TITELS)
    ax.set_xlim(speed[0],speed[-1])
    ax.set_xlabel("kick velocity")
    if (type == "t0"):
        ax.set_ylabel(r"${}$".format(type))
    else: ax.set_ylabel(r"$\{}$".format(type))
    maxy=[];miny=[]
    for i in range(n):
        labeling = str(itimes[i]) + "VK"   
        ax.plot(speed,ydata[i],'-',label=labeling)
        ax.plot(speed,ydata[i],'.')
        maxy.append(np.max(ydata[i]))
        miny.append(np.min(ydata[i]))
    ly = np.min(miny); hy = np.max(maxy)
    ax.set_ylim(ly-ly*0.1,hy+hy*0.1)
    outter="{}.png".format(type)
    ax.legend()
    fig.savefig(outter,bbox_inches='tight')

#!writting the fitting information
def write_out(type,ydata,n):
    speeds = np.asarray(speed)
    out_file = type  + "_" + temp + "_s" + system
    outarr = np.vstack([speeds,ydata]).T
    np.savetxt(out_file, outarr, delimiter='\t')

#!doing the fit!
n = int(len(itimes))
number_files = int(len(unsorted_files))
tau   = np.zeros((n,number_files))
alpha = np.zeros((n,number_files))
t0  = np.zeros((n,number_files))
i = 0
for j in range(n):
    speed=[]; alpha0=[]; tau0=[]; time0=[]
    perc = itimes[i]
    print(j,"fit from", perc)
    for f in files:
        t,v=read(f)
        itime = closest(v,v[0]*perc)
        time = t[itime:]
        velc = v[itime:]
        p,c = optimize.curve_fit(myfunc,time,velc,p0=[1.0,90.0])
        speed.append(v[0]); alpha0.append(p[0])
        tau0.append(p[1]) ; time0.append(itime)
    tau[i]=tau0; alpha[i]=alpha0; t0[i]=time0
    i+=1

temp, angle = read_PARAM("PARAM.base")
TITELS = "T = {}, \u03B8 = {}, sys.{}".format(temp, angle,system)

#!ploting & saving fit coeffs
for i in [tau, alpha, t0]:
    ilabel = retrieve_name(i)
    plot_fit_coeff(ilabel,i,n)
    write_out(ilabel,i,n)

plot_all(tau[0],alpha[0])
plot_logspeed()
plot_speed()
