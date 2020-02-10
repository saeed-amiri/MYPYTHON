#!/usr/bin/env python

'''
VERSION: 10.02.2020

find the average Temperature 

'''

import sys,os,glob,gzip
import pandas as pd
import argparse
import numpy as np
#import matplotlib
#import matplotlib as mpl
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
                       required=True, help="the file contain the kicks")
my_parser.add_argument('-nfiles', action='store', dest="nfiles", type=int,
                       required=False, help="number of files to read") 
my_parser.add_argument('-title', action='store', dest="toptitle", type=str,
                       required=True, help="requested title", nargs='*')                                          
args = my_parser.parse_args()

ran = args.ran
kick = args.kick
nfiles= args.nfiles
toptitle = args.toptitle

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
		if (m!=n): print("'{}' dirs in '{}'', {}' duplicate(s) ignored"
		                .format(n,filename,m-n))
		else: print("'{}' dirs in '{}'".format(n,filename))
		return list_dir

#-> reading the file which contains the names of directories
ran_dirs=read_dirs(ran)
kick_dirs=read_dirs(kick)
#-> convert RAN to integer
for i in range(len(ran_dirs)): ran_dirs[i]=int(ran_dirs[i])
for i in range(len(ran_dirs)): ran_dirs[i]=str(ran_dirs[i])
for i in range(len(kick_dirs)): kick_dirs[i]=str(kick_dirs[i])

def read_lamE(file_name):
	result=dict()    
	heads,n=get_Sheader(file_name)
	df = pd.read_csv(file_name,delim_whitespace=True, skiprows=1,header=None) 
	for i in range(n):
		result[i]=np.asarray(df[i])
	return result

def get_Sheader(filename):
	data = pd.read_csv(filename,delim_whitespace=True)  
	heads=[]
	for col in data.columns: 
		heads.append(col)
	return heads,len(heads)

if (nfiles!=None):
    if (nfiles <= len(ran_dirs) and nfiles > 0) : ndirs=nfiles
else : ndirs =len(ran_dirs)
print("reading {} files ".format(ndirs))

TEMP = np.zeros(ndirs)
def get_ave(k):
	n = 0
	for r in (ran_dirs)[:ndirs]:
		slog_path = './'+r+'/'+k+'/'+"SLOG.0"
		if (os.path.exists(slog_path)): pass
		else: 
			print("'{}' not exist".format(slog_path))
			continue
		Sheads, nE = get_Sheader(slog_path)
		if (Sheads[1]=='C_TEMP'): 
			SLog = read_lamE(slog_path)
			tmp = np.average(SLog[1])
			TEMP[n]=tmp
			n+=1
		else:
			print("PROBLEM IN SELECTING COLUMN IN {}".format(slog_path))
			continue
			
	print('NUMBER OF SLOG FILES FOR kick = {} is {}'.format(k,n))
	return TEMP, n

AVE=np.zeros(len(kick_dirs))
MIN=np.zeros(len(kick_dirs))
MAX=np.zeros(len(kick_dirs))
i=0
with open("ave_temp","w") as f:
	f.write("#kick\tave_temp\tmin\t\tmax\n")
	for k in (kick_dirs):
		tmp,n=get_ave(k)
		AVE[i]=np.average(tmp)
		MIN[i]=np.amin(tmp)
		MAX[i]=np.amax(tmp)
		f.write("{}\t\t{:.5f}\t\t{:.5f}\t{:.5f}\n".format(k,AVE[i],MIN[i],MAX[i]))
		i+=1
	
print(AVE)
plt.plot(kick_dirs, AVE,"bo--")
#plt.plot(kick_dirs, MIN,"--",lw=0.5)
#plt.plot(kick_dirs, MAX,":",lw=0.5)
plt.ylabel("Temperature")
plt.xlabel("kick")
plt.title("{}, nsys={}".format(toptitle,n))
plt.savefig("ave_temp.png",bbox='tight')
plt.show()
