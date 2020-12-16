#!/usr/bin/env python3

''' 
Get average of all the simulation from "job.out". 
'''

import os.path,os 
import numpy as np
import pandas as pd
from pathlib import Path

if os.path.exists('job.out') :
  fname = 'job.out'
elif os.path.exists('LOG.0'):
  fname = 'LOG.0'
else:
  print("read which:")
  os.system("echo $(ls -1v LOG.* )")
  fname = input()
print("reading: ",fname)

def get_chunks():

  job = open(fname,"r") 
  joblines =job.readlines()
  RUN  = 0; LINER = 0
  LOOP = 0; WALL  = 0
  start=[];end=[]
  for line in reversed(joblines):
    LINER+=1
    if line.startswith('Total wall time'):
      RUN+=1; WALL = 1
    if (line.startswith('Loop time of') and WALL==1):
      end.append(LINER+1)
      LOOP = 1; WALL = 0
    if (line.startswith('Step') and LOOP==1):
      start.append(LINER)
      if RUN==1: 
        head=line.split()
      LOOP = 0
  job.close()
  print("{} contains {} simulation(s)".format(fname, RUN))
  print("header:")
  print(head)
  
  return end, start, head, RUN, LINER

end,start,head,RUN,l = get_chunks()
start = [l-start[i]+1 for i in range(len(start))]
end = [l-end[i]+1 for i in range(len(end))]
start.reverse();end.reverse()
for i in range(RUN):
  data = Path(fname).read_text().splitlines()[start[i]:end[i]]
  df = [data[i].split() for i in range(len(data))]
  df=np.asarray(df,dtype=float)
  if i==0: index = df[:,0]
  df=np.delete(df,0,1)
  if i == 0: dfsum = df
  else: dfsum+=df
header = head[1:]
index = np.asarray(index,dtype=int)
df = pd.DataFrame(dfsum/RUN,index=index,columns=header)

df.index.rename(head[0],inplace=True)

df.to_csv('job_average',sep='\t')