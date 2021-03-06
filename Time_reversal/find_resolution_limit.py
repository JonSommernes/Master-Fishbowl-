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

def find_direcories(path):
    # directory = os.listdir('C:/Python/Master (Fishbowl)/Images')
    directory = os.listdir(path)
    paths = []
    for dir in directory:
        if dir != "Single dipole":
            subdirectory = os.listdir(path+'/'+dir)
            for subdir in subdirectory:
                subsubdirectory = os.listdir(path+'/'+dir+'/'+subdir)
                for subsubdir in subsubdirectory:
                    paths.append(path+'/'+dir+'/'+subdir+'/'+subsubdir)
                    # element = os.listdir(path+'/'+dir+'/'+subdir+'/'+subsubdir)
                    # for ele in element:
                    #     if not ".tiff" in ele:
                    #         paths.append(path+'/'+dir+'/'+subdir+'/'+subsubdir+'/'+ele)

    return paths

def find_resolution_limit(paths,plot_extrema=False):
    f = open("resolution.txt", "w+")
    dists = []
    sensors = []
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
                    x_1 = float(element.split('_')[0].split(' ')[0].replace('[',''))
                    x_2 = float(element.split('_')[2].split(' ')[0].replace('[',''))
                    y_1 = float(element.split('_')[0].split(' ')[1])
                    y_2 = float(element.split('_')[2].split(' ')[1])
                    z_1 = float(element.split('_')[0].split(' ')[2].replace(']',''))
                    z_2 = float(element.split('_')[2].split(' ')[2].replace(']',''))
                    dist = np.sqrt((x_2-x_1)**2 + (y_2-y_1)**2 + (z_2-z_1)**2)
                    dists.append(dist)
                    sensors.append(path.split('_')[-2])
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

# def plot_resolution_limit(file):
#     f = open(file, "r")
#     sensors = [100,200,400,600,800]
#     rayleigh = []
#     dist = []
#     for line in f:
#         words = []
#         for word in line.split("/"):
#             words.append(word)
#
#         pos_1 = words[-1].split("__")[0].split(" ")
#         pos_1[0] = pos_1[0].replace('[',' ')
#         pos_1[-1] = pos_1[-1].replace(']',' ')
#
#         pos_2 = words[-1].split("__")[-1].split(" ")[0:3]
#         pos_2[0] = pos_2[0].replace('[',' ')
#         pos_2[-1] = pos_2[-1].replace(']',' ')
#
#         x_1,y_1,z_1 = float(pos_1[0]), float(pos_1[1]), float(pos_1[2])
#         x_2, y_2, z_2 = float(pos_2[0]), float(pos_2[1]), float(pos_2[2])
#         d = np.sqrt((x_2-x_1)**2 + (z_2-z_1)**2 + (z_2-z_1)**2)
#         dist.append(d)
#
#     print(sensors)
#     print(dist)
#     exit()
#
#     plt.plot(sensors,dist)
#     plt.show()

def plot_resolution_limit():
    dists = []
    paths = []
    sensors = []
    f = open("resolution.txt", "r")
    for element in f:
        pos = element.split('/')[-1]
        x_1 = float(pos.split(' ')[0].replace('[',''))
        y_1 = float(pos.split(' ')[1])
        z_1 = float(pos.split(' ')[2].split('_')[0].replace(']',''))
        x_2 = float(pos.split(' ')[2].split('_')[-1].replace('[',''))
        y_2 = float(pos.split(' ')[3])
        z_2 = float(pos.split(' ')[4].replace(']',''))

        dist = np.sqrt((x_2-x_1)**2+(y_2-y_1)**2+(z_2-z_1)**2)
        dists.append(dist)

        sensors.append(int(element.split('/')[-2].split('_')[-2]))

        paths.append(element.split('/')[4])

    parallel_odd = []
    parallel_odd_sen = []
    parallel_even = []
    parallel_even_sen = []
    orthogonal_odd = []
    orthogonal_odd_sen = []
    orthogonal_even = []
    orthogonal_even_sen = []
    for i,dist in enumerate(dists):
        if paths[i] == "Orthogonal_dipoles":
            if sensors[i]%2 == 0:
                orthogonal_even.append(dist)
                orthogonal_even_sen.append(sensors[i])
            else:
                orthogonal_odd.append(dist)
                orthogonal_odd_sen.append(sensors[i])
        else:
            if sensors[i]%2 == 0:
                parallel_even.append(dist)
                parallel_even_sen.append(sensors[i])
            else:
                parallel_odd.append(dist)
                parallel_odd_sen.append(sensors[i])


    orthogonal_even_sen, orthogonal_even = zip(*sorted(zip(orthogonal_even_sen, orthogonal_even)))
    orthogonal_even_sen = orthogonal_even_sen[:1]+orthogonal_even_sen[2:]
    orthogonal_even = orthogonal_even[:1]+orthogonal_even[2:]
    orthogonal_odd_sen, orthogonal_odd = zip(*sorted(zip(orthogonal_odd_sen, orthogonal_odd)))
    parallel_even_sen, parallel_even = zip(*sorted(zip(parallel_even_sen, parallel_even)))
    parallel_odd_sen, parallel_odd = zip(*sorted(zip(parallel_odd_sen, parallel_odd)))


    plt.plot(orthogonal_even_sen,orthogonal_even,'b')
    plt.plot(orthogonal_odd_sen,orthogonal_odd,'r')
    plt.text(430, 0.63, 'Even number of sensors', fontsize=15,  color='black')
    plt.plot([410], [0.63007], 'o',c='b')
    plt.text(430, 0.6295, 'Odd number of sensors', fontsize=15,  color='black')
    plt.plot([410], [0.62957], 'o',c='r')
    plt.ylabel('Resolution limit [wavelengths]')
    plt.xlabel('Number of sensors')
    plt.savefig('resolution_orthogonal_dipoles')
    plt.clf()

    plt.plot(parallel_even_sen,parallel_even,'b')
    plt.plot(parallel_odd_sen,parallel_odd,'r')
    plt.text(430, 0.965, 'Even number of sensors', fontsize=15,  color='black')
    plt.plot([410], [0.96509], 'o',c='b')
    plt.text(430, 0.9645, 'Odd number of sensors', fontsize=15,  color='black')
    plt.plot([410], [0.96459], 'o',c='r')
    plt.ylabel('Resolution limit [wavelengths]')
    plt.xlabel('Number of sensors')
    plt.savefig('resolution_parallel_dipoles')

def plot_resolution_limit_wl():
    dists = []
    paths = []
    sensors = []
    f = open("resolution.txt", "r")
    for element in f:
        pos = element.split('/')[-1]
        x_1 = float(pos.split(' ')[0].replace('[',''))
        y_1 = float(pos.split(' ')[1])
        z_1 = float(pos.split(' ')[2].split('_')[0].replace(']',''))
        x_2 = float(pos.split(' ')[2].split('_')[-1].replace('[',''))
        y_2 = float(pos.split(' ')[3])
        z_2 = float(pos.split(' ')[4].replace(']',''))

        dist = np.sqrt((x_2-x_1)**2+(y_2-y_1)**2+(z_2-z_1)**2)
        dists.append(dist)

        sensors.append(int(element.split('/')[-2].split('_')[-2]))

        # paths.append(element.split('/')[4])



    plt.plot(dists,'b')
    plt.ylabel('Resolution limit [wavelengths]')
    plt.xlabel('Something')
    # plt.savefig('resolution_orthogonal_dipoles')
    # plt.clf()
    plt.show()


def find_reyleigh(path):
    dists = []
    reyleigh = []
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

        background = np.amin(line)
        diff = ((minima-background)/(np.amin(maxima)-background))
        reyleigh.append(diff)
        pos = element.split('/')[-1]
        x_1 = float(pos.split(' ')[0].replace('[',''))
        y_1 = float(pos.split(' ')[1])
        z_1 = float(pos.split(' ')[2].split('_')[0].replace(']',''))
        x_2 = float(pos.split(' ')[2].split('_')[-1].replace('[',''))
        y_2 = float(pos.split(' ')[3])
        z_2 = float(pos.split(' ')[4].replace(']',''))

        dist = np.sqrt((x_2-x_1)**2+(y_2-y_1)**2+(z_2-z_1)**2)
        dists.append(dist)

    plt.plot(dists[:30],reyleigh[:30])
    plt.axhline(0.735,c='r',ls=':')
    plt.xlabel('Distance [wavelengths]')
    plt.ylabel('Intensity difference')
    plt.savefig('rayleigh')



# paths = find_direcories("C:/Python/Master (Fishbowl)/Images")
# find_resolution_limit(paths)
plot_resolution_limit()
# find_reyleigh('C:/Python\Master (Fishbowl)/Images/Orthogonal_dipoles/Symmetric_around_0/2_dipoles__500_sensors')
