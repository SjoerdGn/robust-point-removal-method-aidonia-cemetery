#!/usr/bin/env python
# coding: utf-8

# (c) Sjoerd Gnodde, 2019
# Made for the course CIE4614-18 3D Surveying of Civil and Offshore Infrastructure (2018/19 Q3)

# WARNING, CODE CAN TAKE LONG TO RUN AND CAUSE YOUR COMPUTER TO BE UNRESPONSIVE

import numpy as np
import matplotlib.pyplot as plt
import time


# load data
data=np.genfromtxt('Upper_Cemetery_Octree.txt',  dtype=float, autostrip=True, skip_header=1, delimiter=',')
color = data[:,9:12]/255
points=data[:,3:7]


# time
first = time.time()

n = 300
m = 300
maxnumbers = 8000

# calculate mins and maxs dataset
maxx = np.max(points[:,0])+.0001
minx = np.min(points[:,0])
maxy = np.max(points[:,1])+.0001
miny = np.min(points[:,1])
lenpoints = len(points[:,0])

zcount = np.zeros((n,m))
zfile = np.empty((n,m,maxnumbers,))
zfile[:] = np.nan


# put point data into grid with multiple z's
for i in range(lenpoints):
    xi = int((points[i,0]-minx)/(maxx-minx)*n)
    yi = int((points[i,1]-miny)/(maxy-miny)*m)
    if zcount[xi,yi] < maxnumbers:
        zfile[xi, yi, int(zcount[xi,yi])] = points[i,2]
    zcount[xi,yi]+=1


print(time.time()-first)
plt.savefig("testpic3.png")


first = time.time()
rep = 5

# empty files to store means and standard deviations
zmean = np.zeros((n,m))
zstd = np.zeros((n,m))

# up part gets increasingly mild, down gets increasingly mild
sdup = np.linspace(1.0,1.3,rep)
sddwn = np.linspace(2.9,1.6,rep)

# arbitrary point for histogram
one_point_x = int(68)
one_point_y = int(42)
one_point = np.empty((len(sdup)+1,maxnumbers,))
one_point[:] = np.nan
k = 0
one_point[k,:] = zfile[one_point_x, one_point_y,:]

# calculate means, std, remove outliers
for l in range(rep):
    for i in range(n):
        for j in range(m):

            std = np.nanstd(zfile[i,j])
            zstd[i,j] = std
            mean = np.nanmean(zfile[i,j])
            zmean[i,j] = mean
            outliers = (zfile[i,j] > (mean + sdup[l] * std)) | (zfile[i,j] < (mean - sddwn[l] * std))
            zfile[i,j,outliers] = np.nan 
    k+=1
    one_point[k,:] = zfile[one_point_x, one_point_y,:]


# empty file to fill when point has been changed
deltah = np.empty((n,m))
deltah[:] = np.nan

# problem with this method: uses data that is rejected in other iteration (but this is not so terrible)
replaced = 0
            
# find and remove outliers
for i in range(1,n-1):
    for j in range(1,m-1):
        outside = [zmean[i,j+1],zmean[i+1,j+1],zmean[i+1,j], zmean[i+1,j-1], zmean[i,j-1], zmean[i-1,j-1], zmean[i-1,j], zmean[i-1,j+1]]
        stdo = np.nanstd(outside)
        meano = np.nanmean(outside)
        if abs(zmean[i,j]-meano)>2*stdo:
            deltah[i,j] = meano
            zmean[i,j] = meano
            replaced += 1

# remove nan values            
for k in range(2):           
    for i in range(1,n-1):
        for j in range(1,m-1):
            if np.isnan(zmean[i,j]):
                outside = [zmean[i,j+1],zmean[i+1,j+1],zmean[i+1,j], zmean[i+1,j-1], zmean[i,j-1], zmean[i-1,j-1], zmean[i-1,j], zmean[i-1,j+1]]
                meano = np.nanmean(outside)
                deltah[i,j] = meano
                zmean[i,j] = meano
                replaced += 1
        

            
        
print("Time", time.time()-first)
print("Replaced:", replaced)



# show outliers removed
plt.figure(figsize=(12,11))
plt.imshow(deltah)
plt.colorbar()
plt.title('Outlier replacements (calculated level - average level around in m)')


# Show the results
plt.figure(figsize=(12,11))
plt.imshow(zmean)
plt.colorbar()
print(np.nanmax(zcount))
plt.plot(one_point_x,one_point_y, 'ro')
print(np.max(zmean))
plt.savefig("testpic1.png")
plt.figure()
#plt.hist(zfile[38,57])
plt.savefig("testpic2.png")

np.savetxt('output_grid.csv', zmean, delimiter=',')

# input distance for CloudCompare
print((maxx-minx)/n)
print((maxy-miny)/m)


# plot
bins = np.linspace(385.5, 386.7, 17)
for i in range(6):
    plt.figure()
    plt.hist(one_point[i], orientation = 'horizontal',  bins=bins)
    plt.ylim((385.5, 386.7))
    plt.xlim((0,15))
    plt.xlabel('Number of points')
    plt.ylabel('Height (m)')
    plt.title('Number of points in arbitrary grid cell, iteration {}'.format(i+1))
    plt.savefig('hist{}.png'.format(i))


