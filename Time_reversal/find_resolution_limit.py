import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
from numba import jit
import time

def plot_image_stack():
    for i in range(z):
        plt.imshow(stack[:,:,i],vmin=np.amin(stack),vmax=np.amax(stack))
        plt.colorbar()
        plt.show(block=False)
        plt.pause(0.1)
        plt.clf()
        plt.cla()
    print(path)
    plt.plot(stack[x//2,:,z//2])
    plt.show(block=False)
    plt.pause(0.01)
    plt.clf()
    plt.cla()

# @jit(nopython=True)
def find_middle_minima(line,extremum,idx):
    minima = extremum[(idx[0]+idx[1])//2]

    minima_idx = np.where(line==minima)[0][0]
    area = line[minima_idx-5:minima_idx+5]
    minima = np.amin(area)
    idx = np.where(line==minima)[0][0]

    return minima,idx

# @jit(nopython=True)
def find_exact_maxima(line,point):
    idx = np.where(line==point)[0][0]
    area = line[idx-5:idx+5]
    maxima = np.amax(area)
    idx = np.where(line==maxima)[0][0]

    return maxima,idx

# @jit(nopython=True)
def find_extremum(line):
    derivative = line[1:]-line[:-1]
    zero_crossing = np.where(np.diff(np.sign(derivative)))[0]
    extremum = line[zero_crossing]
    tmp = np.sort(extremum)[-2:]
    idx_1 = np.where(tmp[0]==extremum)[0][0]
    idx_2 = np.where(tmp[1]==extremum)[0][0]
    idx = np.array([idx_1,idx_2])
    top_two_extrema = extremum[idx]

    maxima = []
    maxima_idx = []
    for element in top_two_extrema:
        tmp = find_exact_maxima(line,element)
        maxima.append(tmp[0])
        maxima_idx.append(tmp[1])

    minima,minima_idx = find_middle_minima(line,extremum,idx)

    return maxima,maxima_idx,minima,minima_idx

def find_direcories():
    directory = os.listdir('C:\python\Master (Fishbowl)\class_time_reversal\images')
    paths = []
    for dir in directory:
        if dir != "Single dipole":
            subdirectory = os.listdir('C:\python\Master (Fishbowl)\class_time_reversal\images/'+dir)
            for subdir in subdirectory:
                subsubdirectory = os.listdir('C:\python\Master (Fishbowl)\class_time_reversal\images/'+dir+'/'+subdir)
                for subsubdir in subsubdirectory:

                    paths.append('C:\python\Master (Fishbowl)\class_time_reversal\images/'+dir+'/'+subdir+'/'+subsubdir)

                    # element = os.listdir('images/'+dir+'/'+subdir+'/'+subsubdir)
                    # for ele in element:
                    #     if not ".tiff" in ele:
                    #         paths.append('images/'+dir+'/'+subdir+'/'+subsubdir+'/'+ele)

    return paths

def find_resolution_limit(paths,plot_extrema=False):
    f = open("resolution.txt", "w+")
    for path in paths:
        elements = os.listdir(path)
        elements = [el for el in elements if not ".tiff" in el]
        for element in elements:
            file = os.listdir(path+'/'+element)
            z = len(file)
            x,y = np.array(Image.open(path+'/'+element+'/'+file[0])).shape

            stack = np.zeros((x,y,z))
            for i in range(z):
                stack[:,:,i] = Image.open(path+'/'+element+'/'+'{}.tiff'.format(i))

            line = stack[np.where(stack==np.amax(stack))[0][0],:,z//2]
            maxima, maxima_idx, minima, minima_idx = find_extremum(line)

            if 0.8 <= maxima[0]/maxima[1] <= 1.2:
                background = np.amin(line)
                diff = ((minima-background)/(np.amin(maxima)-background))
                if diff <= 0.735:
                    if plot_extrema == True:
                        plt.plot(line)
                        plt.plot(maxima_idx,maxima,'*',c='g')
                        plt.plot(minima_idx,minima,'*',c='r')
                        plt.show()
                    f.write(path+'/'+element+' ')
                    f.write(str(diff)+'\n')
                    print(path+'/'+element+' '+str(diff))
                    break

            else:
                continue



paths = find_direcories()
find_resolution_limit(paths)