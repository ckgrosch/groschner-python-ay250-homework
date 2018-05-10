# CODE FROM Roma Vasudevan for sliding FFT
# work presented here: https://aip.scitation.org/doi/abs/10.1063/1.4914016
#I claim none of the functions in this cell to be my own, though they did need
#revision to work in this use case. However, I only adapted them from his
#original code and I do not present any of the functions below to be part of my
#project beyond a being a necessary preprocessing step to try to segment images

import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import io
from scipy import fftpack
from scipy import ndimage
from pysptools.eea import nfindr
import pysptools.abundance_maps as amp
#import eea
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn import decomposition
from sklearn.decomposition import NMF


def ApplyHamming(imgsrc,window_size):
    #Applies a Hamming window to the input imgsec
    bw2d = np.outer(np.hamming(window_size), np.ones(window_size))
    bw2d = np.sqrt(bw2d * bw2d.T)
    imgsrc *= bw2d
    return imgsrc

def MakeWindow(imgsrc, xpos, ypos,window_size):
    #Returns the portion of the image within the window given the
    #image (imgsrc), the xposition and the yposition
    imgsrc = imgsrc[xpos:xpos+window_size, ypos:ypos+window_size]
    return imgsrc

def GenerateXYPos(window_size, window_step, image_width):
    #Generates the (x,y) pairs given the window size, window step and image width (=height)
    xpos_vec = np.arange(0,image_width-window_size,window_step)
    ypos_vec = np.arange(0,image_width-window_size,window_step)
    num_steps = len(xpos_vec)
    xpos_mat = np.tile(xpos_vec, num_steps)
    ypos_mat = np.repeat(ypos_vec, num_steps)
    pos_mat = np.column_stack((xpos_mat, ypos_mat))

    return pos_mat

def zoom_interpol(FFT_image,window_size,FFT_zoom_factor, interpol_factor):
    #Accepts an image, returns zoomed image
    zoom_size = (FFT_image.shape[0]/FFT_zoom_factor)/2
    if np.mod(FFT_image.shape[0]/FFT_zoom_factor,2)==0:
        F2_zoomed= FFT_image[int(window_size/2 - zoom_size):int(window_size/2 + zoom_size),
                             int(window_size/2 - zoom_size):int(window_size/2 +zoom_size)]
    else:
        F2_zoomed= FFT_image[int(window_size/2 - zoom_size):int(window_size/2+1 + zoom_size),
                             int(window_size/2 - zoom_size):int(window_size/2 + 1+zoom_size)]

    return ndimage.zoom(F2_zoomed,interpol_factor)

def Do_Sliding_FFT(raw_image,pos_mat,window_size,interpol_factor,FFT_zoom_factor,hamming_filter):
    #Carries out the FFT
    FFT_mat4 = np.zeros(shape = (len(pos_mat),
                                 int(window_size*interpol_factor/FFT_zoom_factor),
                                 int(window_size*interpol_factor/FFT_zoom_factor)))

    for i in np.arange(0,len(pos_mat)):

        img_window = MakeWindow(raw_image, pos_mat[i,0], pos_mat[i,1],window_size) #Generate the window on which FFT is performed

        #Pass the x and y positions of the top-left corner of the FFT window
        #These positions are located in pos_mat

        if hamming_filter ==1: #Apply filter if requested
            img_window_filtered = ApplyHamming(np.copy(img_window),window_size)
        else:
            img_window_filtered = (np.copy(img_window))

        # Take the fourier transform of the image.
        F1 = fftpack.fft2((img_window_filtered))

        # Now shift so that low spatial frequencies are in the center.
        F2 = (fftpack.fftshift((F1)))

        final_FFT = zoom_interpol(np.abs(F2),window_size,FFT_zoom_factor,interpol_factor)

        FFT_mat4[i,:,:,] = final_FFT

    return FFT_mat4


def analyze_endmembers(FFT_mat, num_comp):
    q = FFT_mat.shape
    a = q[0]
    b = q[1]
    c = q[2]
    d = q[3]

    data_mat3 = np.abs(FFT_mat.reshape((a*b, c*d)))

    nnls = amp.NNLS()
    a1 = nfindr.NFINDR(data_mat3, num_comp) #Find endmembers
    endmembers = a1[0]

    data_mat3 = data_mat3.reshape((a,b, c*d))
    amap = nnls.map(data_mat3, endmembers) #Find abundances

    return amap
