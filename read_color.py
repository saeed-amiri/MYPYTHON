#!/usr/bin/env python
'''
saeed
VERSION: 0-18.06.2019
read the color files and return the values 
for using in c code
'''
import pandas as pd,mytools as MT,sys,gzip
from itertools import zip_longest, count
import numpy as np,glob,gzip
import multiprocessing as mp
from color_print import *
from time import time
import concurrent.futures
with concurrent.futures.ProcessPoolExecutor() as executor:
    
print("Number of processors: ", mp.cpu_count())

