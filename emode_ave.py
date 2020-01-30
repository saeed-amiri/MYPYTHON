#!/usr/bin/env python

'''
VERSION: 30.01.2020

Obtain averaged energy of selected mode(s)

'''

import sys,os,glob,gzip
import pandas as pd
import argparse
import numpy as np
import matplotlib
import matplotlib as mpl
from matplotlib.patches import Circle,Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
import matplotlib.pyplot as plt

my_parser = argparse.ArgumentParser(prog="mk_plots.py",
            usage="%(prog)s -id <RUNID> [ -k <kick> -w <MODETOWRITE> -p <MODEPLOT>] ",
            description='plot MODES properties',
            epilog="need COLOR.RUNID.gz, MODEINFO",
            prefix_chars="-")

# Execute the parse_args() method
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-ran', action='store', dest="ran",type=str,
                       required=True, help="the file contain the seed numbers")
my_parser.add_argument('-kick', action='store', dest="kick", type=str,
                       required=True, help="requested kick")
my_parser.add_argument('-modes', action='store', dest="modes", type=str,
                       required=True, help="file contains the mode(s) number")                       
args = my_parser.parse_args()

ran = args.ran
modes= args.modes
kick = args.kick


#https://stackoverflow.com/questions/31742326/efficient-way-of-reading-integers-from-file
def read_dirs(filename):
  with open (filename,"r") as r:
    list_dir = [int(i)  for line in r for i in line.split() if i.isdigit()]
    m = len(list_dir)
    list_dir = list(dict.fromkeys(list_dir))
    n = len(list_dir)
    if (m!=n): print("'{}' dirs in '{}'', {}' duplicate(s) ignored"
                    .format(n,filename,m-n))
    else: print("'{}' dirs in '{}'".format(n,filename))
    return list_dir

#-> reading the file which contains the names of directories
ran_dirs=read_dirs(ran)
mode_dirs=read_dirs(modes)
#-> convert RAN to integer
for i in range(len(ran_dirs)): ran_dirs[i]=str(ran_dirs[i])
for i in range(len(mode_dirs)): mode_dirs[i]=str(mode_dirs[i])

def read_modes(mode):
    return np.loadtxt(mode)
    


#print(mode_dirs)
mode_f = "./2407/2.0/"+mode_dirs[0] + "_totalE"

# TIMESTEP FOR WHICH TO AVERAGE THE SPECTRUM
print(kick)
def spec_plot(mode):
  n = 0
  plt.clf()
  for r in (ran_dirs):
    mode_path = './'+r+'/'+kick+'/'+ str(mode) + "_totalE"
    if (os.path.exists(mode_path)): pass
    else: 
      print("'{}' not exist".format(mode_path))
      continue
    tmp = read_modes(mode_path)
    if n==0:
      s1=tmp; s2=s1**2
    else:
      s1+=tmp; s2+=tmp**2
    n+=1
  # normalize; compute standard deviation
  s1/=n; s2/=n; s2-=s1**2; s2=s2**0.5
  # set data for modes=0,1,2 to __ZERO__ 
  for i in range(3):
    s1[i]=s2[i]=0  
  #make array of mode index, needed for plotting
  m=np.arange( len(s1) )
  plt.plot(m,s1)
  print(np.max(s1),np.argmax(s1))
  plt.title('AVERAGED ENERGY: kick ={}, mode={}, nsys={}'.format(kick,mode,n))
  plt.xlabel('time')
  plt.ylabel('ENERGY')
  plt.fill_between(m,s1-s2/2,s1+s2/2,color='gray',alpha=0.2)
  outfig = ("{}_{}.png".format(mode,kick))
  plt.savefig(outfig, transparent=True)
  #plt.show()

def plot_all():
  for mode in (mode_dirs):
    n = 0
    if (mode == '0'): continue
    for r in (ran_dirs):
      mode_path = './'+r+'/'+kick+'/'+ str(mode) + "_totalE"
      if (os.path.exists(mode_path)): pass
      else: 
        print("'{}' not exist".format(mode_path))
        continue
      tmp = read_modes(mode_path)
      if n==0:
        s1=tmp
      else:
        s1+=tmp
      n+=1
    s1/=n
    # set data for modes=0,1,2 to __ZERO__ 
    for i in range(3):
      s1[i]=0  
    #make array of time, needed for plotting
    m=np.arange( len(s1) )
    plt.plot(m,s1,label=mode)
  plt.title('AVERAGED ENERGY: kick ={}, nsys={}'.format(kick,n))
  plt.xlabel('time')
  plt.ylabel('ENERGY')
  plt.legend()
  outfig = ("all_mode_{}.png".format(kick))
  #plt.show()
  plt.savefig(outfig, transparent=True)


for m in (mode_dirs):
  spec_plot(m)
plt.clf()
plot_all()
