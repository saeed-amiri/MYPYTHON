#!/usr/bin/env python3

'''
VERSION: 08.01.2020
based on mk_plots.py by RV
'''
import os
import argparse
import matplotlib
import numpy as np
import pandas as pd
import sys,os,glob,gzip
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from matplotlib.collections import PatchCollection
from color_print import *

my_parser = argparse.ArgumentParser(prog="mk_plots.py",
            usage="%(prog)s -id <RUNID> [-w <MODETOWRITE> -p <MODEPLOT>] ",
            description='plot MODES properties',
            epilog="need COLOR.RUNID.gz, MODEINFO",
            prefix_chars="-")

# Execute the parse_args() method
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-id', action='store', type=str, dest="RUNID",
                       required=True)
my_parser.add_argument('-write', action='store', dest="fmodes", type=str)
my_parser.add_argument('-plot', action='store', dest="fplots", type=str)

args = my_parser.parse_args()

RUNID=args.RUNID
fmodes=args.fmodes
fplot=args.fplots

# read the COLOR file
def read_colorfile(RUNID):
  f='color.'+RUNID+'.gz'
  print('reading:',f)
  # read number of eigenmodes = first line of file
  with gzip.open(f) as fp:
    numpoints = int( fp.readline() )
    print('number of eigenmodes:',numpoints)
  # read the remaining data 
  color = pd.read_csv(f,compression='gzip',delim_whitespace=True,skiprows=1,header=None)
  # column 0 contains the time step: make this the index
  color=color.set_index(0)
  # make sure index is treated as integer (!)
  color.index=color.index.astype(int)
  # sort data in order of increasing index
  color=color.sort_index()
  # number of computed quantities per eigenmode
  nf=color.shape[1]//numpoints
  print('number of fields:',nf)
  # number of snapshots in the MD trajectory
  numframes=color.shape[0]
  print('number of snapshots:',numframes)
  # rename columns as integers starting from 0
  color.columns=np.arange(nf*numpoints,dtype=int)
  # RETURN IT (!)
  return color,numpoints,numframes,nf

# read the data
color,numpoints,numframes,nf=read_colorfile(RUNID)
modeinfo=np.loadtxt('MODEINFO.'+RUNID).T; freq=modeinfo[0]

# return energy as function of time for mode m
def energy_vs_time(m):
  # displacement \times frequencey
  u = color[nf*m]*freq[m]
  # velocity
  v = color[nf*m+1]
  # etot = potential + kinetic (note: potential energy = harmonic approximation, not exact)
  return 0.5*(u*u+v*v)

def write_energy_vs_time(m):
  outarr=energy_vs_time(m)
  out_file=str(m) + "_totalE"
  np.savetxt(out_file,outarr)


if(fplot!=None):
  if (os.path.exists(fplot)==True):
    with open(fplot, 'r') as f:
      for mlines in f:
        if len(mlines.split()) == 0:
            continue
        plt.plot(energy_vs_time(int(mlines.strip())),label=mlines.strip())
    f.close()
  else:
    print_violet("no such file as ./{} for plot`ing".format(fplot))
    for i in range(3):
      plt.plot(  energy_vs_time(i) , label=i )
else:
  for i in range(3):
    plt.plot(  energy_vs_time(i) , label=i )

if(fmodes!=None):
  if (os.path.exists(fmodes)==True):
    print("writing info for modes in file '{}'".format(fmodes))
    with open(fmodes, 'r') as f:
      for mlines in f:
        if len(mlines.split()) == 0:
            continue
        write_energy_vs_time(int(mlines.strip()))
    f.close()
  else:
    print_violet("no such file as ./{} for writing".format(fmodes))
    for i in range(3):
      write_energy_vs_time(i)
else:
  for i in range(3):
    write_energy_vs_time(i)


plt.legend()
plt.show()

# return energy of all modes at 'timestep' i
def energy_all_modes(i):
  # tmp is the i-th ROW of the 'color' dataframe
  tmp=np.asarray(color.iloc[i])
  # kinetic energy
  ke=tmp[1::nf]; ke*=0.5*ke
  # potential energy
  pe=tmp[0::nf]*freq; pe*=0.5*pe
  etot=ke+pe
  etot=etot[3:]
  #etot/=etot.max()
  return etot

# set INDEX for starting point
if len(sys.argv) > 2:
  INDEX=int(sys.argv[2])
else: INDEX=0

fig=plt.figure()
plt.plot(energy_all_modes(INDEX))

# upon keypress, update the colors, or save image, or exit...
def on_keyboard(event):
  global PCL,INDEX
  if event.key == 'right':
    INDEX+=1
    if INDEX==numframes: INDEX=0
  elif event.key == 'left':
    INDEX-=1
    if INDEX==-1: INDEX=numframes-1
  elif event.key == 'w':
    fname = 'FIGURE.' + str(INDEX) + '.png'
    print('saving figure:',fname)
    plt.savefig(fname)
    return
  else: exit()
  print(INDEX,energy_all_modes(INDEX).max(),np.argmax(energy_all_modes(INDEX)))
  plt.clf()
  plt.plot(energy_all_modes(INDEX))
  fig.canvas.draw_idle()


fig.canvas.mpl_connect('key_press_event',on_keyboard)

plt.show()