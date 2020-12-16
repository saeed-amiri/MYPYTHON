#!/usr/env/bin python3 

import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dirs = sys.argv[1:]
print(dirs)
csv = sys.argv[-1].split("=")[1] if '=' in sys.argv[-1] else 'df'
dirs = [i for i in dirs if os.path.exists(i+'/'+csv)]

class DATA:
	def __init__ (self,dir):
		print(dir+'/'+csv)
		df = pd.read_csv(dir+'/'+csv, delim_whitespace=True, header=0, index_col=0 )
		self.index = df.index
		self.kick = df['KICK']
		self.t0 = df['t0']
		self.eta = df['eta1']



lstyle = ['-',':']#,'-.','--']
lwidth = [1.5,2,2,2]
lcolor = ['r', 'b']#,'g','k']
max_t0 = []; imax_t0 = []; kicks = []
plt.tick_params(axis='both', which='major', labelsize=13)
# ploting the t0
#for j , i in enumerate(dirs):
#	df = DATA(i)
#	plt.plot(df.kick,df.t0,label=str(i.split('_')[1]),ls=lstyle[j],c=lcolor[j])
#	max_t0.append(df.t0.max())
#	imax_t0.append(df.t0.argmax())
#	kicks.append(df.kick[df.t0.argmax()])
#for j , i in enumerate(dirs):
#	plt.vlines(kicks[j],0,np.max(max_t0),colors=lcolor[j],linestyles=list(reversed(lstyle))[j],lw=2)
#plt.xlim(0,df.kick.max())
#plt.ylim(0,np.max(max_t0))
#plt.xlabel('kick')
#plt.ylabel('transition (time)')
#plt.legend()
#plt.savefig('trnasition.pdf')
#plt.show()
max_eta=[]
imax_eta=[]
# ploting the eta
for j , i in enumerate(dirs):
	df = DATA(i)
	plt.plot(df.kick,df.t0,label='N='+str(i.split('_')[1]),ls=lstyle[j],c=lcolor[j],lw=lwidth[j])
	max_eta.append(df.t0.max())
	imax_eta.append(df.t0.argmax())
	kicks.append(df.kick[df.t0.argmax()])
plt.xlabel(r'$kick$',fontsize=14)
#plt.ylabel(r'$t_0$',fontsize=16)
plt.ylabel('transition (time)',fontsize=14)
plt.xlim(df.kick.min(),df.kick.max())
plt.ylim(0,1200)
for j , i in enumerate(dirs):
	plt.vlines(kicks[j],0,np.max(max_eta),colors=list(reversed(lcolor))[j],linestyles=lstyle[j],lw=2,zorder=5)
print(kicks,max_eta,imax_eta)
plt.tight_layout()
plt.legend(fontsize=14)
plt.savefig('transit.png')
plt.show()
