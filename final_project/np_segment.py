from skimage import morphology
from skimage import filters
from skimage import segmentation
from skimage import transform
from skimage.feature import blob_dog
from glob import glob
from sfft import *

def run_sfft(raw_image):
    """Function to run slidding FFT on an image. Outputs an abundance map of shape (m,n,p,3)"""
    num_of_comp = 3
    hamming_filter = 1
    FFT_zoom_factor = 1
    interpol_factor = 1
    window_size = 64
    window_step = 16
    pos_mat = GenerateXYPos(window_size, window_step, raw_image.shape[0]) #Generate matrix with (x,y) locations of window position
    FFT_mat4 = Do_Sliding_FFT(raw_image,pos_mat,window_size,interpol_factor,FFT_zoom_factor,hamming_filter) #Do the Sliding FFT
    FFT_mat5 = FFT_mat4.reshape(int(np.sqrt(FFT_mat4.shape[0])),
                                        int(np.sqrt(FFT_mat4.shape[0])),
                                        int(window_size*interpol_factor/FFT_zoom_factor),
                                        int(window_size*interpol_factor/FFT_zoom_factor))


    amap = analyze_endmembers(FFT_mat5, num_of_comp)
    return amap

def sfft_filter(sfft,upper = 0.87,lower = 0.1):
    """Function to threshold and apply morphological functions to an accumulation map of an image after going
    through slidding fourier filtering. Returns a binary image or shape (1024,1024). The variables upper and lower
    refer to thresholds for determining regions that should be included as particle regions from the
    accumulation map"""
    thres1 = filters.threshold_otsu(sfft[:,:,1])
    thres2 = filters.threshold_otsu(sfft[:,:,2])
    if thres1 < thres2:
        image = np.flipud(np.rot90(sfft[:,:,1]))
    else:
        image = np.flipud(np.rot90(sfft[:,:,2]))
    image[image>upper] =1
    image[image<lower] = 1
    image[image!=1] = 0
    image = segmentation.clear_border(morphology.dilation(morphology.erosion(morphology.closing(image))))
    image = transform.resize(image,(1024,1024))
    return image

def segmentation_pipeline(directory,start = 0,number_images =10,upper = 0.87,lower = 0.1):
    """Wrapper function to go through a file of atomic resolution images of nanoparticles and segement out regions
    which contain nanoparticles. Section of a directory of images can be indicated by start and number of images
    both integers.The variables upper and lower refer to thresholds for determining regions
    that should be included as particle regions from the accumulation map."""
    if os.path.isdir(directory+'/images/') == False:
        raise \
        RuntimeError('Current directory must have images placed in a directory labeled images')
    image_file_list = glob(directory+'/images/*.png')[start:start+number_images]
    if len(image_file_list) == 0:
        raise RuntimeError('No images found. All images must be in png format')
    image_new_directory = directory + '/segmented_images/'
    if os.path.isdir(image_new_directory) != True:
        os.mkdir(image_new_directory)
    image_name_list = [name.split('/')[-1].split('.')[0] for name in image_file_list]
    blob_dict = {}
    for idx, image_file in enumerate(image_file_list):
        image = io.imread(image_file,as_grey=True)
        if image.shape != (1024,1024):
            raise \
            RuntimeError('Images are not of shape (1024,1024) please resize and try again.\
                         File causing error {}'.format(image_name_list[idx]))
        sfft = run_sfft(image)
        binary_image = sfft_filter(sfft,upper,lower)
        blobs = blob_dog(binary_image, max_sigma=60, min_sigma=50, threshold=.5)
        blobs[:, 2] = blobs[:, 2] * np.sqrt(2)
        blob_dict[image_name_list[idx]] = blobs
        for idx2, blob in enumerate(blobs):
            x = int(blob[0])
            y = int(blob[1])
            r = int(blob[2])
            if x - r < 0 or y - r < 0:
                pass
            elif x+r > 1023 or y+r > 1023:
                pass
            else:
                plt.imsave(image_new_directory+image_name_list[idx]+'_'+str(idx2),image[x-r:x+r,y-r:y+r],cmap = 'gray')
    return blob_dict
