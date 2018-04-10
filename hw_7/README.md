# Homework 7 Scikit-Image

For problem 1, I took the coins image and show the application of each of the steps outlined in the problem definition.

For problem 2, the file of images I stitched together is included in the file called 'bridge'. This directory is defined and then sent into the pipeline function which then calls all the other functions which implement the code shown in the image stitching tutorial.

For the extra credit I had some issues in processing the data including very long runtimes. I tried to solve this problem by changing each image to a png and then loading that into the ImageCollection function so each one would only have to be in memory one at a time most of the time. I was unable to get this to work. 
