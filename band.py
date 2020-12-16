#!/usr/bin/env python3

'''
calculating phononic band structure of a trigunal lattice (hegzagonal laticce)
the Dynamical matrix of the system:

                    D(q) = 2D/M \sum_{i=3}^{n} [1 - np.cos(qn_ia)]n_i*n_i{T}
            
                   |
               ____|____
              /    |    \
             /     |    .\M
        ____/_____G|______\K_______
            \      |      /     
             \     |     /
              \____|____/
                   |
based on the Knop paper
'''

import sys
import numpy as np
import matplotlib.pyplot as plt

#lattice = 'sparse'
lattice = sys.argv[1]

if lattice == 'sparse': g = (1+np.sqrt(5))/2   # sparse lattice: a = 1.618033988749895
elif lattice == 'dense': g = 2/(1+np.sqrt(5))  # dense lattice:  a = 0.6180339887498948
elif lattice == 'unit': g = 1                  # normal lattice: a = 1.0
else: sys.exit("undefined lattice unite")
    

def dynamical_matrix(kx, ky, matrix):
    """
    dynamical matrix
    """
    matrix[0,0] = 3.0 - 2*np.cos(g*kx) - np.cos(g*0.5*kx)*np.cos(g*0.5*SQRT3*ky)
    matrix[1,1] = 3.0 - 3*np.cos(g*0.5*kx)*np.cos(g*0.5*SQRT3*ky)
    matrix[0,1] = matrix[1,0] = SQRT3 * np.sin(g*0.5*kx) * np.sin(g*0.5*SQRT3*ky)
    for i in (0,1): 
        for j in (0,1): matrix[i,j]*=FC
    return matrix

kk=[];f1=[];f2=[]
def diag_append(matrix,k):
    # call LAPACK to compute eigenvalues and vectors: eigenvalues -> w; eigenvectors -> v
    w,v=np.linalg.eig(a)
    kk.append(k)
    f1.append(np.sqrt(w[0]))
    f2.append(np.sqrt(w[1]))
    #print(k, np.sqrt(w[0]), np.sqrt(w[1]))


step=0.1
FC=72.00
a=np.zeros((2,2))

# reciprical lattice vectors
SQRT3=np.sqrt(3)
b = 4*np.pi/SQRT3/g
b1x = 0.5*SQRT3*b; b1y = -0.5*b
b2x = 0.0; b2y = b

fbz=0.5*b
for kn in np.arange(0,fbz+step,step):
    kx=kn*np.cos(np.pi/6)
    ky=kn*np.sin(np.pi/6)
    a=dynamical_matrix(kx,ky,a)
    diag_append(a,kn)
kn30=kn
#for i in range(len(kk)):
#    print(kk[i],f1[i],f2[i])
#exit()
# scan K-M direction
fbz=1
kx0=0.5*b*np.cos(np.pi/6)
ky0=0.5*b*np.sin(np.pi/6)
for kn in np.arange(0,fbz+step,step):
    kx=(1-kn)*0.5*b*np.cos(np.pi/6)+b/SQRT3*(kn)
    ky=(1-kn)*0.5*b*np.sin(np.pi/6)
    d=np.sqrt((kx-kx0)*(kx-kx0)+(ky-ky0)*(ky-ky0))
    a=dynamical_matrix(kx,ky,a)
    diag_append(a,d+kn30)

kn2=d+kn30
   
fbz=b/SQRT3
for kn in np.arange(0,fbz+step,step):
    kx=fbz-kn
    ky=0.0
    a=dynamical_matrix(kx,ky,a)
    diag_append(a,kn+kn2)
    
plt.xticks([0,kn30,kn2,kn+kn2],(r'$\Gamma$','M','K',r'$\Gamma$'),fontsize=14)
print(0,kn30,kn2,kn+kn2)
#plt.title("bands for '{}' lattice: a = {:.3f}".format(lattice,g))
plt.yticks(np.arange(0,21,step=5), fontsize=14)
plt.ylabel(r'$\omega$', fontsize=16)
plt.ylim(0,21)
plt.xlim(0,kn+kn2)
plt.plot(kk,f1)
plt.plot(kk,f2,ls='dashed')
plt.vlines(kn30,0,21,color='k',lw=0.75)
plt.vlines(kn2,0,21,color='k',lw=0.75)
x0,y0=(kn30+kn2)/2,3.5
plt.plot(x0,y0,marker='H', markersize=85,markerfacecolor='w',
             markeredgewidth=1.5, markeredgecolor='r')
plt.plot(x0,y0,marker='.',markerfacecolor='k',markeredgecolor='k')
plt.plot(x0+1.185/g,y0,marker='.',markerfacecolor='k',markeredgecolor='k')
plt.plot(x0+0.62/g,y0+2.85,marker='.',markerfacecolor='k',markeredgecolor='k')
plt.plot([x0, x0+1.185/g], [y0, y0], color='k', linestyle='--', linewidth=1)
plt.plot([x0, x0+0.62/g], [y0, y0+2.85], color='k', linestyle='--', linewidth=1)
plt.plot([x0+1.185/g, x0+0.62/g], [y0, y0+2.85], color='k', linestyle='--', linewidth=1)

plt.text(x0,y0-1,r'$\Gamma$')
plt.text(x0+0.7/g,y0-1,'K')
plt.text(x0+0.5/g,y0+1.4,'M')
#xreso=[0,3.1093703386872296,1.0364567795624122,2.072913559124812]
#yreso=[0,20.26349485751388,9.018104184917219,16.250064272494793]
#reso=np.loadtxt('unit',usecols=(1,2,3)).T
#print(kn30)
#reso2=reso[2][reso[0]<kn30]
#reso1=reso[1][reso[0]<kn30]
#reso0=reso[0][reso[0]<kn30]
#print(np.sort(reso2))
#plt.scatter(reso0,reso1,marker='h',s=50,c='k')
#reso=np.loadtxt('unit1',usecols=(1,2,3)).T
#reso2=reso[2][reso[0]<kn30]
#reso1=reso[1][reso[0]<kn30]
#reso0=reso[0][reso[0]<kn30]
#print(np.sort(reso2))
#plt.scatter(reso0,reso1,marker='h',s=50,c='r')
reso=np.loadtxt('dense_T50',usecols=(1,2)).T
plt.scatter(reso[0],reso[1],marker='h',s=50,c='k')
reso=np.loadtxt('dense_T3',usecols=(1,2)).T
plt.scatter(reso[0],reso[1],marker='h',s=50,c='r')
reso=np.loadtxt('dense_reso',usecols=(1,2)).T
plt.scatter(reso[0],reso[1],marker='h',s=50,c='k')
reso=np.loadtxt('dense_L3',usecols=(1,2)).T
plt.scatter(reso[0],reso[1],marker='h',s=50,c='r')


plt.savefig("band.pdf")
plt.show()


