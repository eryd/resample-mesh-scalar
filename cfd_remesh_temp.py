#!/usr/bin/python

# This script resample a 2D calculation result from CFD
# from higher resolution into a lower resolution. This particular
# script handles the temperature result, or any other scalar
# parameter. Another corresponding script handles velocity result.
# 
# This script is developed as a support for the following workflow.
# CFD calculation (prepared through Rhino-Grasshopper-Butterfly
# and then OpenFoam) is used to provide input for thermal comfort
# calculation conducted by Rhino-Grasshopper-Honeybee and EnergyPlus.
# CFD calculation provides the air velocity and temperature distribution
# for the thermal comfort calculation.
# 
# The CFD calculation is typically run at a higher resolution
# so that the airflow distribution can be fully resolved. Such a
# fine mesh will be very slow to process in the thermal comfort
# calculation. The finer mesh needs to be resampled into a coarser
# mesh so that the comfort calculation can be performed quickly.
# 
# There is a Grasshopper object that can perform the same task as
# this script, but the processing time is slow. For the size of mesh
# that triggers the development of this script (about 3 million
# point on a horizontal plane), the processing time through Grasshopper
# is prohibitive. Hence, this script.
# 
# This script takes two input files and produces two output files.
# 
# The first input is a CSV file containing 2D data of temperature
# as typically output from ParaView, i.e. a CSV containing four
# columns, the first one is the temperature and the next three
# columns are the cell coordinate in x,y,z. The first row of the 
# file contains the header.
# 
# The second input is a CSV file containing the coordinates of the
# points from the second mesh with lower resolution. This file contains
# three columns for the x,y,z coordinate values. Typically this file
# is an output from comfort grid points defined in Grasshopper Honeybee.
# 
# The script outputs two files, one with coordinates and the other
# without the coordinates. The temperature values are listed in the
# first column. Both contains the same order of points as provided
# by the second input file. The single column output is ready to be
# input into the thermal comfort calculation object in Honeybee.
# 
# This script is hosted at github.
# 
# Credit:
# This file is developed from an example in StackOverflow:
# https://earthscience.stackexchange.com/questions/12057/how-to-interpolate-scattered-data-to-a-regular-grid-in-python
# specifically, this answer:
# https://earthscience.stackexchange.com/a/12061/16958
# 
# Written by:
# Ery Djunaedy
# www.kinerja.org
# v.1 - 2019-05-24
#
# LEGALESE: CC BY-NC-SA 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
# In plain English:
# You are free to use, change, and redistribute this script
# as long as you:
# 1. give credit to us
# 2. license your new creations under the identical terms
# 3. do not make money out of it
# 4. release us from liability for any damages
############################################################

import sys
import numpy as np
from scipy.interpolate import griddata
from datetime import datetime

############################################################
if len(sys.argv) < 3:
    print("This script needs two arguments.")
    print("Usage: cfd_remesh_temp filename1 filename2")
    print("Aborting ...")
    exit()

starttime = datetime.now()

filename1 = sys.argv[1]
filename2 = sys.argv[2]
basename1 = filename1.split(".")
basename2 = filename2.split(".")
filename3 = basename1[0] + "_" + basename2[0] + "_output_with_coordinates.csv"
filename4 = basename1[0] + "_" + basename2[0] + "_output_single_column.csv"
print "Filename1 = ",filename1
print "Filename2 = ",filename2
print "Output file1 =",filename3
print "Output file2 =",filename4
print("")

############################################################
print "Processing ",filename1," at ",datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# read data from CSV file, then
# assign to array per column of the CSV file
data = np.genfromtxt(filename1, delimiter=",", skip_header=1)

#DEBUG print(data)
#DEBUG print(data.shape)
# Always check what you are importing
# the shape should be 2D array, i.e. (row, column)

# column 1: x coordinate
x = data[:,1]
# column 2: y coordinate
y = data[:,2]
# column 0: temperature data
temp1 = data[:,0]

#DEBUG print("x")
#DEBUG print(type(x))
#DEBUG print(x.shape)
#DEBUG print(min(x),max(x))
# Always check what you are importing

############################################################
print "Processing ",filename2," at ",datetime.now().strftime('%Y-%m-%d %H:%M:%S')
grid = np.genfromtxt(filename2, delimiter=",", skip_header=0)

# column 1: x coordinate
xi = grid[:,0]
# column 2: y coordinate
yi = grid[:,1]
# column 3: z coordinate
zi = grid[:,2]

############################################################
# This line below is recorded here as it has caused delays during
# development of this script
# xi,yi = np.meshgrid(xi,yi)
#
# The line above is from the original code in the example of stackexchange.
# ONLY use that code if the xi and yi is the grid axis position.
# Say, for a grid of 10x10, the length of xi is 10 and yi is 10.
# In this case, use the code above to create a grid of 100 points.
# DO NOT use the code if you already have 100 points. If you do, then
# the following line will create a strange result.

############################################################
# Calculating the value of the temperature in the new grid
# based on the temperature value of the nearest location in the
# finer mesh. Aside from nearest, other method can be "linear" or
# cubic.
# 
print "Calculating temperature values at new grid at ",datetime.now().strftime('%Y-%m-%d %H:%M:%S')
temp2 = griddata((x,y),temp1,(xi,yi),method='nearest')
#DEBUG print("temp2")
#DEBUG print(type(temp2))
#DEBUG print(temp2.shape)
#DEBUG print(str(temp2))
#DEBUG print(min(temp2),max(temp2))
# Always check the result
# IF we do NOT use the np.meshgrid above, then this will result in
# one single array.
# However, if we use the np.meshgrid above, then this will result in 
# a 3D array.

############################################################
# Generating one big 2D array from multiple single arrays
# to be written into CSV files.
# The square bracket is important
print "Writing output files ",datetime.now().strftime('%Y-%m-%d %H:%M:%S')
write = np.transpose([temp2,xi,yi,zi])
#DEBUG print("write")
#DEBUG print(type(write))
#DEBUG print(write.shape)

############################################################
np.savetxt(filename3,write , delimiter=',', header="T,x,y,z", fmt="%s", comments="")
# This will ONLY work on 2D array.
# Depending on the result of the griddata above, this will easily
# create error. Always check the type of the result of every step.

write = np.transpose([temp2])
np.savetxt(filename4,write , delimiter=',', fmt="%s", comments="")

############################################################
# Ending
endtime = datetime.now()
duration = endtime - starttime
print "Done at ",endtime.strftime('%Y-%m-%d %H:%M:%S')
print "Duration = ", duration
exit()

############################################################
# Original code
# https://earthscience.stackexchange.com/a/12061/16958

import matplotlib.pyplot as plt

# data coordinates and values
x = np.random.random(100)
y = np.random.random(100)
z = np.random.random(100)

# target grid to interpolate to
xi = yi = np.arange(0,1.01,0.01)

xi,yi = np.meshgrid(xi,yi)

# set mask
mask = (xi > 0.5) & (xi < 0.6) & (yi > 0.5) & (yi < 0.6)

# interpolate
zi = griddata((x,y),z,(xi,yi),method='linear')
print("zi")
print(type(zi))
print(zi.shape)

# mask out the field
zi[mask] = np.nan

# plot
fig = plt.figure()
ax = fig.add_subplot(111)
plt.contourf(xi,yi,zi,np.arange(0,1.01,0.01))
plt.plot(x,y,'k.')
plt.xlabel('xi',fontsize=16)
plt.ylabel('yi',fontsize=16)
plt.savefig('interpolated.png',dpi=100)
plt.close(fig)

