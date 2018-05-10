import numpy as np
import matplotlib.pyplot as plt
from skimage import io
import os
import skimage.feature
import skimage.filters
import pandas as pd
from pathlib import Path
from joblib import Parallel, delayed
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib
from sklearn import model_selection
import logging
from sklearn.metrics import confusion_matrix
import seaborn as sns
from glob import glob
import shutil
from ast import literal_eval

DIRECTORY = os.getcwd() + '/rf_data'

def rf_label_reader(txt_file, image_file):
    """Reads in text file and associated image file and using the information in the text file
    makes an array of labels and saves the associated region of the image corrsponding to that label
    to create training and testing data for random forest creation"""
    txt_info = open(txt_file,'r')
    image = io.imread(image_file, as_grey=True)
    #test for 1024x1024 image
    if image.shape != (1024,1024):
        raise RuntimeError('Image is not required shape: 1024x1024')

    #setup required variables
    txt = []
    centers = []
    radii = []
    labels = []
    image_cuts = []
    empty_count = 0 #how many image cuts generated with the label empty meaning no particle present
    null_count = 0 #how many image cuts generated with the label null meaning particle present but not atomic resolution
    no_count = 0 #how many image cuts generated with the label no meaning particle present, atomic res, no defect
    yes_count = 0 #how many image cuts generated with the label yes meaning particle present, atomic res, has defect

    #read text file
    for line in txt_info:
        if line == '\n':
            pass
        else:
            line = line.strip('\n')
            txt.append(line)
    center_stop = txt.index('Radius Size:')
    radius_stop = txt.index('Defect Label:')
    label_stop = txt.index('Image Size:')

    #create image and label pair
    if radius_stop - center_stop == 1: #ID if there are no particles present in text file
        for x in range(0,4*256,256):
            for y in range(0,4*256,256):
                image_slice = image[x:x+256,y:y+256]
                image_cuts.append(image_slice)
                labels.append('empty')
                empty_count += 1
    else:
        for loc in txt[1:center_stop]:
            centers.append(literal_eval(loc))
        for loc in txt[center_stop+1:radius_stop] :
            radii.append(int(loc))
        for loc in txt[radius_stop+1:label_stop] :
            labels.append(loc)
            if loc == 'null':
                null_count += 1
            if loc == 'no':
                no_count += 1
            if loc == 'yes':
                yes_count += 1
        for idx, center in enumerate(centers): #slice up image to create images to feed into
            x_min = center[0]-radii[idx]-2
            x_max = center[0]+radii[idx]+2
            y_min = center[1]-radii[idx]-2
            y_max = center[1]+radii[idx]+2
            if x_min < 0:
                x_min = 0
            if y_min < 0:
                y_min = 0
            if x_max > 1023:
                x_max = 1023
            if y_max > 1023:
                y_max = 1023
            image_slice = image[int(y_min):int(y_max), int(x_min):int(x_max)]
            image_cuts.append(image_slice)

    return labels, image_cuts, empty_count, null_count, no_count, yes_count

def rotate(df):
    """Function to rotate non-null images"""
    rot_dir = {'filename':[],'label':[]}
    for idx, label in enumerate(df['label']):
        if label == 'null':
            pass
        else:
            image = io.imread(df['filename'][idx])
            name = df['filename'][idx].split('.')[0]
            for count in np.arange(1,4):
                rot_img = np.rot90(image,count)
                rot_dir['filename'].append(name+'rot'+str(count)+'.png')
                rot_dir['label'].append(label)
                try:
                    plt.imsave(name+'rot'+str(count)+'.png',rot_img,cmap = 'gray')
                except:
                    pass
    df2 = pd.DataFrame(data = rot_dir)
    df = df.append(df2)
    print('Done!')
    return df

def rf_data_pipeline(directory):
    """Wrapper function to run through directories of labels and images to
    create a pandas dataframe with all the labels and associated image
    filenames needed to generate features for random forest training"""
    #set up required variables
    if os.path.isdir(directory+'/text_files') == False:
        raise RuntimeError('No text file directory present.')
    if os.path.isdir(directory+'/images') == False:
        raise RuntimeError('No image file directory present.')
    txt_list = glob(directory+'/text_files/*.txt')
    image_list = glob(directory+'/images/*.png')
    if len(txt_list) == 0:
        raise RuntimeError('No txt label files')
    if len(image_list) == 0:
        raise RuntimeError('No image files')
    txt_name_list = [name.split('/')[-1].split('.')[0] for name in txt_list]
    image_name_list = [name.split('/')[-1].split('.')[0] for name in image_list]
    data = {'filename':[],'label':[]}
    total_empty_count = 0
    total_null_count = 0
    total_no_count = 0
    total_yes_count = 0
    if os.path.isdir(directory+'/labeled_images') == False:
        os.mkdir(directory+'/labeled_images')

    #test for correct images and labels
    if txt_name_list != image_name_list:
        raise RuntimeError('Names of txt label files do not match names of image files.')

    #create dataframe of files and labels
    for idx, txt in enumerate(txt_list):
        labels, image_cuts, empty_count, null_count, no_count, yes_count = rf_label_reader(txt, image_list[idx])
        total_empty_count += empty_count
        total_null_count += null_count
        total_no_count += no_count
        total_yes_count += yes_count
        for idx2, label in enumerate(labels):
            data['label'].append(label)
            rf_data_fname = directory+'/labeled_images/'+image_name_list[idx]+ '_'+ label + '_' + str(idx2) +'.png'
            plt.imsave(rf_data_fname,image_cuts[idx2], cmap='gray')
            data['filename'].append(rf_data_fname)
    df = pd.DataFrame(data = data)
    print(df['label'].iloc[0])
    df = rotate(df)
    df.to_csv(directory+'/rf_data.csv')
    print('done!')
    print('empty: {}, null: {}, no: {}, yes {}'.format(total_empty_count*4, total_null_count,total_no_count*4,total_yes_count*4))
    return df, (total_empty_count, total_null_count, total_no_count, total_yes_count)

#Defining Feature Functions and Feature Creation Pipeline
def sobel_edges(gray_image):
    """Returns histogram of edges"""
    edges = skimage.filters.sobel(gray_image)
    edge_hist = np.histogram(edges.flatten(),bins=50, density = True)[0]
    return edge_hist

def blobs_log(gray_image):
    """returns two features: average blob size and total number of blobs detected by laplace of gaussians"""
    blob = skimage.feature.blob_log(gray_image,max_sigma=2, num_sigma=30, threshold=.2)
    blobs = blob[:,2]
    num_blobs = len(blobs)
    if num_blobs == 0:
        avg_blob = 0
    else:
        avg_blob = blobs.mean()
    blob_info = np.array([avg_blob, num_blobs])
    return blob_info

def fft_hist(gray_image):
    """returns 10 bin histogram of frequencies from fft of image"""
    fft = np.log2(abs(np.fft.rfft2(gray_image)))
    fhist = np.histogram(fft,bins=20,density = True)[0]
    return fhist

def center_cut(image):
    """returns a 1d array of length 48 which is 4x4 center of image of all three channels flattened"""
    middle = (image.shape[0]//2,image.shape[1]//2)
    cut = image[(middle[0]-10):(middle[0]+10),(middle[1]-10):(middle[1]+10)].ravel()
    return cut

def lbp_cut(gray_image):
    """returns 10 bin histogram of local binary patterns from image"""
    lbp = skimage.feature.local_binary_pattern(gray_image,2,16)
    middle = (lbp.shape[0]//2,lbp.shape[1]//2)
    lbp = lbp[(middle[0]-10):(middle[0]+10),(middle[1]-10):(middle[1]+10)].ravel()
    return lbp

def gray_range(image):
    irange = np.array([image.mean(),image.std()])
    return irange

def get_features(file, label):
    """Function takes in a file name from list of files, opens it,
     creates a gray version for features which require gray image and then
     creates a list of features as well as a label which is then returned"""
    image = io.imread(file, as_grey=True)
    features = []
    features.append(center_cut(image))
    features.append(lbp_cut(image))
    features.append(fft_hist(image))
    features.append(blobs_log(image))
    features.append(sobel_edges(image))
    features.append(gray_range(image))
    features = np.concatenate(features)
    return (features,label)

def feature_frame(file_label_df,directory = DIRECTORY):
    """Creates a pandas dataframe with all the calculated features for all the
     images in a given dataframe which contains all the images file names
      and labels."""
    features = [get_features(file, file_label_df['label'].iloc[idx]) for idx,file in enumerate(file_label_df['filename'])]
    print('Done!')
    feat_list, labels_list = zip(*features)
    df = pd.DataFrame.from_records(feat_list)
    column_names = [['center_cut']*400,['lbp_cut']*400,\
                    ['fft_hist']*20,['blobs_log']*2,['sobel_edges']*50,['mean'],['std']]
    column_names = sum(column_names, [])
    df.columns = column_names
    df['Label'] = labels_list
    df.to_csv(directory+'/rf_features.csv')
    return df

def balance_split_train_test(df,total_empty_count, total_null_count, total_no_count, total_yes_count):
    """Create two balanced dataframes of features with an equal number of
    each class, one with 80% of the data (training set)the other with 20% of
    the data (test set)"""
    cutoff = int(np.array([total_empty_count, total_null_count, total_no_count, total_yes_count]).min()*0.8)
    #shuffle input dataframe so that you do not end up with the same rotated image several times
    df = shuffle(df, random_state=0)
    bal_df1 = pd.DataFrame(columns=df.columns.values)
    bal_df2 = pd.DataFrame(columns=df.columns.values)
    names_list = df['Label'].drop_duplicates()
    for name in names_list:
        temp = df[df.values == name]
        bal_df1=bal_df1.append(temp.iloc[:cutoff,:])
        bal_df2=bal_df2.append(temp.iloc[cutoff:,:])
    bal_df1 = shuffle(bal_df1, random_state=0)
    bal_df2 = shuffle(bal_df2, random_state=0)
    return bal_df1, bal_df2

def XY_split(train_set,test_set):
    """splits training and testing dataframes into feature and label sets"""
    X_train = train_set.iloc[:,:-1]
    Y_train = train_set.iloc[:,-1]
    X_test = test_set.iloc[:,:-1]
    Y_test = test_set.iloc[:,-1]
    return X_train, Y_train, X_test, Y_test

def train_random_forest(X_train, Y_train, nestimators = 50,crit='gini',max_feat='auto'):
    """function that takes in the training feature set and training labels and trains a radnom forest with
    n estimators given by nestimators"""
    classifier = RandomForestClassifier(n_estimators= nestimators,criterion= crit,max_features=max_feat)
    classifier.fit(X_train, Y_train)
    return classifier

def cross_val_stratified(features_df,model,nsplit):
    """runs stratified k-fold cross validation where nsplit specifies the number of splits
    and returns the mean and standard deviation of the cross validation score. Based on the code shown in
    class."""
    X = features_df.iloc[:,:-1]
    Y = features_df.iloc[:,-1]
    cv = StratifiedKFold(n_splits=nsplit)
    scores = cross_val_score(model, X, Y, cv=cv, n_jobs=-1)
    print("mean: {:3f}, stdev: {:3f}".format(
        np.mean(scores), np.std(scores)))

def plot_confusion_matrix(X, Y, df, model):
    """Creates a confusion matrix for the different classes given a set of features, true labels, the dataset
    and the desired trained classfier"""
    Y_pred = model.predict(X)
    Y_labels = df['Label'].drop_duplicates()
    cfm = confusion_matrix(Y, Y_pred, labels=Y_labels)
    df_cfm = pd.DataFrame(data = cfm, columns=Y_labels, index=Y_labels)
    plt.subplots(figsize=(5,5))
    ax = sns.heatmap(df_cfm, vmax = 90, annot=True, fmt="d",cmap='rainbow')

def feature_importance(X_train,classifier):
    """Makes a plot of feature importance based of the feature importances calculated by scikit learn.
    Obviously features such as historgrams actually go into the classifier as several features so the function
    adds the importances of each of the features belonging to a certain class of feature"""
    feat_importance = np.vstack((X_train.columns.values,classifier.feature_importances_))
    previous = feat_importance[0,0]
    classes = [previous]
    counts = []
    temp_count = 0
    for idx, classify in enumerate(feat_importance[0,:]):
        if classify == previous:
            temp_count += feat_importance[1,idx]
            previous = classify
        else:
            counts.append(temp_count)
            classes.append(classify)
            temp_count = 0
            temp_count += feat_importance[1,idx]
            previous = classify

    counts.append(temp_count)
    fig, ax = plt.subplots()
    plt.bar(np.arange(1,len(classes)+1),counts,tick_label = classes)
    for tick in ax.get_xticklabels():
        tick.set_rotation(80)
    ax.set_xlabel('Feature Class')
    ax.set_ylabel('Feature Importance')
    ax.set_title("Feature Importance vs Feature Class")

def optimize_model(X_train,Y_train, nestimators = [10,20,30,50,70,100]):
    """function which runs model optimization given a certain number of n_estimators, max_features, and criterion
    (gini or entropy)"""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    parameters = {'n_estimators':nestimators,  'max_features':[3,8,10,'auto'],
                 'criterion': ['gini','entropy']}
    rf_tune = model_selection.GridSearchCV(RandomForestClassifier(), parameters,
                                       n_jobs = -1, cv = 5,verbose=1)
    rf_opt = rf_tune.fit(X_train, Y_train)
    print("Best zero-one score: " + str(rf_opt.best_score_) + "\n")
    print("Optimal Model:\n" + str(rf_opt.best_estimator_))
    return rf_opt
