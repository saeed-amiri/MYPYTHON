import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### helper function to read data file and return first two columns as lists
def read(file_name):
    df = pd.read_csv(file_name,sep=',',skiprows=20,skipfooter=1, header=None, engine='python')
    xdata=np.asarray(df[0])    
    ydata=np.asarray(df[1])
    return xdata.tolist(), ydata.tolist()

### helper function to get normal value to normalized all ydatas
def normal_value(norm_file):
    xdata, ydata = read(norm_file)
    i_ave=xdata.index(1.5)
    f_ave=xdata.index(2)
    arr_ave = ydata[i_ave:f_ave]
    return np.average(arr_ave)

### helper function to plot data
def plot_data(file_name):
    labeler=file_name.split(".") 
    Intensity, Distance = read(file_name)
    #normal_val = normal_value()
    plt.plot(Intensity, Distance, lw=2, label=labeler[0])
    

### reading files (!!! all the files which are ended with extention ".msa" are reding !!!)
for f in glob.glob("*.msa"):
    plot_data(f)

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlabel("Distance [nm]")
plt.ylabel("Intesity [a.u.]")
#plt.title("normalized to O1:[550,650]")
plt.xlim(0.01,2.1)
plt.ylim([2900,4000])

plt.show()
#plt.savefig("fig.png")