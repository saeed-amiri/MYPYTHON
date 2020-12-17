#!/usr/env/bin pyhton3
'''
read job_average of simulations and produce a DataFrame of system:

t0: when system start to decay (can be cahnged by "critical_time" in "JOB" calss)
t1: when system start to decay (can be cahnged, 0.05 in "JOB" calss)
fit to desierd function:
coef1, eta1: fitting parameters

needed files:
PARAM
job_average

'''

import os, sys
import builtins
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from itertools import islice
from scipy.optimize import curve_fit
from contextlib import contextmanager
from matplotlib.backends.backend_pdf import PdfPages

@contextmanager
def open_file(file_name, mode):
	try:
		f = open(file_name,mode)
		yield f
	finally: f.close()

def smooth_dataframe(df,sz,dt):
	df['i'] = df.index
	df['x'] = np.arange(df.shape[0])//sz
	df=df.groupby(df['x'],axis=0).mean()
	df.index=df['i']*dt
	df.drop(columns=['i','x'],inplace=True)
	return df

def get_param(fname,string):
	chk = f"#{string}"
	try:
		with open_file(fname,'r') as fp:
			for line in fp:
				field=line.strip().split('=')
				if field[0]==chk:
					return field[1]
	except: print(f'WARNNING: file, {fname}, does not contain variable {chk}')

def closest(array, k): return (np.abs(array - k)).argmin()

#fitting function
def func1(t,coef,eta): return coef * np.exp(-eta * t)
def func2(t,coef,eta): return coef * np.exp(-eta * t**2) 
def fune(t,a,b,c): return np.max(t) / (c + np.exp(a*(t-b)) )

class ERR():
    err_list = [err for err in dir(builtins) if err.endswith( "Error")]
    err_list.extend(["srun: error", "zlib.error","pandas.errors.",
                "No such file or directory", "unexpected end of file","violated","Broken pipe"])
    def __init__(self, dir):
        self.err = ' '
        fname = os.path.join(dir, 'job.err')
        with open_file(fname, 'r') as f:
            lines = f.readlines()
        for line in lines:
            for err in ERR.err_list:
               if line.startswith(err) or line.endswith(err):
                    self.err = err
                    break
            if len(self.err) > 1: break

class JOB:
	'''
	reading job_average from directory and return values
	'''
	def __init__(self,dir):
		fname = os.path.join(dir, 'job_average')
		df = pd.read_csv( fname, delim_whitespace=True, header=0, index_col=0 )
		df = smooth_dataframe(df,10,0.001)
		self.header=df.head; self.index = df.index
		self.vx = np.array(df['c_VCOM[1]']); self.vy = np.array(df['c_VCOM[2]'])
		self.vx0 = self.vx[0]; self.vy0 = self.vy[0]
		self.temp = df['c_TEMP']
		self.v = np.hypot(self.vx, self.vy)
		pname = dir + '/PARAM'
		self.kick = -1.0 if get_param(pname,"KICK") is None else float(get_param(pname,"KICK"))
		if self.kick == -1.0: sys.exit('ERROR: in getting KICK from PARAM')
		critical_time = 0.90; thermo_time = 0.05
		self.crit_place = closest( self.vx, self.vx0 * critical_time )
		self.stop = closest( self.vx, self.vx0*thermo_time  )
		self.decay = self.vx[self.crit_place:self.stop].tolist()
		self.thermalized = self.temp[self.stop:].mean()
		self.argdecay = df.index[self.crit_place:self.stop]-df.index[self.crit_place]

class INIT():
		def __init__(self,dir):
			fname = os.path.join(dir, 'INIT.0')
			with open_file(fname,'r') as f:
				INIT = list(islice(f, 25))
			for line in INIT:
				if line.strip().endswith('atoms'): self.natoms=line.strip().split(' ')[0]
				if line.strip().endswith('bonds'): self.nbonds=line.strip().split(' ')[0]
				if line.strip().startswith('Bond'):self.bondstyle=line.strip().split(' ')[-1]
				if line.strip().endswith('xhi'):
					self.xlo = float(line.strip().split(' ')[0])
					self.xhi = float(line.strip().split(' ')[1])
				if line.strip().endswith('yhi'):
					self.ylo = float(line.strip().split(' ')[0])
					self.yhi = float(line.strip().split(' ')[1])
			self.lx = self.xhi-self.xlo
			self.ly = self.yhi-self.ylo
			self.area = self.lx*self.ly
			fname = os.path.join(dir, 'PARAM')
			self.cutbonds = get_param(fname,'CUTBONDS')
			self.coupling = get_param(fname,'COUPLING')
			self.timestep = get_param(fname,'DT')
			self.cwd = dir.split('/')[0]


dirs = sys.argv[1:]
OutDir = '.'
if '=' in dirs[-1]: 
	OutDir = dirs.pop().split('=')[1]
	os.makedirs(OutDir,exist_ok=True)
print('SETTING OutDir:',OutDir)

dirs = [(i.strip('/')) for i in dirs if os.path.exists(i+'/job_average')]
print(f'number of intro dirs: {len(dirs)}')

err_dirs = []; err = []
for dir in dirs:
	df = ERR(dir)
	if len(df.err)>1: 
		err_dirs.append(dir)
		err.append(df.err)
if err_dirs: dirs = [dir for dir in dirs if dir not in err_dirs]
print(f'number of dirs: {len(dirs)}')

if len(dirs)==0 : sys.exit(" ERROR! NO DIRECTORY TO READ")

def do_fit(x, y):
    p1,_ = curve_fit(func1, x, y, p0=[0.01,0.0001])
    p2,_ = curve_fit(func2, x, y, p0=[0.01,0.0001])
    return p1, p2

def assign_df(df):
#getting information from all the dirs
    t0 = []; t1 = []; coef1 = []; eta1 = []; coef2 = []; eta2 = []; thermalized = []; vx0 = []; vy0 = []
    for i,dir in enumerate(df.DIR):
        dj=JOB(dir)
        t0.append(dj.crit_place); t1.append(dj.stop); 
        thermalized.append(dj.thermalized)
        vx0.append(dj.vx0); vy0.append(dj.vy0)
        #fitting
        p1, p2 = do_fit(dj.argdecay, dj.decay)
        coef1.append(p1[0]); eta1.append(p1[1])
        coef2.append(p2[0]); eta2.append(p2[1])
    df['t0'] = t0; df['t1'] = t1; df['decay_time'] = df.t1-df.t0
    df['coef1']=coef1; df['eta1']=eta1; df['coef2']=coef2; df['eta2']=eta2
    df['thermalized']=thermalized; df['vx0']=vx0; df['vy0']=vy0
    return df

def info_pdf(init,axes):
    plt.suptitle('Summary')
    #write in first column
    l1 = [f'Parent dir: {os.getcwd()}',f'Source dir: {init.cwd}',f'Numbers of sub-directories: {len(dirs)}']
    l2 = [f'Bondstyle: {init.bondstyle}',r'$L_x/L_y =$ {}'.format(init.lx/init.ly),f'Numbers of particles = {init.natoms}',
          f'Numbers of bonds = {init.nbonds}', f'Coupling = {init.coupling}', f'Cut bonds: {init.cutbonds}', f'Timestep = {init.timestep}']
    sub_tit = ['Directory infos:','Simulations infos:']
    ll = (l1, l2)
    for j, l in enumerate(ll):
        axes[j].axis('off')
        axes[j].set_title(sub_tit[j],x=0, y=1,ha='left',fontsize=13)
        for i, txt in enumerate(l):
            height=0.95-i*0.05
            color='r' if (i==0 and j==1) else 'k' 
            axes[j].text(0,height,txt ,color = color)
        if err_dirs and j==0:
            for ii, (ed, ee) in enumerate(zip(err_dirs,err)):
                axes[0].text(0,height-ii*0.1,f'err_dirs: {ed}\nerr: {ee}')
class DATA():
    def __init__(self):
        #making data frame from all "dir" in "dirs"
        #initiat dataframe with "dirs" names
        df = pd.DataFrame(dirs,columns=['DIR'])
        #adding KICK from PARAM files
        kick = []
        for dir in df['DIR']:
            kick.append(float(get_param(os.path.join(dir,'PARAM'),"KICK")))
        df['KICK'] = kick
        #sort the "dirs" list based on the "kick"
        df.sort_values('KICK', inplace=True, ignore_index=True)
        #assign data to df
        df=assign_df(df)
        #attach attributes to obj
        self.index = df.index; self.DIR = df['DIR']
        self.KICK = df['KICK']; self.t0 = df.t0
        self.t1 = df.t1; self.decay_time = df.decay_time
        self.coef1 = df.coef1; self.eta1 = df.eta1; self.coef2 = df.coef2; self.eta2 = np.sqrt(df.eta2)
        self.thermalized = df['thermalized']
        init=INIT(df.DIR[0])
        ###################################################################################################
        ##save data to pdf file by setting graph
        nplots = 2
        fig, axes = plt.subplots(1,nplots, figsize=(12.8, 6.8))
        info_pdf(init,axes)
        ###################################################################################################

        pdf.savefig(fig)
        
        #start plotting
        # plotting the decay curve with fitted graphs
        fig, axes = plt.subplots(1,2, figsize=(12.8, 6.8))
        for i in range(2):axes[i].tick_params(axis='both', which='major', labelsize=14)
        select = [np.argmax(self.t0), len(dirs)//2, np.random.random_integers(2,len(dirs)-2) ]#, np.argmin(self.t0)]
        labels = ['max', 'median', 'random', 'min']
        color = ['b','r','k','g']
        plt.suptitle("fitting the decay of COM velocity (max: longest initial transition, etc.)")
        for j, i in enumerate(select):
            dj=JOB(self.DIR[i])
            print(j,i,dj.kick)
            axes[0].plot(dj.argdecay,dj.decay,label=f"kick={dj.kick:.4f},({labels[j]})",color=color[j],ls='dashed')
            axes[0].plot(dj.argdecay,func1(dj.argdecay,df.coef1[i],df.eta1[i]),color=color[j])
            axes[1].plot(dj.argdecay,dj.decay,label=f"kick={dj.kick:.4f},({labels[j]})",color=color[j],ls='dashed')
            axes[1].plot(dj.argdecay,func2(dj.argdecay,df.coef2[i],df.eta2[i]),color=color[j])

        plt.legend(fontsize=14)
        for i in range(2):	
            axes[i].set_xlabel("time",fontsize=16); axes[i].set_ylabel(r"$v_{COM}$",fontsize=16)
            axes[i].legend(fontsize=14)
        axes[0].set_title(r'$a_1\,e^{-\eta_1 t} $',fontsize=18)
        axes[1].set_title(r'$a_2\,e^{-\eta_2 t^2} $',fontsize=18)
        head=['KICK', 'vx0', 'vy0', 't0','t1','decay_time', 'coef1', 'eta1', 'coef2', 'eta2', 'thermalized','DIR']
        df.to_csv(OutDir+'/df',sep='\t',index_label='#index',columns=head,header=head)		
        pdf.savefig(fig)




with PdfPages(OutDir+'/df.pdf') as pdf:

	df=DATA()
	##########################################################################
	nplots = 2
	fig, axes = plt.subplots(1,nplots, figsize=(12.8, 6.8))
	for i in range(nplots):axes[i].tick_params(axis='both', which='major', labelsize=14)
	st = fig.suptitle(r'fitting the decay with " $a_1\,e^{-\eta_1 t}$ " and " $a_2\,e^{-\eta_2 t^2}$ "'+
										f', data over {len(dirs)} diffrent directories (KICK)',fontsize=14)
	plt.subplots_adjust(wspace=0.3)
	# Setting the values for all axes.
	plt.setp(axes, xlim=(0,df.KICK.max()))

	plt_list = [df.KICK,df.t0,df.decay_time,df.coef1,df.eta1,df.coef2,df.eta2]

	act_list = ['kick', 'transition', 'decay time',  r'coeff $(a_1)$',r'$\eta_1$',  r'coeff $(a_2)$', r'$\sqrt{\eta_2}$']
	axes[0].plot(df.KICK,df.KICK,ls=':',c='r',lw=2,label=r"$y=x$")
	for i,pl in enumerate(plt_list[3:5]):
		axes[i].plot(df.KICK[1:],pl[1:],label=act_list[i+3])
		axes[i].plot(df.KICK[1:],plt_list[i+5][1:], ls='dashed',label=act_list[i+5])
		#axes[i].set_ylabel(labels[i],fontsize=14)
		axes[i].set_xlabel('kick',fontsize=14)
		axes[i].set_ylim(pl[1:].min(),pl[1:].max())
		#axes[i].set_title(titles[i])
		axes[i].legend(fontsize=14)
	#plt.show()
	pdf.savefig(fig)
	
	
	nplots = 2
	fig, axes = plt.subplots(1,nplots, figsize=(12.8, 6.8))
	for i in range(nplots):axes[i].tick_params(axis='both', which='major', labelsize=14)
	titles = ['beginning of decay','duration of decay']
	labels = [r'$t_0$','decay time',r'$\tau$']
	for i,pl in enumerate(plt_list[1:3]):
		axes[i].plot(df.KICK,pl)
		axes[i].set_ylabel(labels[i],fontsize=14)
		axes[i].set_xlabel('kick',fontsize=14)
		axes[i].set_ylim(pl.min(),pl.max())
		axes[i].set_xlim(df.KICK.min(),df.KICK.max())
		axes[i].set_title(titles[i])
	#plt.show()
	pdf.savefig(fig)

	#plot t0 and decay time on same gaph
	nplots = 1
	fig, axes = plt.subplots(1,nplots, figsize=(12.8, 6.8))
	axes.tick_params(axis='both', which='major', labelsize=13)
	#axes1: plot 't0' with color=red
	color = 'r'
	axes.plot(df.KICK,plt_list[2],color=color)
	axes.tick_params(axis='y',colors=color)
	axes.set_xlabel(r'${KICK}$',color='k',fontsize=14)
	axes.set_ylabel(r'decay time',color=color,fontsize=14)
	axes.set_xlim(df.KICK.min(), df.KICK.max())
	axes.set_ylim(0, plt_list[2].max())

	axes2=axes.twinx()
	axes2.tick_params(axis='both', which='major', labelsize=14)
	color = 'blue'
	axes2.tick_params(axis='y',colors=color)
	axes2.set_ylabel(r'$t_0$',color=color,fontsize=14)
	axes2.plot(df.KICK,plt_list[1],color=color,ls='dashed')
	axes2.set_ylim(0, plt_list[1].max())
	pdf.savefig(fig)
#	plt.show()

def min_max(dir,mode,j):
	if mode == 'max' : out.write(f"\n\nHighest {act_list[j]}:")
	if mode == 'min' : out.write(f"Lowset {act_list[j]}:")
	out.write(f"  kick={df.KICK[dir]},\n\tt0={df.t0[dir]},  t1={df.t1[dir]},  tau={df.coef1[dir]},\n\tdir: {df.DIR[dir]}\n")

with open_file(OutDir+'/max_min','w') as out:
	out.write(''.join(['-']*70))
	out.write(f'\ndata over {len(dirs)} diffrent directories (KICK)\n')
	out.write(''.join(['-']*70))
	for j, i in enumerate(plt_list):
		min_max(np.argmax(i),'max',j)
		min_max(np.argmin(i),'min',j)
		out.write(''.join(['_']*70))