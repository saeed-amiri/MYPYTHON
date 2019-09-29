
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import palettable
from matplotlib.font_manager import FontProperties
font = FontProperties()
font.set_family('serif')
font.set_name('Times New Roman')
font.set_style('italic')
plt.rcParams.update({'font.size': 13})

def f(x,y):
    return (x**2+y**2)**(0.5)

X,Y = np.mgrid[-1:1:100j, -1:1:100j]

Z = f(X,Y)
#plt.figure()
# convert to array to color map, assign to hexagons Sequential
colors1 = palettable.cartocolors.sequential.PinkYl_7.mpl_colormap(np.linspace(0,1,256))
colors4 = palettable.cartocolors.sequential.PinkYl_7_r.mpl_colormap(np.linspace(0,1,256))
# stacking the 2 arrays row-wise
colors = np.vstack((colors1, colors4))

# generating a smoothly-varying LinearSegmentedColormap
CMAP = mcolors.LinearSegmentedColormap.from_list('colormap', colors)

mpb = plt.pcolormesh(X,Y,Z,cmap=CMAP)

# draw a new figure and replot the colorbar there
fig,ax = plt.subplots()
print(Z.max())
print(Z.min())
#cb=plt.colorbar(mpb,ax=ax, orientation='horizontal')
cb=plt.colorbar(mpb,ax=ax,ticks=[Z.min(),(Z.min() + Z.max())/2 ,Z.max()])
#cb.set_ticks([])
cb.outline.set_visible(True)
cb.ax.set_yticklabels([r'$0$', r'$\pi$', r'$2\pi$' ]) 
ax.remove()
# save the same figure with some approximate autocropping
plt.savefig('cbar_v.png',bbox_inches='tight',transparent=True)
#plt.show()