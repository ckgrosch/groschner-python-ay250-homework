from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import io

def imm(image):
    """function to display a large grayscale image"""
    fig, ax = plt.subplots(figsize=(10,10))
    ax.imshow(image, cmap = 'gray')
    ax.axis('off')

def check_label(labels,images,idx,alpha = 0.25):
    """Takes in skimage ImageCollections for labels and original images and an index for an image
    to show the overlay of the created label mask and original image"""
    pic = alpha*np.reshape(labels[idx][:,:,0],(1024,1024)) + (1-alpha)*np.reshape(images[idx][:,:,0],(1024,1024))
    imm(pic)
