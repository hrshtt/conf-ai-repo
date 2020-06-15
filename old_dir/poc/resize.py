import cv2 # add cv2 library
#import numpy as np # add numpy library with alias np 
from PIL import Image # add Image library from PIL
import os
import time_util

""" Resize JPG based on max length given

  Typical usage example:

  Example 
"""

def resize_keep_aspect(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def resize_image( run_at, path, name, length ):

	# create the output/run_at folder if it does not exist
	if not os.path.exists('output/' + run_at + '/scaled_bw_jpgs'):
		#print(time_util.timestamp() + "[INFO] Missing output/run_at/scaled_bw_jpgs folder, creating it...")
		os.makedirs('output/' + run_at + '/scaled_bw_jpgs')

	# create the output/ folder if it does not exist
	if not os.path.exists('output/scaled_bw_jpgs'):
		#print(time_util.timestamp() + "[INFO] Missing output/scaled_bw_jpgs folder, creating it...")
		os.makedirs('output/scaled_bw_jpgs')

	# Only create file if it does not exist
	try:
		# For single run
		#f = open('output/scaled_bw_jpgs/' + name + '_bw.jpg')
		# For individual runs
		f = open('output/' + run_at + '/scaled_bw_jpgs/' + name + '_bw.jpg')
	except IOError:
		# If not there create file

		# Set Max_Length for Resize
		max_length = length 

		# Use pillow to read images 
		img = Image.open(path)

		#resize does not respect aspect ratio so we do not use it 
		#img_resized = img.resize((400, 400))
		#img_resized.save('image_400.jpg')

		# Resize Image using thumbnail method to max_length on longest side 
		img.thumbnail((max_length, max_length))
		# Save thumbnail image 
		#img.save( name + '.jpg')

		# Convert thumbnail image to greyscale
		img = img.convert('L')

		# Save the greyscale image globally
		#img.save('output/scaled_bw_jpgs/' + name + '_bw.jpg')
		#f = open('output/scaled_bw_jpgs/' + name + '_bw.jpg')

		# Save the greyscale image per run
		img.save('output/' + run_at + '/scaled_bw_jpgs/' + name + '_bw.jpg')
		f = open('output/' + run_at + '/scaled_bw_jpgs/' + name + '_bw.jpg')
	finally:
		# if jpg is there skip
	    f.close()



