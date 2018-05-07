from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import os
from ast import literal_eval
import shutil

def txt_reader(file):
    txt_info = open(file,'r')
    txt = []
    centers = []
    radii = []
    for line in txt_info:
        if line == '\n':
            pass
        else:
            line = line.strip('\n')
            txt.append(line)
    center_stop = txt.index('Radius Size:')
    radius_stop = txt.index('Defect Label:')
    for loc in txt[1:center_stop]:
        centers.append(literal_eval(loc))
    for loc in txt[center_stop+1:radius_stop] :
        radii.append(int(loc))
    image_size = literal_eval(txt[-1])
    return centers, radii, image_size


def spot_maker(location, radius, label_mask):
    for x in np.arange(location[0]-radius,location[0]+radius,1):
        for y in np.arange(location[1]-radius,location[1]+radius,1):
            dx = x - location[0]
            dy = y - location[1]
            if np.sqrt((dx**2+dy**2)) <= radius \
            and int(x) < label_mask.shape[0] and int(y) < label_mask.shape[1]:
                label_mask[int(y),int(x)] = 1
    return label_mask

def mask_maker(file):
    centers, radii, image_size = txt_reader(file)
    label_mask = np.zeros(image_size)
    for idx,radius in enumerate(radii):
        label_mask = spot_maker(centers[idx],radius,label_mask)
    return label_mask

def mask_pipeline(directory):
    file_list = glob(directory+'/text_files/*.txt')
    name_list = [name.split('/')[-1].split('.')[0] for name in file_list]
    for idx, file in enumerate(file_list):
        if len(open(file,'r').readlines()) == 0:
            pass
        else:
            label_mask = mask_maker(file)
            plt.imsave(directory+'/labels/'+name_list[idx]+'.png',label_mask, cmap='gray')
        shutil.move(file,directory+'/old_text_files/')
    print('done!')
