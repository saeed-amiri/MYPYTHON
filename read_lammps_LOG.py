#!/usr/bin/env python

'''
VERSION [RV]: 02.03.2019
VERSION [SD]: 16.01.2020 (argparse)

PURPOSE: scan LAMMPS logfile for 'thermo' output lines, compute time average
of selected quantities, and write the corresponding time series to file. It is
assumed that 'step' is part of the thermo output!

USAGE: -log LOGFILE -equal EQUIL [-file OUTFILE] -keys KEY1 KEY2 ...
EG: -l LOG.0 -e 20000 [-f ELOG.0] -k TEMP LX

Output lines for steps<EQUIL are ignored!. Obviously, you can only provide KEYS 
for quantities that are actually in the logfile. Note that keys must be 
written in CAPITAL letters.

OUTPUT: The averaged output and the time series are named as the LOGFILE,
with 'A' and 'S' prepended [or user chose for 'S'], respectively. 
The format of the time series is as columns:

step KEY1 KEY2 ...

You should _NOT_ specify 'STEP' as one of the keys, as this will throw an error! In 
case the logfile contains thermo output of several runs, only the output of the 
last 'run' instance is used! 
'''

import sys
import argparse
import pandas as pd
from pathlib import Path
from mytools import *
from color_print import *
my_parser = argparse.ArgumentParser(prog="read_lamms_LOG.py",
            usage="%(prog)s -log <LOG.RUNID> -equal <EQUIL> [-file <OUTFILE>] -keys <...>] ",
            description='reading logfile (LOG.RUNID)',
            epilog="need LOG.RUNID",
            prefix_chars="-")

# Execute the parse_args() method
my_parser = argparse.ArgumentParser()
my_parser.add_argument('-log', action='store', type=str, dest="LOGFILE",
  required=True,help="the LOG.RUNID file")
my_parser.add_argument('-equil', action='store', type=str, dest="EQUIL",
  required=True,help="output lines for steps<EQUIL are ignored!")
my_parser.add_argument('-file', action='store', dest="outfile", type=str,
  required=False,help="output file for time series, an 'A' will be add for AVERAGE file")
my_parser.add_argument('-keys', action='store', dest="KEY", type=str, nargs='*',
  required=True,help="KEYS to read from logfile, must be in capital")

args = my_parser.parse_args()
LOGFILE=args.LOGFILE
EQUIL=args.EQUIL
outfile=args.outfile
KEY=args.KEY

# check if the single string 'word' can be converted to float
def isfloat(word):
  try:
    float(word)
    return True
  except ValueError:
    return False

# check if all the single string elements in the list 'wordlist' can be converted to floats
def isfloat_list(wordlist):
  # BEWARE: watch out for empty list (!)
  if len(wordlist)==0: return False
  for w in wordlist:
    if isfloat(w)==False:
      return False
  return True

# convert all elements of list 'wordlist' to UPPER case letters
def to_upper(wordlist):
  return [w.upper() for w in wordlist]

# READ LAMMPS LOGFILE -> return thermo output of last run instance as dataframe
def read_logfile(logfile,equil):
  # read entire logfile
  data = Path(logfile).read_text().splitlines();
  # scan data in REVERSE order until string 'Loop time of' is found
  #  -> assume this marks the end of the thermo output of the last run 
  # instance
  # OR: for incomplete logfiles -> scan until a line with only numbers is
  # found (!)
  for i in range(len(data)-1,0,-1):
    if data[i].startswith('Loop time of'):
      end=i; break
    if isfloat_list( data[i].split() ):
      end=i-1; break
  # continue reverse scan starting from 'end' until you find a line that
  # contains only letters; assume this line is the header line
  for i in range(end-1,0,-1):
    f=data[i].split()
    if isfloat_list(f)==False:
      header=to_upper(f); start=i; break
  # thermo field 'step' is required (!)
  if 'STEP' not in header: printerror('no field step in thermo output')
  # now grab the data; dump in dataframe
  df = [data[i].split() for i in range(start+1,end,1)]
  df = pd.DataFrame(df,columns=header,dtype=float)
  # make 'step' the index
  df = df.set_index('STEP')
  # only keep data beyond equilibration
  df = df[df.index >= int(equil)]
  # RETURN IT (!)
  print_green("availabels KEYS in thermo:")
  print(header)
  return df,header


# read logfile
LOGDATA,header=read_logfile(LOGFILE,EQUIL)

# thermo_style keywords that the user wants (CAPITAL LETTERS; 
# if you request a keyword that is not in the thermo output, 
# an error is generated)

if KEY[0]=='ALL': 
  KEY=list(header)
  KEY.remove('STEP')

for k in range(len(KEY)):
  if KEY[k] not in header: printerror('requested key "{}" not in thermo output'.
                                        format(KEY[k]))
print_blue("requested KEYS:")
print(KEY)
# print time averages and standard deviations: 
# output file is name of logfile with 'A' prepended
sys.stdout=open('A'+outfile,'w') if (outfile!=None) else open('A'+LOGFILE,'w')

for k in range(len(KEY)):
  print(1+header.index(KEY[k]),KEY[k],LOGDATA[KEY[k]].mean(),LOGDATA[KEY[k]].std(),sep='\t')

# TIME SERIES: output file is name of logfile with 'S' prepended
sys.stdout = open(outfile,'w') if (outfile!=None) else open('S'+LOGFILE,'w')

LOGDATA.to_csv(sys.stdout,columns=KEY,index=True,header=KEY,
               sep='\t',float_format='%.10e')
sys.stdout = sys.__stdout__
