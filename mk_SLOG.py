#!/usr/bin/env python3

'''
VERSION: 22.01.2020

Obtain averaged spectrum at selected timestep

ARGS = TIMESTEP
'''

import sys,os,glob,gzip
import pandas as pd
import argparse
import numpy as np
import matplotlib
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
my_parser.add_argument('-title', action='store', dest="toptitle", type=str,
                       required=True, help="requested title", nargs='*')                       
args = my_parser.parse_args()

ran = args.ran
kick = args.kick
toptitle = args.toptitle

#https://stackoverflow.com/questions/4138202/using-isdigit-for-floats
def isFigit(x):
  try:
    float(x)
    return True
  except ValueError:
    return False
#https://stackoverflow.com/questions/31742326/efficient-way-of-reading-integers-from-file
def read_dirs(filename):
  with open (filename,"r") as r:
    list_dir = [float(i)  for line in r for i in line.split() if isFigit(i)]
    m = len(list_dir)
    list_dir = list(dict.fromkeys(list_dir))
    n = len(list_dir)
    if (m!=n): print("'{}' in '{}' saved', {}' duplicate(s) ignored"
                    .format(n,filename,m-n))
    else: print("'{}' in '{}' saved".format(n,filename))
    return list_dir
#-> reading the file which contains the names of directories
ran_dirs=read_dirs(ran)
kick_dirs=read_dirs(kick)
#-> convert RAN to integer
for i in range(len(ran_dirs)): ran_dirs[i]=int(ran_dirs[i])
for i in range(len(ran_dirs)): ran_dirs[i]=str(ran_dirs[i])
for i in range(len(kick_dirs)): kick_dirs[i]=str(kick_dirs[i])
    
def get_Sheader(filename):
  data = pd.read_csv(filename,delim_whitespace=True)  
  heads=[]
  for col in data.columns: 
      heads.append(col)
  return heads,len(heads)
    
def read_lamE(file_name):
  result=dict()    
  heads,n=get_Sheader(file_name)
  df = pd.read_csv(file_name,delim_whitespace=True, skiprows=1,header=None) 
  for i in range(n):
      result[i]=np.asarray(df[i])
  return result

def TITLE(k,n):
  if (toptitle!=None):
    mytitle = "{} AVE_V: kick={}, n_samples={}".format(toptitle,k,n)
    alltilte= "{} AVE_V: n_samples={}".format(toptitle,n)
  else: 
    mytitle = "AVE_V: kick={}, n_samples={}".format(k,n)
    alltilte = "AVE_V: n_samples={}".format(n)
  return mytitle, alltilte

def plot(k):
  n = 0
  for r in (ran_dirs):
    slog_path = './'+r+'/'+k+'/'+"SLOG.0"
    if (os.path.exists(slog_path)): pass
    else: 
      print("'{}' not exist".format(slog_path))
      continue
    Sheads, nE = get_Sheader(slog_path)
    SLog = read_lamE(slog_path)
    tmp = SLog[2]**2 + SLog[3]**2
    tmp = tmp**0.5
    if n==0:
      s1=tmp; s2=s1**2
    else:
      s1+=tmp; s2+=tmp**2
    n+=1
  print('NUMBER OF SLOG FILES FOR kick = {} is {}'.format(k,n))
  # normalize; compute standard deviation
  s1/=n; s2/=n; s2-=s1**2; s2=s2**0.5
  xdata = SLog[0]*0.001
  mytitle,_ = TITLE(k,n)
  plt.plot(xdata,s1)
  plt.title(mytitle)
  plt.xlabel('time')
  plt.ylabel('V of COM')
  plt.fill_between(xdata,s1-s2/2,s1+s2/2,color='gray',alpha=0.2)


if (os.path.exists('./mean_slog')): pass
else: os.mkdir('./mean_slog')

# make array of mode index, needed for plotting
for k in (kick_dirs):
  plot(k)
  outpic = "./mean_slog/" + k +".png"
  plt.savefig(outpic,bbox_inches='tight')
  plt.close()

def plot_AllInOne():
  for k in (kick_dirs):
    n = 0
    for r in (ran_dirs):
      slog_path = './'+r+'/'+k+'/'+"SLOG.0"
      if (os.path.exists(slog_path)): pass
      else: 
        print("'{}' not exist".format(slog_path))
        continue
      Sheads, nE = get_Sheader(slog_path)
      SLog = read_lamE(slog_path)
      tmp = SLog[2]**2 + SLog[3]**2
      tmp = tmp**0.5
      if n==0:
        s1=tmp; s2=s1**2
      else:
        s1+=tmp; s2+=tmp**2
      n+=1
    # normalize; compute standard deviation
    s1/=n; s2/=n; s2-=s1**2; s2=s2**0.5
    xdata = SLog[0]*0.001
    _,alltitle = TITLE(k,n)
    plt.plot(xdata,s1,label=k)
    plt.legend()
    plt.title(alltitle)
    plt.xlabel('time')
    plt.ylabel('V of COM')
    plt.fill_between(xdata,s1-s2/2,s1+s2/2,color='gray',alpha=0.2)
    outpic = "./mean_slog/all.png"
    plt.savefig(outpic,bbox_inches='tight')
  
plot_AllInOne()  

