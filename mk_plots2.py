#!/usr/bin/env python3

'''
VERSION: 08.01.2020
based on mk_plots.py by RV
'''
import argparse
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import sys,os,glob,gzip,shutil
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from matplotlib.collections import PatchCollection
from color_print import *

my_parser = argparse.ArgumentParser(prog="mk_plots.py",
            usage="%(prog)s -id <RUNID> [ -k <kick> -w <MODETOWRITE> -p <MODEPLOT>] ",
            description='plot MODES properties',
            epilog="need COLOR.RUNID.gz, MODEINFO",
            prefix_chars="-")

# Execute the parse_args() method
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-id', action='store', dest="RUNID",type=str,
                       required=True, help="the RUNID")
my_parser.add_argument('-kick', action='store', dest="kick",type=str,
                       required=False, help="the kick velocity")
my_parser.add_argument('-write', action='store', dest="fmodes", type=str,
                      help="file with the index of mode to write energy")
my_parser.add_argument('-plot', action='store', dest="fplots", type=str,
                      help="file with the index of mode to plot energy")
my_parser.add_argument('-intg', action='store', dest="fintg", type=str,
                      help="file to claculate the area under the energy plot")
my_parser.add_argument('-screen', action='store', dest="screen", type=str,
                      help="to turn off plt.show() ")
my_parser.add_argument('-energy', action='store', dest="efile", type=str,
                      help="to read energy file")                      

args = my_parser.parse_args()

RUNID  = args.RUNID
fmodes = args.fmodes
fplot  = args.fplots
fintg  = args.fintg
kick   = args.kick
screen = args.screen
efile  = args.efile

def get_Eheader(filename):
  data = pd.read_csv(filename,delim_whitespace=True)  
  heads=[]
  for col in data.columns: 
      heads.append(col)
  return heads,len(heads)
    
def read_lamE(file_name):
  result=dict()    
  heads,n=get_Eheader(file_name)
  df = pd.read_csv(file_name,delim_whitespace=True, skiprows=1,header=None) 
  for i in range(n):
      result[i]=np.asarray(df[i])    
  return result

# read the COLOR file
def read_colorfile(RUNID):
  if (kick!=None): f='color_'+kick+'.'+RUNID+'.gz'; print_blue(f)
  else: f='color.'+RUNID+'.gz'; print('reading:',f)
  # read number of eigenmodes = first line of file
  with gzip.open(f) as fp:
    nums = (fp.readline()).decode("utf-8")
    numpoints = int(nums.split(" ")[0]) 
    nsteps = int(nums.split(" ")[1]) 
    nprops = int(nums.split(" ")[2]) 
    print('#eigenmodes: {}, #steps: {}, #prop: {}:'
          .format(numpoints,nsteps,nprops))
  # read the remaining data 
  color = pd.read_csv(f,compression='gzip',delim_whitespace=True,
                      skiprows=1,header=None)
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

if (efile!=None):
  Eheads, nE = get_Eheader(efile)
  Energys = read_lamE(efile)

# read the data
color,numpoints,numframes,nf=read_colorfile(RUNID)
if (kick!=None): fm='MODEINFO_'+kick+'.'+RUNID; print_blue(fm)
else: fm='MODEINFO.'+RUNID; print(fm)
modeinfo=np.loadtxt(fm).T; freq=modeinfo[0]

# return energy as function of time for mode m
def energy_vs_time(m):
  # displacement \times frequencey
  u = color[nf*m]*freq[m]
  # velocity
  v = color[nf*m+1]
  # etot = potential + kinetic 
  # (note: potential energy = harmonic approximation, not exact)
  return 0.5*(u*u+v*v)

# return energy of all modes at 'timestep' i
def energy_all_modes(i):
  # tmp is the i-th ROW of the 'color' dataframe
  tmp=np.zeros(numpoints,dtype=float); ke=np.zeros(numpoints,dtype=float)
  pe =np.zeros(numpoints,dtype=float); ke=np.zeros(numpoints,dtype=float)
  tmp=np.asarray(color.iloc[i])
  # kinetic energy
  ke=tmp[1::nf]; ke=0.5*ke*ke
  # potential energy
  pe=tmp[0::nf]*freq; pe=0.5*pe*pe
  etot=ke+pe
  #etot=etot[3:]
  #etot/=etot.max()
  return etot



def total_energy(m):
  return np.sum(energy_all_modes(m))

def write_energy_vs_time(m):
  outarr=energy_vs_time(m)
  if (kick!=None):out_file=kick+"_totalE."+str(m) 
  else :out_file=str(m) + "_totalE"
  np.savetxt(out_file,outarr)

#https://thispointer.com/python-how-to-move-files-and-directories/
def moveAllFilesinDir(dstDir):
  # Check if both the are directories
  Path=os.path.abspath('./')
  if (os.path.isdir(dstDir)==False): os.mkdir(dstDir)
  # Iterate over all the files in source directory
  srcFiles=dstDir+"_totalE"+".*"
  for filePath in glob.glob(srcFiles):
    # Move each file to destination Directory
    if (os.path.exists(os.path.join((Path+"/"+kick+"/"),filePath))):
      os.remove(os.path.join((Path+"/"+kick+"/"),filePath))
    shutil.move(os.path.join(Path,filePath),os.path.join(Path,dstDir))

# set INDEX for starting point of energy_all_modes
INDEX = 0
#! plot energy of mode vs time
if(fplot!=None):
  if (os.path.exists(fplot)==True):
    with open(fplot, 'r') as f:
      ModeList=[]
      for mlines in f:
        if len(mlines.split()) == 0:
            continue
        ModeList.append(int(mlines.strip()))
      ModeList.sort()
      for m in ModeList:
        plt.plot(energy_vs_time(m),label=m)
        INDEX = int(m)
      plt.xlabel("time"); plt.ylabel("energy")
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
        if (kick!=None): moveAllFilesinDir(kick)
    f.close()
  else:
    print_violet("no such file as ./{} for writing".format(fmodes))
    for i in range(3):
      write_energy_vs_time(i)
else:
  for i in range(3):
    write_energy_vs_time(i)

plt.legend()
if (screen!=None):
  if screen == "off":
    pass
else: plt.show()

if(fintg!=None):
  if(os.path.exists(fintg)==True):
    with open(fintg, 'r') as f:
      for mlines in f:
        if len(mlines.split())==0:
          continue
        intg = np.trapz(energy_vs_time(int(mlines.strip())))
        print("integral of mode {} is {:.2f}".format(mlines.strip(),intg))
                


fig=plt.figure()
plt.plot(energy_all_modes(INDEX))

def Etitle(m):
  if (efile!=None):
    etitl = ("t:{},lmp_({}+{}): {:.3f},modeE:{:.3f}"
            .format(m,Eheads[2],Eheads[1],Energys[2][m]+Energys[1][m],
              total_energy(m)))
  else:
    etitl = str(m)
  return etitl

# upon keypress, update the colors, or save image, or exit...
def on_keyboard(event):
  global PCL,INDEX
  if event.key == 'right':
    INDEX+=1
    if INDEX==numframes: INDEX=0
  elif event.key == 'left':
    INDEX-=1 
    if INDEX==-1: INDEX=numframes-1
  if event.key == 'up':
    INDEX+=10
    if INDEX>=numframes: INDEX=0
  elif event.key == 'down':
    INDEX-=10
    if INDEX<=-1: INDEX=numframes-1
  elif event.key == 'w':
    fname = 'FIGURE.' + str(INDEX) + '.png'
    print('saving figure:',fname); plt.savefig(fname)
    return
  elif event.key == 'q': exit()
  else: pass

  print(INDEX,np.amax(energy_all_modes(INDEX)),
        np.argmax(energy_all_modes(INDEX)))
  plt.clf()
  etitl=Etitle(INDEX)
  plt.title(etitl)
  plt.plot(energy_all_modes(INDEX))
  fig.canvas.draw_idle()


fig.canvas.mpl_connect('key_press_event',on_keyboard)
if (screen!=None):
  if screen == "off": pass
else: plt.show()
#plt.show()