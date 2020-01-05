#!/usr/bin/env python
import os
import csv
import glob
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from color_print import *
matplotlib.rcParams.update({'figure.max_open_warning': 0})

#! getting the name of the Data directories
dirs=[]
for x in os.listdir(os.getcwd()):
        if os.path.isdir(x):
            x_pwd = './' + str(x) + '/PARAM.base'
            if os.path.isfile(x_pwd):
                dirs.append(x)
print_blue("directorys to compare: {}".format(dirs))

#! getting the number of timesteps from PARAM.base
def get_PARAM():
    searchfile = open( "PARAM.base", "r" )
    for line in searchfile:
        if "NEVERY" in line: 
            NEVERY = line.split( "=" ); NEVERY = int( NEVERY[1] )
        elif "NRUN" in line:
            NRUN = line.split( "=" ); NRUN = int( NRUN[1] )
        elif "ANGEL" in line:
            ANGEL = line.split( "=" ); #ANGEL = int( ANGEL[1] )
        elif "XX" in line:
            XX = line.split( "=" ); XX = int( XX[1] ) 
            XX *= XX * 2 * np.sqrt( 3 ) * 1.0046; Nparticles = np.round( XX )
    searchfile.close(  )
    ntraj = int( NRUN / NEVERY ) + 1 
    return ntraj, ANGEL[1], int( Nparticles )

#! reading the files
def read( file_name ):
    df=pd.read_csv( file_name,delim_whitespace=True,header=None )
    t  = np.asarray( (df[0]-df[0][0])*0.001, dtype=float )
    ux = np.asarray( df[1], dtype=float )
    uy = np.asarray( df[2], dtype=float )
    return t, ux, uy

#! Python code to convert tuple into string 
def convertTuple(tup): 
    str =  ''.join(tup) 
    return str

#! cheking the excistens of a Directory
def check_dir( dirName):
    try:
        os.makedirs( dirName )    
        outex = "Directory '" , dirName ,  "' Created "
        outex = convertTuple( outex )
        print_green( outex )
    except FileExistsError:
        shutil.rmtree( dirName )
        os.makedirs( dirName )    
        outex = "old Directory '" , dirName ,  "' deleted and a new Created "
        outex = convertTuple( outex )
        print_violet( outex )

#! writting v-t for diffrent seeds
def write_out( v_array, kick):
    if kick == 0.1 : check_dir( 'compare_data' )
    out_name = './compare_data/V_' + str(kick)
    np.savetxt(out_name, v_array, delimiter='\t')

#! plotting v-t for diffrent seeds
def plot_compare( v_array, kick ):
    if kick == 0.1 : check_dir( 'compare_plot' )
    numcols = len(v_array[0])
    fig = plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax.set_title(kick)
    ax.set_xlabel("time")
    ax.set_ylabel(r"$v_{cm}$")
    j = 1
    nn = int( nfiles * 2 + 1 )
    for i in range(1, 11, 2):
        speed = v_array[i]*v_array[i] + v_array[i+1]*v_array[i+1]
        speed = np.sqrt(speed)
        ax.plot (v_array[0], speed, label=j)
        j += 1
    ax.legend()
    figname = './compare_plot/tcom_' + str(kick) + '.png'
    #plt.show()
    fig.savefig(figname,bbox_inches='tight')


#! plotting average v-t for diffrent seeds
def plot_ave(v_array, kick, n_cut):
    if kick == 0.1 : check_dir( 'ave_plot' )
    numcols = len(v_array[0])
    avefig = plt.figure()
    aveax=avefig.add_subplot(1,1,1)
    aveax.set_title('averaged {} seeds,`kick` = {}, np ~ {}'
                    .format(nfiles, kick, XX))
    aveax.set_xlabel("time")
    aveax.set_ylabel(r"$v_{cm}$")
    j = 1
    ave_speed = np.zeros(n_cut)
    nn = int( nfiles * 2 + 1 )
    for i in range(1, 11, 2):
        speed = v_array[i]*v_array[i] + v_array[i+1]*v_array[i+1]
        speed = np.sqrt(speed)
        ave_speed += speed
        aveax.plot (v_array[0], speed, ls=':', lw = 0.5)
    aveax.plot(v_array[0], ave_speed/nfiles)
    figname = './ave_plot/ave_' + str(kick) + '.png'
    avefig.savefig( figname, bbox_inches='tight' )

def std_err( v_array, kick ):
    if kick == 0.1 : check_dir( 'err_plot' )
    errfig = plt.figure()
    errax=errfig.add_subplot(1,1,1)
    errax.set_title('averaged {} seeds,`kick` = {}, np ~ {}'
                    .format(nfiles, kick, XX))
    errax.set_xlabel("time")
    errax.set_ylabel(r"$v_{cm}$")
    j = 0
    speed = np.zeros( (nfiles, nrows) )
    nn = int( nfiles * 2 + 1 )
    for i in range(1, 11, 2):
        speed[j] = np.sqrt( v_array[i]*v_array[i] + v_array[i+1]*v_array[i+1] )
        j += 1
    err = np.std( speed, axis=0 )
    plt.errorbar(v_array[0,:50], speed[1,:50], yerr=err[:50],
                    ecolor='r',capsize=2,  )
    figname = './err_plot/err_' + str(kick) + '.png'
    errfig.savefig ( figname, bbox_inches = 'tight' )

#! making the arrays
SFILE = "SLOG.0"
nfiles = int( len(dirs) ) 
ncolumns = nfiles * 2 + 1
nrows, ANGEL, XX = get_PARAM()
for k in np.arange( 0.1, 2.1, 0.1 ):
    vel = np.zeros( (ncolumns, nrows) )
    i = 0
    for p in dirs:
        k = round( k, 2 )
        k_loc = "./" + p + "/" + str( k ) + '/' + SFILE
        t, vx, vy = read( k_loc )
        if i == 0 :  vel[0] = t
        vel[i + 1] = vx
        vel[i + 2] = vy
        i += 2
    write_out( vel.transpose(), k )    
    plot_compare( vel, k )
    n_cut = 50
    plot_ave( vel[:,0:n_cut], k, n_cut )
    std_err( vel, k )
