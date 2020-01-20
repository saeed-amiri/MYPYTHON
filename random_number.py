#!/usr/bin/env python3
'''
13.01.2020 version 1.0
producing N random numbers with D digits:
 and append them  
 start = 10^D, 
 end = 10^(D+1)-1
 num = N 
'''
import argparse
import numpy as np
import random
import sys,os,shutil

my_parser = argparse.ArgumentParser(prog="random.py",
            usage="%(prog)s -n <N>  -d <D> [-f <outfile>] ",
            description='producing N random numbers with D digits',
            epilog="-n <int> -d <int> should assign",
            prefix_chars="-")

# Execute the parse_args() method
my_parser.add_argument('-n', action='store', dest="N", type=int, required=True,
                      help="numbers of random number")
my_parser.add_argument('-d', action='store', dest="D", type=int, required=True,
                      help="numbers of digits")                      
my_parser.add_argument('-f', action='store', dest="file", type=str, required=False,
                      help="outfile to write to [optional]")                      

args = my_parser.parse_args()
 
N=int(args.N)
D=int(args.D)
outfile=args.file


# Function to generate 
start=int(pow(10,D-1))
end=int(pow(10,(D)))-1
num = N
print("random integer between {} and {}".format(start,end))
#https://stackoverflow.com/questions/31742326/efficient-way-of-reading-integers-from-file
def read_dirs(list_dir):
    m = len(list_dir)
    list_dir = list(dict.fromkeys(list_dir))
    n = len(list_dir)
    if (m!=n): print("'{}' in saved', {}' duplicate(s) ignored"
                    .format(n,m-n))
    else: print("'{}'random numbers saved".format(n))
    return list_dir

def checkDuplication(ListElem):
    for elem in ListElem:
        if ListElem.count(elem)>2:
            return True
    return False

res = np.zeros(num)
#res=np.chararray(num)

def Rand(start, end, num): 
    for j in range(num): 
        res[j] = (random.randint(start, end))
    return res 

if (outfile!=None):
    res=Rand(start, end, num)
    res=read_dirs(res)
    np.savetxt(outfile,[res],fmt='%d',newline=" ")
else : print(Rand(start, end, num))
