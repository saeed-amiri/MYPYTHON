#!/usr/bin/env python

'''
VERSION: 06.03.2019

PURPOSE: Display phonon amplitudes of transversal and longitudinal modes 
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

import sys
import numpy as np
from mytools import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib as mpl

def colorbar(mappable):
    ax = mappable.axes
    fig = ax.figure
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, ax=ax)
# MAIN PROGRAM STARTS HERE

if len(sys.argv)==1:
  print(__doc__); exit()

RUNID=sys.argv[1]
# read all phonon data
kx,ky,kn,w1,w2,color,numpoints,numframes = read_phonon_all(RUNID)

if len(sys.argv) > 2:
  INDSTART=int(sys.argv[2])
  if (INDSTART)>=numframes : 
    INDSTART%=numframes
    print("number of frames available: ",numframes)
else: INDSTART=0

# compute NOT NORMALIZED phonon amplitudes -> dump in array 'PHAMP'
PHAMP=np.zeros((numframes,2,numpoints))
for i in range(numframes):
  # tmp is the i-th ROW of the 'color' dataframe
  tmp=np.asarray(color.iloc[i])
  # m loops over transvere (m=0) and longitudinal (m=1) modes
  for m in range(2):
    # take real and imaginary part, compute absolute value
    re=tmp[2*m::4]; im=tmp[2*m+1::4]
    PHAMP[i][m]=(re**2+im**2)
    if m==1:
      PHAMP[i][m]*=w1
    else: PHAMP[i][m]*=w2 

# helper function to return NORMALIZED phonon amplitudes of frame=i and mode=m 
# as above: m=0 selects transverse modes; m=1 longitudinal modes
#def PHAMP_N(i,m):
#  tmp=PHAMP[i][m]
#  #return tmp/1.0 # to remove normalizaion
#  return tmp/tmp.max()
thold=1280
def PHAMP_N(i,m):
  tmp=PHAMP[i][m]
  return sorted(tmp)[-thold:] 

# helper function to return index of selected phonons of "PHAMP_N(i,m)" 
def PHAMP_ind(i,m):
  tmp=PHAMP[i][m]
  return np.argsort(tmp)[-thold:] 

# width of FBZ hexagon; scale this to obtain the optimal symbol size to use
# in the plot such that symbols do not overlap
FBZ=4.0*np.pi/3.0; SS=FBZ/np.sqrt(numpoints)

# helper function to create hexagon polygon at position (x,y) and edge=e
def hexagon(x,y,e):
  p=[]
  for i in range(6):
    t=i*np.pi/3
    p.append([x+e*np.cos(t),y+e*np.sin(t)])
  return plt.Polygon(p)


# create two panel plot; try to give it a reasonable size
nrows=1; ncols=2
fig,axs=plt.subplots(nrows,ncols)
fig.set_figwidth( ncols*plt.rcParams.get('figure.figsize')[0])
#fig.set_figheight( nrows*plt.rcParams.get('figure.figsize')[1])


# helper function to set the hexagon colors for each mode for frame=i
PCL=[]
def set_color(index):
  # choose your favorite colors: RdYlBu_r, jet, plasma, magma ...
  PCL.clear()
  CMAP=cm.get_cmap('RdYlBu_r')
  for m in range(2):
    active_point=PHAMP_ind(index,m)
    pc=[hexagon(kx[i],ky[i],SS) for i in active_point]
    pc=PatchCollection(pc)
    PCL.append(pc)
#    PCW.append(pc)
  for m in range(2):
    # for the coloring, the normalized phonon amplitudes are used
    clr=CMAP(PHAMP_N(i,m))
    PCL[m].set_facecolor(clr)
    PCL[m].set_edgecolor(clr)
 #   clw=CMAW(1)
 #   PCW[m].set_facecolor(clw)
 #   PCW[m].set_edgecolor(clw)
 #   PCW[m].set_linewidths(0)


# INITIALIZE FIRST FRAME
INDEX=np.abs(INDSTART) ; set_color(INDEX)


# attach the hexagon patches to each subplot, set labels...
for m,ax in enumerate(fig.axes):
  bb=hexagon(0,0,FBZ)
  bb.set_fill(False)
  bb.set_edgecolor('gray')
  ax.add_patch(bb)
  ax.add_collection(PCL[m],autolim=True)
  ax.autoscale_view()
  ax.axis('equal')
  s='Transverse modes' if m==0 else 'Longitudinal modes'
  ax.text(0,-4.5,s,horizontalalignment='center',fontsize=16,color='grey')
  plt.sca(ax)
  #colorbar(ax)
  plt.title(INDEX)
  plt.axis('off')

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
    plt.savefig(fname,bbox_inches='tight')
    return
  elif event.key == 'q':
    exit()
  else : pass
  # update colors for new value of INDEX
  for m,ax in enumerate(fig.axes):
    ax.remove()
  nrows=1; ncols=2
  fig,axs=plt.subplots(nrows,ncols)
  fig.set_figwidth( ncols*plt.rcParams.get('figure.figsize')[0])
  set_color(INDEX)
  # update the plot titles; redraw things
  for m,ax in enumerate(fig.axes):
    ax.add_collection(PCL[m],autolim=True)
    plt.sca(ax) 
    plt.title(INDEX)
    plt.draw()

# upon mouse click, print some useful info about the k-vector
def onclick(event):
  # get (x,y) coordinate of mouse click
  x=event.xdata; y=event.ydata
  if x==None or y==None: return
  # find index of nearest k-vector where you clicked
  dst=(kx-x)**2+(ky-y)**2; ind=np.argmin(dst)
  print()
  if kn[ind]>0.0:
    te="K-POINT: " + str(ind) + ", FRAME: " + str(INDEX)
    print(te)
    print('KX:',kx[ind])
    print('KY:',ky[ind])
    print('WAVELAMPTH:',2*np.pi/kn[ind])
    print('MODE FREQUENCIES:',w1[ind],w2[ind])
    print('MODE AMPLITUDES, NOT NORMALIZED:',PHAMP[INDEX][0][ind],PHAMP[INDEX][1][ind])
    print('MODE Energy, NOT NORMALIZED:',PHAMP[INDEX][0][ind]*w1[ind],PHAMP[INDEX][1][ind]*w2[ind])
  else: print('GAMMA POINT')


# MAGIC LINES: enable interaction with keyboard and mouse
plt.gcf().canvas.mpl_connect('key_press_event',on_keyboard)
plt.gcf().canvas.mpl_connect('button_press_event',onclick)
#plt.tight_layout(h_pad=1)
plt.show()
