#!/usr/bin/env python3

'''
Get average of all the simulation from "job.out".
'''

import os
import sys
import os.path
import time
import numpy as np
import pandas as pd
from pathlib import Path
import concurrent.futures

#    if os.path.exists('job.out') :
#     # fname = 'job.out'
#   elif os.path.exists('LOG.0'):
#    fname = 'LOG.0'
#   else:
#    print("read which:")
#    os.system("echo $(ls -1v LOG.* )")
#    fname = input()
#   print("reading: ",fname)
#
start = time.perf_counter()


def get_chunks(fname):
    job = open(fname, "r")
    joblines = job.readlines()
    RUN: int = 0
    LIENER: int = 0
    LOOP: bool = False
    WALL: bool = False
    start = []
    end = []
    for line in reversed(joblines):
        LIENER += 1
        if line.startswith('Total wall time'):
            RUN += 1
            WALL = True
        if line.startswith('Loop time of') and WALL:
            end.append(LIENER+1)
            LOOP = True
            WALL = False
        if line.startswith('Step') and LOOP:
            start.append(LIENER)
            if RUN == 1:
                head = line.split()
            LOOP = False
    job.close()
    print(f"---> {fname} contains {RUN} simulation(s)\n header:\n {head}")
    return end, start, head, RUN, LIENER


def make_df(fname):
    # fname=os.path.join(src,'LOG.300')
    end, start, head, RUN, line = get_chunks(fname)
    start = [line-start[i]+1 for i in range(len(start))]
    end = [line-end[i]+1 for i in range(len(end))]
    start.reverse()
    end.reverse()
    for i in range(RUN):
        data = Path(fname).read_text().splitlines()[start[i]:end[i]]
        df = [data[i].split() for i in range(len(data))]
        df = np.asarray(df, dtype=float)
        if i == 0:
            index = df[:, 0]
        df = np.delete(df, 0, 1)
        if i == 0:
            dfsum = df
        else:
            dfsum += df
    header = head[1:]
    index = np.asarray(index, dtype=int)
    df = pd.DataFrame(dfsum/RUN, index=index, columns=header)

    df.index.rename(head[0], inplace=True)
    job_out = os.path.join('.', 'job_average')
    df.to_csv(job_out, sep='\t')


dirs = sys.argv[1:]
# print(dirs)
# dirs = [d for d in dirs if os.path.exists(os.path.join(d,'LOG.300'))]
print(dirs)
with concurrent.futures.ThreadPoolExecutor() as executor:
    j = executor.map(make_df, dirs)

finish = time.perf_counter()

print(f'\nTotal time: {finish-start} seconds\n')
