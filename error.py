#!/usr/env/bin python3
'''
checking job.err for errors:

Traceback (most recent call last):
  File "../color_inline_november9.py", line 161, in <module>
    update_average('gt_ke.gz',cur.ke)
  File "../color_inline_november9.py", line 146, in update_average
    gt.attrs['ns'] = n
  File "/usr/product/applsw/conda/2019.03/lib/python3.7/site-packages/pandas/core/generic.py", line 5067, in __getattr__
    return object.__getattribute__(self, name)
AttributeError: 'DataFrame' object has no attribute 'attrs'

srun: error: dmp024: task 0: Segmentation fault
/var/spool/slurm/d/job5947725/slurm_script: line 17: ../phonon_nov9: No such file or directory
Traceback (most recent call last):
  File "../color_inline_november9.py", line 158, in <module>
    cur = READCOLOR(sys.argv[1])
  File "../color_inline_november9.py", line 63, in __init__
    with gzip.open(fname,'r') as f: fl=f.readline().split()
  File "/opt/rh/rh-python36/root/usr/lib64/python3.6/gzip.py", line 53, in open
    binary_file = GzipFile(filename, gz_mode, compresslevel)
  File "/opt/rh/rh-python36/root/usr/lib64/python3.6/gzip.py", line 163, in __init__
    fileobj = self.myfileobj = builtins.open(filename, mode or 'rb')
FileNotFoundError: [Errno 2] No such file or directory: 'color.0.gz'
#######################################################################################
SyntaxError: probebly problem is in loading one of pyhton packages
AttributeError: Mostly because of "attr" attribute in "color_inline_november9.py"
FileNotfound: mostly is a result of the missing one of the programs, e.g. phonon
ModuleNotFoundError: No module named 'pandas.compat'
srun: error: Segmentation fault on running LAMMPS 
zlib.error: Error -3 while decompressing data: invalid code lengths set

#######################################################################################
'''
from datetime import datetime
import sys, os
import builtins
from contextlib import contextmanager
import concurrent.futures
import subprocess

@contextmanager
def open_files(fname, mode):
  try:
    f = open(fname, mode)
    yield f
  finally:
    f.close()

class ERR:
  err_list = [err for err in dir(builtins) if err.endswith("Error")]
  err_list.extend(["srun: error", "zlib.error", "pandas.errors.","Fatal Python error",
              "No such file or directory", "unexpected end of file", "violated", "Broken pipe"])

  def __init__(self, dir):
    self.err = []
    self.fname = os.path.join(dir, 'job.err')

  # reading the job.err files and return the set of the errors (without duplicates)   
  def get_errors(self):
    with open_files(self.fname, 'r') as f:
      lines = f.readlines()

    for line in lines:
      for err in ERR.err_list:
        if line.startswith(err) or line.endswith(err):
          self.err.append(err)
          #break
      #if len(self.err) > 1: break
    return self.err  

# get the directories names from consol
dirs = sys.argv[1:]
dirs = [dir for dir in dirs if (os.path.exists(dir+'/job.err'))]
# print("NUMBER OF DIRECTORIES: {}".format(len(dirs)))

err_src=[]
def err(src) -> None:
  df = ERR(src)
  if len( df.get_errors() ) > 1: 
    print(src, set( df.get_errors() ), len( df.get_errors() ))
    err_src.append(src)

with concurrent.futures.ThreadPoolExecutor() as executor:
  error_job = executor.map(err,dirs)

class GetJobId:
  def __init__(self,src) -> None:
    self.src = os.path.join(src, 'job.out')

  def get_id(self) -> int:
    try:
      with open_files(self.src, 'r') as f:
        self.head = [next(f) for x in range(2)]
      self.id = self.head[1]
      self.id = self.id.split(" = ")[1].strip()
      # print(self.src, self.id,file=sys.stderr)
      if self.id is not None : return self.id
    except: pass

def cancel_rm(src) -> None:
  id = GetJobId(src)
  subprocess.Popen(['scancel' ,f'{id.get_id()}'])
  subprocess.Popen(['rm', '-rf', f'{src}'])
  print(f"JOB {id.get_id()} canceld and dir {src} is removed")

print(f'{len(err_src)} sources faced error(s)')

sys.stdout = open('ERROR','+a')
print(f"\n{datetime.now()}")
with concurrent.futures.ThreadPoolExecutor() as executor:
  remove_job = executor.map(cancel_rm, err_src)