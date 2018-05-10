#Pipeline to Classify the Atomic Structure of CdSe Quantum Dots

My research looks at the effect of atomic defects in cadmium selenide quantum
dots on optical properties. Current techniques of classifying nanoparticle
structures average over an entire population and therefore cannot account for
the impact of defects since these techniques average out defect populations.
The only way to directly measure these defects are through high-resolution
electron microscopy (HR-TEM). HR-TEM can give atomic resolution images which
can show whether the nanoparticle being observed contains a defect. Getting
statistics from these images to date has been an extremely slow process of
having a grad student count individual particles and then whether or not those
particles contain a defect. Clearly having an automated method of determining
defect content would be hugely helpful in characterizing heterogeneity
in nanoparticle populations, and is an active field of work within electron
microscopy.

This project therefore sought to try to leverage the machine learning and
image processing topics from class to create a pipeline of functions which would
be able to identify nanoparticle regions in HR-TEM micrographs and then classify
whether these regions were atomic resolution with a defect (in this project
labeled 'yes'), atomic resolution without a defect (labeled 'no'), and regions
that were not atomic resolution (labeled 'null'). 'Null' regions are labeled
such because without atomic resolution the defect content cannot be determined.

The data set consists of several hundred (approx 300) HR-TEM images of quantum
dots and their labels. These labels were both location of the center of the
identified particle, the radius of the particle (in pixels), and whether the
particle was defected ('yes'), not defected ('no'), or indistinguishable
('null') shown below (yes first, in pink, then no, in blue, finally null,
  in orange).

![yes](/README_images/np_no.tif)
![no](/README_images/np_no.tif)
![null](/README_images/np_null.tif)

My original plan was to try to segment the images using a convolutional neural
net based on a U-Net structure (discussed here:
  https://link.springer.com/chapter/10.1007%2F978-3-319-24574-4_28). However,
  this failed despite trying changing CNN structure, input size,
  filtering the data, etc. All these attempts can be found in jupyter notebooks
  in the file labeled file_of_failure. These didn't work because while they
  would overfit to the training data, once validation data was provided it would
  not give a mask like result as it was trained to do. I therefore
  transitioned to using the labeling information to artificially segment out
  nanoparticle regions based on the label data and using the artificially
  segmented images as training and testing data for a random forest classifier.

  The random forest classifier was very successful on these artificially
  segmented images, getting a mean cross validation score of 0.8. The confusion
  matrix from the test data is shown below. Because the segmentation was such
  a problem I determined that it would probably be necessary to include a 4th
  class called 'empty' which would identify regions that contained no
  nanoparticle. All of the functions were put into a .py file called random
  forest so that test functions could be run on them and they are imported into
 the final demo jupyter notebook. All of the work to develop the random forest
 classifier can be found in the jupyter notebook labeled
 Random_Forest_Development.

  ![confusion_matrix](/README_images/confusion_matrix.tif)

  Having created a seemingly good structure classifier I then
