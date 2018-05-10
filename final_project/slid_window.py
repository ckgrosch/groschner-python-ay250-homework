from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import io
import numpy as np

def sliding_image_slice(directory,image_name = None):
    """used to break up the 1024x1024 images into 128x128 segments.
    Can specify a specific image by giving filename of image"""
    if image_name == None:
      file_list = glob(directory+'/images/*.png')
    else:
      file_name = directory+'/images/'+image_name
      file_list = glob(file_name)
    new_directory = directory + '/slid_window_images/'
    if os.path.isdir(new_directory) == False:
        os.mkdir(new_directory)
    name_list = [name.split('/')[-1].split('.')[0] for name in file_list]
    for idx, file in enumerate(file_list):
        image2split = io.imread(file,as_grey=True)
        for idx2, x in enumerate(np.arange(0,896,64)):
            for idx3, y in enumerate(np.arange(0,896,64)):
                image = image2split[x:x+128,y:y+128]
                fname = new_directory+name_list[idx]+'_'+str(x)+'_'+str(y)+'.png'
                plt.imsave(fname,image, cmap='gray')
    print('done!')
