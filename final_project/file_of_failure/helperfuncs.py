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

def image_slice(directory, im_lbl):
    """used to break up the 1024x1024 images into 512x512 segments takes a
     diretory and string specifying whether it is slicing 'image' or  'label'"""
    if im_lbl == 'image':
        file_list = glob(directory+'/images/*.png')
        new_directory = directory + '/sliced_images/'
    elif im_lbl == 'label':
        file_list = glob(directory+'/labels/*.png')
        new_directory = directory + '/sliced_labels/'
    name_list = [name.split('/')[-1].split('.')[0] for name in file_list]
    for idx, file in enumerate(file_list):
        image2split = plt.imread(file)
        image1 = image2split[:512,:512,:]
        plt.imsave(new_directory+name_list[idx]+'_a.png',image1, cmap='gray')
        image1 = image2split[512:,:512,:]
        plt.imsave(new_directory+name_list[idx]+'_b.png',image1, cmap='gray')
        image1 = image2split[:512,512:,:]
        plt.imsave(new_directory+name_list[idx]+'_c.png',image1, cmap='gray')
        image1 = image2split[512:,512:,:]
        plt.imsave(new_directory+name_list[idx]+'_d.png',image1, cmap='gray')
    print('done!')

def image_slice_small(directory):
    """Used to break up the 1024x1024 images into 64x64 segments takes a
     diretory that is the source. This is only for creating training
     dataset. Throws out regions of the masks and images with no identified
     particles so that training set will have better balance of positive and
     negative pixels."""
    image_file_list = glob(directory+'/images/*.png')
    image_new_directory = directory + '/small_sliced_images/'
    if os.path.isdir(image_new_directory) != True:
        os.mkdir(image_new_directory)
    label_file_list = glob(directory+'/labels/*.png')
    label_new_directory = directory + '/small_sliced_labels/'
    if os.path.isdir(label_new_directory) != True:
        os.mkdir(label_new_directory)
    image_name_list = [name.split('/')[-1].split('.')[0] for name in image_file_list]
    label_name_list = [name.split('/')[-1].split('.')[0] for name in label_file_list]
    if len(image_name_list) != len(label_name_list):
        raise RuntimeError('different number of images and labels')
    if image_name_list != label_name_list:
        raise RuntimeError('images and labels did not match')
    for idx, file in enumerate(image_file_list):
        image2split = io.imread(file, as_grey=True)
        label2split = io.imread(label_file_list[idx], as_grey=True)
        for x in range(0,15*64,64):
            for y in range(0,15*64,64):
                image = image2split[x:x+64,y:y+64]
                label = label2split[x:x+64,y:y+64]
                if np.any(np.isin([1],label)) == False:
                    pass
                else:
                    image_name = image_name_list[idx]+ '_' + str(x)+ str(y) + '.png'
                    label_name = image_name_list[idx]+ '_' + str(x)+ str(y) + '.png'
                    plt.imsave(image_new_directory+image_name,image, cmap='gray')
                    plt.imsave(label_new_directory+label_name,label, cmap='gray')
    print('done!')

def slicing_for_assembley(directory):
    """Used to break up the 1024x1024 images into 64x64 segments takes a
     diretory that is the source. Same process as image_slice_small but all
     regions are saved so that regions can be stitched back together"""
    image_file_list = glob(directory+'/images/*.png')
    image_new_directory = directory + '/small_sliced_images_asmbl/'
    if os.path.isdir(image_new_directory) != True:
        os.mkdir(image_new_directory)
    label_file_list = glob(directory+'/labels/*.png')
    label_new_directory = directory + '/small_sliced_labels_asmbl/'
    if os.path.isdir(label_new_directory) != True:
        os.mkdir(label_new_directory)
    image_name_list = [name.split('/')[-1].split('.')[0] for name in image_file_list]
    label_name_list = [name.split('/')[-1].split('.')[0] for name in label_file_list]
    if len(image_name_list) != len(label_name_list):
        raise RuntimeError('different number of images and labels')
    if image_name_list != label_name_list:
        raise RuntimeError('images and labels did not match')
    for idx, file in enumerate(image_file_list):
        image2split = io.imread(file, as_grey=True)
        label2split = io.imread(label_file_list[idx], as_grey=True)
        for x in range(0,16*64,64):
            for y in range(0,16*64,64):
                image = image2split[x:x+64,y:y+64]
                label = label2split[x:x+64,y:y+64]
                image_name = image_name_list[idx]+ '-' + str(x)+ '-' + str(y) + '.png'
                if x != 64 and y != 64:
                    label_name = image_name_list[idx]+ '-' + str(x)+ '-' + str(y) + '.png'
                elif x != 64 and y == 64:
                    label_name = image_name_list[idx]+ '-' + str(x)+ '-' + str(0) +str(y) + '.png'
                elif x == 64 and y != 64:
                    label_name = image_name_list[idx]+ '-' +str(0)+str(x)+ '-' +str(y) + '.png'
                elif x == 64 and y == 64:
                    label_name = image_name_list[idx]+ '-' + str(0)+ str(x)+ '-' + str(0) +str(y) + '.png'
                plt.imsave(image_new_directory+image_name,image, cmap='gray')
                plt.imsave(label_new_directory+label_name,label, cmap='gray')
    print('done!')

def reassemble_slices(directory):
    label_file_list = glob(directory+'/small_sliced_labels/*.png')
    label_file_list.append('end')
    previous_label = label_file_list[0].split('/')[-1].split('-')[0]
    previous_x = 'start'
#     previous_y = label_file_list[0].split('/')[-1].split('-')[2].split('.')[0]
    img_row = np.zeros((64,64))
    image = np.zeros((64,64))
    label_dict = {}
    for label in label_file_list:
        original_label = label.split('/')[-1].split('-')[0]
        if label != 'end':
            sub_img = io.imread(label, as_grey=True)
            sub_x = label.split('/')[-1].split('-')[1]
            sub_y = label.split('/')[-1].split('-')[2].split('.')[0]
        if original_label == previous_label:
            if previous_x == 'start':
                img_row = sub_img
                previous_x = sub_x
            elif sub_x == str(0) and previous_x == sub_x:
                img_row = np.concatenate((img_row,sub_img),axis =1)
                previous_x = sub_x
            elif previous_x != sub_x and previous_x == str(0):
                image = img_row
                img_row = sub_img
                previous_x = sub_x
            elif sub_x != str(0) and previous_x == sub_x:
                img_row = np.concatenate((img_row,sub_img),axis =1)
                previous_x = sub_x
            elif previous_x != sub_x and previous_x != str(0) and previous_x != 'start':
                image = np.concatenate((image,img_row),axis =0)
                img_row = sub_img
                previous_x = sub_x
        else:
            image = np.concatenate((image,img_row),axis =0)
            label_dict[previous_label] = image
            previous_label = original_label
            image = np.zeros((64,64))
            img_row = sub_img
            previous_x = sub_x
        previous_label = original_label
    if os.path.isdir(directory+'/reconstructed_images') == False:
        new_directory = directory+'/reconstructed_images'
        os.mkdir(new_directory)
    else:
        new_directory = directory+'/reconstructed_images'
    for key in label_dict:
        plt.imsave(new_directory+'/'+key+'.png',label_dict[key],cmap = 'gray')
    print('done!')
