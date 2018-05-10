import pytest
import random_forest as rf
from glob import glob
import numpy as np
from skimage import io
import np_segment as nps


print(rf.DIRECTORY)
LIST_OF_TXT_FILES = glob(rf.DIRECTORY+'/text_files/*.txt')
LIST_OF_IMAGE_FILES = glob(rf.DIRECTORY+'/images/*.png')
SAMPLE_IMAGE_FILE = LIST_OF_IMAGE_FILES[0]
SAMPLE_TXT_FILE = LIST_OF_TXT_FILES[0]
SAMPLE_IMAGE = io.imread(SAMPLE_IMAGE_FILE,as_grey=True)


#Tests for random_forest.py

def test_rf_label_reader():
    """Tests the outputs of the rf_label_reader function to ensure that it
    generates teh same number of labels and image cuts and that it has
    actually generated some result by checking the that the total label
    count is greater than zero."""
    labels, image_cuts, empty_count, null_count, no_count, yes_count = \
    rf.rf_label_reader(SAMPLE_TXT_FILE,SAMPLE_IMAGE_FILE)
    assert len(labels) == np.asanyarray(image_cuts).shape[0]
    assert empty_count + null_count + no_count + yes_count > 0

def test_rf_data_pipeline():
    """Test the rf_data_pipeline function by making sure that the function
    creates a dataframe containing data and that labels have been created."""
    df, totals = rf.rf_data_pipeline(rf.DIRECTORY)
    assert df.shape[0] > 0
    assert np.sum(totals) > 0

def test_sobel_edges():
    """Test feature function making a histogram of sobel edges by making sure
    the array output has the right length and is not all zeros."""
    edge_hist = rf.sobel_edges(SAMPLE_IMAGE[:256,:256])
    assert edge_hist.shape[0] == 50
    assert np.all(np.asarray(edge_hist,dtype=int) == 0) == False

def test_blobs_log():
    """Test that correct array length for blobs_log function."""
    blob_info = rf.blobs_log(SAMPLE_IMAGE[:256,:256])
    assert blob_info.shape[0] == 2

def test_fft_hist():
    """Tests fft_hist by checking length of array and that output is not
    all zeros"""
    ffthist = rf.fft_hist(SAMPLE_IMAGE)
    assert ffthist.shape[0] == 20
    assert np.all(ffthist == 0) == False

def test_lbp_cut():
    """Tests lbp_cut by checking length of array and that output is not
    all zeros"""
    lbpcut = rf.lbp_cut(SAMPLE_IMAGE[:256,:256])
    assert lbpcut.shape[0] == 400
    assert np.all(np.asarray(lbpcut,dtype=int) == 0) == False

def test_gray_range():
    """Tests gray_range by checking length of array and that output is not
    all zeros or all ones"""
    irange = rf.gray_range(SAMPLE_IMAGE[:256,:256])
    assert irange.shape[0] == 2
    assert np.all(irange == 0) == False
    assert np.all(irange == 1) == False

def test_get_features():
    df, totals = rf.rf_data_pipeline(rf.DIRECTORY)
    print(df['filename'].iloc[0],df['label'].iloc[0])
    print(df.shape)
    features = rf.get_features(df['filename'].iloc[0],df['label'].iloc[0])
    assert features[0].shape[0] == 874
    assert isinstance(features[1],str)

def test_run_sfft():
    amap = nps.run_sfft(SAMPLE_IMAGE)
    assert amap.shape[2] == 3

def test_sfft_filter():
    amap = nps.run_sfft(SAMPLE_IMAGE)
    bin_image = nps.sfft_filter(amap)
    assert bin_image.shape == (1024,1024)
    assert int(bin_image.max()) == 1
    assert int(bin_image.min()) == 0
