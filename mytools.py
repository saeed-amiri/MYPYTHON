import sys,pandas as pd,numpy as np,glob,gzip

# FUNCTION: return numerical value of variable str from my typical PARAM files
def get_param(fname,str):
  chk = "#{}".format(str)
  fp=open(fname)
  for line in fp:
    field=line.strip().split('=')
    if field[0]==chk:
      fp.close()
      return field[1]
  print('ERROR: file',fname,'does not contain variable',str)
  exit()

# FUNCTION: return n-th line from file, which may be gzipped (!)
def get_line_number(file,n):
  n=int(n)
  if file.endswith('.gz'): f=gzip.open(file,'rt')
  else: f=open(file)
  return f.readlines()[n-1:n][0].strip()

# FUNCTION: prints string w in bold red, without newline at end
def PBR(w):
  # see	here for some info on colors: http://ascii-table.com/ansi-escape-sequences.php
  # 1=bold,31=foreground red
  bold_red = '\033[1;31m'
  normal = '\033[0m'
  print(bold_red + w + normal,end='')

# FUNCTION: print string then exit
def printerror(*args):
  bold_red = '\033[1;31m'
  normal = '\033[0m'
  print(bold_red + 'ERROR:' + normal,' '.join(args),file=sys.stderr)
  exit()

# FUNCTION: print string but do not exit
def printwarning(*args):
  color = '\033[1;34m'
  normal = '\033[0m'
  print(color + 'WARNING:' + normal,' '.join(args),file=sys.stderr)

# FUNCTION: read multi-column ascii text file containing __numbers only __ and return list of column averages
def text_file_average(file):
  df=pd.read_csv(file,delim_whitespace=True,header=None)
  avg=[]
  for c in df.columns: avg.append(df[c].mean())
  return avg

# SMOOTHING FUNCTION: https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
def smooth(x,window_len=11,window='hanning'):
  if x.ndim != 1:
    printerror('smooth only accepts 1D arrays')
  if x.size < window_len:
    printerror('input vector needs to be bigger than window size')
  if window_len<3:
    return x
  if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
    printerror('window must be one of: flat hanning hamming bartlett blackman')
  if window_len%2 == 0:
    printerror('window length must be an odd integer')
  s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
  if window == 'flat':
    w=np.ones(window_len,'d')
  else:
    w=eval('np.'+window+'(window_len)')
  y=np.convolve(w/w.sum(),s,mode='valid')
  # return array must have same length
  return y[:x.size]

# FUNCTION: READ PHONON DATA
def read_phonon_all(RUNID):

  # read k-grid
  df=pd.read_csv('KGRID.' + RUNID,delim_whitespace=True,header=None)

  # number of k-vectors in the grid
  numpoints=df.shape[0]

  # for each k-vector: store components (kx,ky); k-vector length; frequency of each polarization mode
  kx=df[0]; ky=df[1]; kn=np.sqrt(kx*kx+ky*ky); w1=df[2]; w2=df[3]

  # read COLOR data: the color data is scattered over several COLOR.RUNID.* files (!)
  color=[]
  for f in glob.glob('COLOR.' + RUNID + '.*'):
    # use gzip if needed
    if f.endswith('.gz'): color.append( pd.read_csv(f,compression='gzip',delim_whitespace=True,header=None) )
    else: color.append( pd.read_csv(f,delim_whitespace=True,header=None) )
  color=pd.concat(i for i in color)
  # column 0 contains the time step: make this the index
  color=color.set_index(0)
  # make sure index is treated as integer (!)
  color.index=color.index.astype(int)
  # sort data in order of increasing index
  color=color.sort_index()
  # SANITY CHECK: ncols must equal 4 \times numpoints
  if color.shape[1] != 4*numpoints: printerror('color data does not match FBZ grid')
  # number of snapshots in the MD trajectory
  numframes=color.shape[0]
  # rename columns as integers starting from 0
  color.columns=np.arange(4*numpoints,dtype=int)

  # RETURN ALL IN ONE GO (!)
  return kx,ky,kn,w1,w2,color,numpoints,numframes
