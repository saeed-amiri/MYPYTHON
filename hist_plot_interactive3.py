#!/usr/bin/env python

'''
VERSION: 08.05.2019

PURPOSE: Display phonon ENERGY of transversal and longitudinal modes 
for MD trajectory as obtained from previously computed COLOR.RUNID.* files.

FEATURES:

* By pressing 'left' and 'right' keys you can cycle through the trajectory.

* If you press 'w' a PNG image of the current frame is written to file which 
you can show to your friends.

* If you click the mouse on a point inside the FBZ some info about that k-vector
is printed to the screen.

* Any other key terminates the program.

ARGS: RUNID

Note that in the color coding used, each subplot, for all times, has its signal 
normalized between 0 and 1. Hence, you can always see which modes are the most 
active, but you cannot compare colors between left and right panels in absolute
terms, nor between panels taken at different times.

OBVIOUSLY: In order for this to work, the COLOR files must be available, as
well as the KGRID file -> generated with the C-program 'phonon_k' (!)
'''

import os
import sys
import palettable
import numpy as np
import pandas as pd
import mytools  as MT
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties
from matplotlib.collections import PatchCollection
font = FontProperties()
font.set_style('italic')
#plt.rcParams.update({'font.size': 14})

if len(sys.argv)==1:
  print(__doc__); exit()

RUNID=sys.argv[1]
# read all phonon data 
kx,ky,kn,w1,w2,color,numpoints,numframes = MT.read_phonon_all(RUNID)

# set INDEX for starting point
if len(sys.argv) > 2:
  INDEX=int(sys.argv[2])
  if INDEX>=numframes : 
    INDEX%=numframes
    tmp='available frames: {}, frame sets to {}'.format(numframes,INDEX)
    print(tmp)
else: INDEX=0

# set Threshold for coloring in histogram
if len(sys.argv) > 3:
  Thold=int(sys.argv[3])
  if Thold>=numpoints : 
    Thold%=numpoints
    tmp='available points: {}, initiate at {}'.format(numpoints,Thold)
    print(tmp)
else: Thold=2

# chose the number of most energic k-points in a frame to write thier info
if len(sys.argv) > 4:
  Engpoints = int(sys.argv[4])
  if Engpoints>=numpoints :
    Engpoints=6
    tmp='available points: {}, write info for {}'.format(numpoints,Engpoints)
  elif Engpoints==0: Engpoints=6
else: Engpoints=6

vfile="SLOG."+RUNID
os.system("read_lammps_LOG.py LOG.{} 0 C_VEL[1] C_VEL[2] E_BOND KINENG C_KES".format(RUNID))

## reading the file containing velocity
df=pd.read_csv(vfile,delim_whitespace=True,header=None)
# convert to arrays
xxx=np.asarray(df[0],dtype=float)
vx=np.asarray(df[1],dtype=float)
vy=np.asarray(df[2],dtype=float)
ebonds=np.asarray(df[3],dtype=float)
kineng=np.asarray(df[5],dtype=float)
# convert xxx from steps into time units
xxx*=float(MT.get_param("PARAM","DT"))
xxx-=xxx[0]

# DT below is the time between array samples (not the MD timestep)
DT=xxx[1]

# compute NOT NORMALIZED phonon amplitudes -> dump in array 'PHAMP'
PHAMP=np.zeros((numframes,2,numpoints))
for i in range(numframes):
  # tmp is the i-th ROW of the 'color' dataframe
  tmp=np.asarray(color.iloc[i])
  # m loops over transvere (m=0) and longitudinal (m=1) modes
  for m in range(2):
    # take real and imaginary part, compute phonon energy 
    re=tmp[2*m::4]; im=tmp[2*m+1::4]
    if m==0: PHAMP[i][m]=(re**2+im**2)*w1
    else: PHAMP[i][m]=(re**2+im**2)*w2

# helper function to return NORMALIZED phonon amplitudes of frame=i and mode=m 
# as above: m=0 selects transverse modes; m=1 longitudinal modes
def PHAMP_N(i,m):
  tmp=PHAMP[i][m]
  return tmp

# width of FBZ hexagon; scale this to obtain the optimal symbol size to use in the plot such that symbols do not overlap
FBZ=4.0*np.pi/3.0; SS=FBZ/np.sqrt(numpoints)

# helper function to create hexagon polygon at position (x,y) and edge=e
def hexagon(x,y,e):
  p=[]
  for i in range(6):
    t=i*np.pi/3
    p.append([x+e*np.cos(t),y+e*np.sin(t)])
  return plt.Polygon(p)

def set_color(i):

  # choose your favorite colors: RdYlBu_r, jet, plasma, magma
  # gist_stern, gnuplot, cubehelix, PiYG,Greys  ...
  colors = palettable.cmocean.sequential.Amp_20.mpl_colormap(np.linspace(0, 1, 256))
  CMAP = mcolors.LinearSegmentedColormap.from_list('colormap', colors)
  # NEW: calculate some additional quantities of interest
  qq=[]
  pp=[]
  for m in range(2):
    # fraction to choose
    #p = int(0.05*numpoints)
    p=200
    # set the energy cutoff
    max = np.sort(PHAMP[i][m])[-p]
    # create the color array based on the cutoff
    clr=np.zeros(numpoints)
    for k in range(numpoints):
      if PHAMP[i][m][k]<max: clr[k]=0
      else: clr[k]=1
    # convert to array to color map, assign to hexagons
    clr=CMAP(clr)
    PCL[m].set_facecolor(clr)
    PCL[m].set_edgecolor(clr)

    qq.append( np.median(PHAMP[i][m]) )
    pp.append( np.sum(PHAMP[i][m]) )

  return qq,pp

# function to write "Engpoints" numbers of most active k-point in the frame INDEX
def write_info(INDEX):
  tmp = "F_{}".format(INDEX)
  if os.path.isdir(tmp)==True:
    rm = 'rm -rf {}'.format(tmp)
    os.system(rm)
  os.mkdir(tmp)


# Create a list of hexagons: PCL[0] = hexagon data list for transverse modes; PCL[1] = same for longitudinal modes
PCL=[]
for m in range(2):
  # create list of hexagon polygons
  pc=[hexagon(kx[i],ky[i],SS) for i in range(numpoints)]
  # convert to PatchCollection object
  pc=PatchCollection(pc)
  # append it to the list
  PCL.append(pc)

# make plot twice the default size in x-direction
fig = plt.figure(figsize=(1.6*6.4,2*4.8))

# define panels
l1 = fig.add_subplot(321)
r1 = fig.add_subplot(322)
tt = fig.add_subplot(313)

# set plot labels
tt.set_xlabel('time',size=15)
tt.set_ylabel(r"$v$",rotation='horizontal',ha='right' ,size=15)
tt.set_xlim(0,xxx[-1])
tt.plot(xxx,np.sqrt(vx*vx+vy*vy),'r')

def histogram(m):
  global l2, r2
  
  l2 = fig.add_subplot(323)
  r2 = fig.add_subplot(324)
  mid = int(numpoints/2)
  n_bins = 10
  tmp = np.sort(PHAMP[INDEX][m])
  off = tmp[0:mid]
  red = tmp[-6:]
  blu = tmp[mid:-6]
  data = [off, blu, red]
  colors = ['thistle', 'dimgrey', 'r']
  qq,_=set_color(INDEX)
  ax=l2 if m==0 else r2
  ax.axvline(qq[m],ls = "--",c='r')
  ax.grid(True, color='grey', linestyle='--')

  ax.hist(data, n_bins,alpha=1,log=True, color=colors)

  return ax.plot()

for m in range(2):
  histogram(m)

# INITIALIZE FIRST FRAME
set_color(INDEX)
# attach the hexagon patches to each subplot, set labels...
for m in range(2):
  ax=l1 if m==0 else r1
  bb=hexagon(0,0,FBZ)
  bb.set_fill(False)
  bb.set_edgecolor('gray')
  ax.add_patch(bb)
  ax.add_collection(PCL[m],autolim=True)
  ax.autoscale_view()
  ax.axis('equal')
  tmp=np.zeros(numpoints)
  plt.sca(ax)
  plt.title(INDEX)
  plt.axis('off')
  

# upon keypress, update the colors, or save image, or exit...
qq,pp=set_color(INDEX)
EB='E_phonon = {:.2}'.format(pp[0]+pp[1])
ttext = tt.text(numframes/2,vx[0]/2,EB, ha='center',size='large')
vline = tt.axvline(INDEX) 
def on_keyboard(event):
  global PCL,INDEX,r2,l2
  if event.key == 'right':
    INDEX+=1
    if INDEX==numframes: INDEX=0
  elif event.key == 'left':
    INDEX-=1
    if INDEX==-1: INDEX=numframes-1
  elif event.key == 'up':
    INDEX+=10
    if INDEX>=numframes: INDEX=10
  elif event.key == 'down':
    INDEX-=10
    if INDEX<=-1: INDEX=numframes-10
  elif event.key == 'pageup':
    INDEX+=100
    if INDEX>=numframes: INDEX=100
  elif event.key == 'pagedown':
    INDEX-=100
    if INDEX<=-1: INDEX=numframes-100
  elif event.key == 'home':
    INDEX=0
  elif event.key == 'w':
    fname = 'FIGURE.' + str(INDEX) + '.png'
    print('saving figure:',fname)
    plt.savefig(fname)
    return
  elif event.key == 'q':
    exit()
  else : pass
  # update colors for new value of INDEX
  qq, pp=set_color(INDEX)
  # update the plot titles; redraw things
  l2.remove()
  r2.remove()
  for m in range(2):
    histogram(m)
    ax=l1 if m==0 else r1
    plt.sca(ax) 
    s='TA' if m==0 else 'LA'
    tmp = '{}, F={}, MEDIAN={:.2E}, E_{}={:.2E}'.format(s,INDEX,qq[m],s,pp[m])
    vline.set_xdata(INDEX)
    EB='E_phonon = {:.3}, E = {:.3}'.format(pp[0]+pp[1],ebonds[INDEX]+kineng[INDEX] )
    ttext.set_text(EB)
    plt.title(tmp)
    plt.draw()
  
  

# upon mouse click, print some useful info about the k-vector
def onclick(event):
  # get (x,y) coordinate of mouse click
  x=event.xdata; y=event.ydata
  if x==None or y==None: return
  # find index of nearest k-vector whery you clicked
  dst=(kx-x)**2+(ky-y)**2; ind=np.argmin(dst)
  # print some information about the k-vector
  print()
  if kn[ind]>0.0:
    print('ind:',ind)
    print('KX:',kx[ind])
    print('KY:',ky[ind])
    print('WAVELENGTH:',2*np.pi/kn[ind])
    print('MODE FREQUENCIES:',w1[ind],w2[ind])
    print('MODE ENERGY:',PHAMP[INDEX][0][ind],PHAMP[INDEX][1][ind])
    print('AVERAGED ENERGY OVER ALL MODES: TA, LA:',PHAMP[INDEX][0].mean(),PHAMP[INDEX][1].mean())
  else: print('GAMMA POINT')
  if kn[ind]>0.0:
    filename=str(ind) + '.en'
    f = open(filename,'w')
    for i in range(numframes):
      f.write("{} {} {}\n".format(i, PHAMP[i][0][ind], PHAMP[i][1][ind]))
    f.close()
    print("file {}.en is saved".format({ind}))




# MAGIC LINES: enable interaction with keyboard and mouse
plt.gcf().canvas.mpl_connect('key_press_event',on_keyboard)
plt.gcf().canvas.mpl_connect('button_press_event',onclick)


plt.show()
