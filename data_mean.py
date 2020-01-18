#!/usr/bin/env python3

'''
VERSION: 17.01.2020
geting mean of ELOG.0
'''
import csv
import argparse
import numpy as np
import pandas as pd
import sys,os,glob,gzip,shutil
from pathlib import Path

my_parser = argparse.ArgumentParser(prog="mk_plots.py",
            usage="%(prog)s -id <RUNID> [ -k <kick> -w <MODETOWRITE> -p <MODEPLOT>] ",
            description='plot MODES properties',
            epilog="need COLOR.RUNID.gz, MODEINFO",
            prefix_chars="-")

# Execute the parse_args() method
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-sourcefile', action='store', dest="source",type=str,
                       required=True, help="name of the file contain the data; should be same in all the directories")
my_parser.add_argument('-ran', action='store', dest="ran",type=str,
                       required=True, help="the file contain the seed numbers")
my_parser.add_argument('-kick', action='store', dest="kick", type=str,
                       required=True, help="the file contain the kick")

args = my_parser.parse_args()

source = args.source
ran = args.ran
kick = args.kick

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

def get_header(filename):
  with open(filename) as f:
    for rows, l in enumerate(f):
      pass
  data = pd.read_csv(filename,delim_whitespace=True)  
  heads=[]
  for col in data.columns: 
      heads.append(col)
  return heads,len(heads),rows

def read_lamE(file_name):
  heads,col,row=get_header(file_name)
  data = np.zeros((Ccol,Crows))
  df = pd.read_csv(file_name,delim_whitespace=True, skiprows=1,header=None) 
  for i in range(col):
      data[i]=(np.asarray(df[i]))
  return data

def write_out(data,k,Cheads):
  out=source+'_'+k
  np.savetxt(out,data.transpose(),fmt='%.18e',header=Cheads,delimiter=' ',)

#-> reading the file which contains the names of directories
ran_dirs=read_dirs(ran)
kick_dirs=read_dirs(kick)
#-> convert RAN to integer
for i in range(len(ran_dirs)): ran_dirs[i]=int(ran_dirs[i])
for i in range(len(ran_dirs)): ran_dirs[i]=str(ran_dirs[i])
for i in range(len(kick_dirs)): kick_dirs[i]=str(kick_dirs[i])

j=0
for k in (kick_dirs): 

  if (j==0): 
    controlFile= ran_dirs[0]+'/'+k+'/'+source
    print("Control file: '{}'".format(controlFile))
    Cheads,Ccol,Crows=get_header(controlFile)
    print("header, #Columns, #Rows: {}, {}, {}".format(Cheads,Ccol,Crows))
    j=1
    HEADS=[]
    for i in Cheads:
      HEADS.append(i.split('\t')[0])
  
  data = np.zeros((Ccol,Crows))
  for r in (ran_dirs):
    data_path = './'+r+'/'+k+'/'+source
    if (os.path.exists(data_path)): pass
    else: print("'{}' not ex".format(data_path))
    n,m,o=get_header(data_path)
    if (n!=Cheads or m!=Ccol or o!=Crows):
      print ("Wrong '{}'".format(data_path))
      pass
    result=read_lamE(data_path)    
    for i in range(Ccol):
      data[i]+=result[i]
  for i in range(Ccol):
    data[i]=data[i]/len(ran_dirs)
  
  write_out(data,k,HEADS)  
