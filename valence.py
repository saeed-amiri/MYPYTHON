import glob
import matplotlib
import numpy as np
import pandas as pd
from scipy import integrate
import matplotlib.pyplot as plt

'''
Santiago Version 05.10.2019
calculating the Valence

'''
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

### helper function to read data file and return first two columns as lists
def read(file_name):
    df = pd.read_csv(file_name,sep=',',skiprows=20,skipfooter=1, header=None, engine='python')
    xdata=np.asarray(df[0])    
    ydata=np.asarray(df[1])
    return xdata.tolist(), ydata.tolist()

### helper function to get normal value to normalized all ydatas
def normal_value(norm_file):
    xdata, ydata = read(norm_file)
    i_ave=xdata.index(550)
    f_ave=xdata.index(560)
    arr_ave = ydata[i_ave:f_ave]
    return np.average(arr_ave)

#!finding the closest value of a list to a certain value
def closest(list, k):
    lst = np.asanyarray(list)
    idx = (np.abs(lst - k)).argmin()
    return idx

### helper function to plot data
def plot_data(file_name):
    labeler=file_name.split(".")
    Intensity, Energy = read(file_name)
    ax.plot(Intensity, Energy, label=labeler[0])

### helper to integrate
def integral(file_name,x1,x2,text):
    x, y = read(file_name)
    xdata = np.asanyarray(x); ydata = np.asanyarray(y)
    i = int(closest(xdata,x1))
    f = int(closest(xdata,x2))
    xi = xdata[i:f]; yi = ydata[i:f]
    #integ = np.trapz(yi,x = xi, dx = 14.061592342877,axis=0)
    integ = integrate.simps(yi,x = xi, dx = 14.061592342877,axis=0)
    fill_bet(xi,yi,text)
    return integ

### to fill the integration area
def fill_bet(x,y,text):
    ax.fill_between(x,y,alpha= 0.5)
    p = np.argmax(y)
    ax.text(x[p-13],y[p]/3,text,c = 'r',size=13)
    
### reading files (!!! all the files which are ended with extention ".msa" are reding !!!)
for f in glob.glob("*.msa"):
    plot_data(f)
    x1 = 638; x2 = 648; x3 = 658
    L3 = integral(f,x1,x2,"L3")
    L2 = integral(f,x2,x3,"L2")
    valence = -0.73 * L3/L2 + 5
    print("L3/L2 = ", L3/L2, ", Valence = ", valence)

plt.legend()
plt.xlabel("Energy Loss [eV]")
plt.ylabel("Intesity [a.u.]")
xl = 620; xh = 700
plt.xlim([xl,xh])
ax.text((xh+xl)/2, 20000,"Valence = {:.3}".format(valence))

plt.show()
#plt.savefig("fig.png")