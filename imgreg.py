#!usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 11:40:45 2016
@author: csheng (shengcaibin@gmail.com)
Loewer lab, TU Darmstadt
"""

import os, glob, multiprocessing
from PIL import Image
import numpy as np
import humansort as hs
from scipy import signal
from math import floor

def align(Dir,TimePoint,Posperplate,Positions):
    
    # assign global variables
    global num_plates, mydir, time_point, pos_per_plate, pos
    
    mydir = Dir + os.sep;
    time_point = TimePoint;
    pos_per_plate = Posperplate;
    pos = Positions;
    num_plates = int(pos/pos_per_plate);
    
    offset_parallel() # parallel process to get offset
    align_parallel()  # parallel process to align images 

def offset_parallel():
    """multiprocessing to get offset for images"""
    # create a pool    
    pool = multiprocessing.Pool(multiprocessing.cpu_count()); # restrict the cpu number here if needed
    tasks = [];
    plateID = 0;
    
    # the relative shifting of positions for a given plate should be constant, so take the first position to
    # compute the offset
    while plateID < num_plates:
        tasks.append((plateID*pos_per_plate+1,plateID))
        print('task '+'P'+("%02d"%(plateID*pos_per_plate+1))+' added')
        plateID += 1
    
    # run parallel process
    for t in tasks:
        pool.apply_async(get_multi_offset,(t[0],t[1]))
    pool.close()
    pool.join()
    print('Offset computation finished!!!')
    print('OffSet_Pos files saved in '+os.path.join(mydir,'Offset/'))
    pool.terminate()


def get_multi_offset(firstPos_of_plate,plateID):
    """get the offsets for each plate using it’s first position and save them in separate csv files"""

    off_set = get_single_offset(firstPos_of_plate)
    Offsetpath = os.path.join(mydir,'Offset/')
    if not os.path.exists(Offsetpath):
        os.makedirs(Offsetpath)
    np.savetxt(os.path.join(Offsetpath,'OffSet_Pos'+("%02d"%(plateID*pos_per_plate+1))+'.csv'), off_set, delimiter=',', fmt='%d')


def get_single_offset(firstPos_of_plate):
    """get the offsets for a given position and save them in a csv file"""
    
    files = glob.glob(mydir+'mov*/calibrated/P'+("%02d"%firstPos_of_plate)+'/*.TIF')
    hs.sort_nicely(files) # sort the files according to the number order
     
    # get the constant parameters
    Im0 = Image.open(files[0])
    width,height = Im0.size
    im1 = np.zeros(shape=(time_point,height,width),dtype='int')
    im2 = np.zeros(shape=(time_point,height,width),dtype='int')
    Center =  np.zeros(shape=(time_point,2),dtype='int')
    shift =  np.zeros(shape=(time_point,2),dtype='int')
    Center[0] =int(height/2),int(width/2)
    offset =  np.zeros(shape=(time_point,4),dtype='int')
     
     # calculate the offset between image(T) and image(T+1)
    for i in range(0,time_point-1):
        im1 = Image.open(files[i])
        im1 = im1-np.mean(im1)
         
        im2 = Image.open(files[i+1])
        im2 = im2-np.mean(im2)
         
        a = signal.fftconvolve(im1,im2[::-1,::-1],mode='same')
        Center[i+1] = np.unravel_index(np.argmax(a), a.shape)
        shift[i+1] = Center[i+1]-Center[0]+shift[i]
        print(files[i] + ' relatively shift '+str(Center[i+1]-Center[0]))
     
    shift_max = np.amax(shift,axis = 0)
    shift_min = np.amin(shift,axis = 0)
    offset[0] = (shift_max[1],shift_max[0],width+shift_min[1],height+shift_min[0])
    for i in range(1,time_point):      
        offset[i] = offset[0]-[shift[i,1],shift[i,0],shift[i,1],shift[i,0]]
    return offset


def align_parallel():
    """multiprocessing to align the images"""
    
    import csv
    align_tasks = [];
    
    # check if separate movies are put in proper directories and create folders for final cropped images
    for foldername1 in os.listdir(mydir):
        if foldername1 in ('mov0','mov1','mov2','mov3','mov4','mov5','mov6','mov7'):
       # Check if the 4 folders exist
           for foldername in os.listdir(os.path.join(mydir,foldername1)):
             if foldername in ('phase','calibrated','calibrate2', 'calibrate3'):
                    path_of_files = os.path.join(mydir,foldername);
                    print(path_of_files)
                    if not os.path.exists(path_of_files):
                        os.makedirs(path_of_files)

    # read offset from offset files and add them to mutiple align tasks  
    for position in range(1,pos+1):
        with open(os.path.join(mydir,'Offset','OffSet_Pos'+("%02d"%(floor((position-1)/pos_per_plate)*pos_per_plate+1)))+'.csv', newline='') as f:
            reader = csv.reader(f)
            offset =[]
            for row in reader:
                offset.append((int(row[0]),int(row[1]),int(row[2]),int(row[3])))    
        f.close()
      
        for foldername in os.listdir(mydir):
            if foldername in ('phase','calibrated','calibrate2', 'calibrate3'):
                filespath = os.path.join(mydir,'mov*',foldername,'P'+("%02d"%(position)))
                newdir = os.path.join(mydir,foldername,'P'+("%02d"%(position)))
                if not os.path.exists(newdir):
                    os.makedirs(newdir)
                files = glob.glob('%s/*.TIF'%filespath)
                hs.sort_nicely(files)

                for i in range(1,time_point+1):
                    img =  files[i-1]
                    newimg = newdir + '/' + foldername+'-P'+ ("%02d"%(position))+'.'+("%03d"%(i))+'.TIF'
                    cropimg = offset[i-1]           
                    align_tasks.append((img,newimg,cropimg))
                    align_tasks.append((img,newimg,cropimg))
            print('Task '+img+' added')
    
    # run parallel processing      
    pool1 = multiprocessing.Pool(multiprocessing.cpu_count())
    for t in align_tasks:
        pool1.apply_async(align_single_img,(t[0],t[1],t[2]))
    pool1.close()
    pool1.join()
    print (' A pool of workers has done')
    pool1.terminate()
     
def align_single_img(old_img,new_img,offset):
    """crop a single image (old_img) and save it as new_img"""
    img = Image.open(old_img)     
    cropimg = img.crop(offset)
    cropimg.save(new_img)
    print (new_img + '  cropped and saved!')