#!/usr/bin/env python

'''
VERSION: 12.08.2019
MYVECTORS.py <RUNID> <POLARIZATION> <C_ID> <N_FILTERD> <TIME_STEP(OPT)>
'''

import os
import sys
import numpy as np
import pandas as pd
import mytools  as MT
from color_print import *
import pathlib

print_green(__doc__)


if len(sys.argv)==1:
    print(__doc__); exit()

RUNID=sys.argv[1]

kgrid="KGRID."+str(RUNID)
kfile = pathlib.Path(kgrid)
if kfile.exists ():
    print_blue("KGRID exist")
else:
    print_yellow("KGRID not exist")


# read all phonon data 
kx,ky,kn,w1,w2,color,numpoints,numframes = MT.read_phonon_all(RUNID)

# checking the LONGITIUDIAL or TRANSVERS 
if len(sys.argv) > 2:
  if int(sys.argv[2]) in [1, 2]:
    Polarization = int(sys.argv[2])
  else:
    print_red(__doc__)
    print_yellow("\n ERROR, only 1 (LONGITUDINAL) or 2 (TRANSVERS) for sys.argv[2]\n")

if len(sys.argv) > 3:
    if int(sys.argv[3]) in [1, 2, 3]:
        C_ID = int(sys.argv[3])
        tmp = "C_ID is:{}".format(C_ID)
        print_blue(tmp)
    else: 
        C_ID = Polarization
        print_green("\nC_ID will be same as sys.argv[2]\n")

# checking the NUMBER of MAXs (optional, default is 6)
tmp='\navailable points: {}, write info for {} (sys.argv[3])\n'.format(numpoints,6)
if len(sys.argv) > 4:
    MaxPoints = int(sys.argv[4])
    if MaxPoints>numpoints :
      MaxPoints=6
      print_green(tmp)
    elif MaxPoints==0: MaxPoints=6; print_green(tmp)
else: MaxPoints=6; print_green(tmp)
tmp='writing infos for {} k points ...\n'.format(MaxPoints)
print_blue(tmp)

# checking the TIME (optional, default is: 0)
if len(sys.argv) > 5:
    TIME = int(sys.argv[5]) if int(sys.argv[5])<=numframes else 0
else: TIME=0



# compute NOT NORMALIZED phonon ENERGY -> dump in array 'PHENG'
PHENG=np.zeros((numframes,2,numpoints))
for i in range(numframes):
  # tmp is the i-th ROW of the 'color' dataframe
  tmp=np.asarray(color.iloc[TIME])
  # m loops over transvere (m=0) and longitudinal (m=1) modes
  for m in range(2):
    # take real and imaginary part, compute phonon energy 
    re=tmp[2*m::4]; im=tmp[2*m+1::4]
    if m==0: PHENG[TIME][m]=(re**2+im**2)*w1
    else: PHENG[TIME][m]=(re**2+im**2)*w2


def FILTER(max,t,m):
    list = np.argsort(PHENG[t][m])
    return( np.flip(list[-max:]))


def WRITE_VEC(TIME):
    MaxList=FILTER(MaxPoints,TIME,Polarization)
    fvec="MYVECTORS."+str(TIME)
    MYVEC = open(fvec,"w")
    for i in MaxList:
        k_info = str(kx[i])+" "+str(ky[i])+" "+str(C_ID)+"\n"
        MYVEC.write(k_info)
    MYVEC.close()
    flog="MYVECTORS_log."+str(TIME)
    MYLOG = open(flog,"w")
    MYLOG.write("#i      kx[i]   ky[i]     k     ENG_L[i]    ENG_T[i]  C_ID\n")
    for i in MaxList:
        k_v = np.sqrt(kx[i]*kx[i] + ky[i]*ky[i])
        k_ind = str("{:5d}  ".format(i)) 
        kx_i  = str("{:+.3f}  ".format(kx[i]))
        ky_i  = str("{:+.3f}  ".format(ky[i]))
        kv_i   = str("{:+.3f}  ".format(k_v))
        ENG_L = str("{:+.3e}  ".format(PHENG[TIME][0][i]))
        ENG_T = str("{:+.3e}  ".format(PHENG[TIME][1][i]))
        CID   = str("{:d}\n".format(C_ID)) 

        k_info = k_ind + kx_i + ky_i + kv_i + ENG_L + ENG_T + CID
        MYLOG.write(k_info)
    MYLOG.close()


WRITE_VEC(TIME)
print("\nDONE\n")