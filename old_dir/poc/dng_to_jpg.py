import fnmatch
import imageio
import os
import rawpy
from shutil import copyfile
import time_util

""" Convert DNG to JPG with some post processing to make up for demosaicing 

1. Open Image given a Path
2. Post Process Raw to RGB
3. Save as JPG file type given output name

  Typical usage example: 

  Example convert(image_path, outputname)
"""

def convert( run_at, path, name):

	# Only create file if it does not exist
	try:
		f = open('output/converted_jpgs/' + name + '.jpg')
	except IOError:
		# If not there create file
		if(fnmatch.fnmatch(path, '*.dng')):
			with rawpy.imread(path) as raw:
				# https://letmaik.github.io/rawpy/api/rawpy.Params.html
				rgb = raw.postprocess(demosaic_algorithm=0, use_camera_wb=True, four_color_rgb=False, no_auto_bright=True, exp_shift=2.5, user_black=350, exp_preserve_highlights=1.0)

			# If saving jpgs each time imageio.imsave('output/' + run_at + '/converted_jpgs/' + name + '.jpg', rgb)
			# If saving jpgs once
			imageio.imsave('output/converted_jpgs/' + name + '.jpg', rgb)
			f = open('output/converted_jpgs/' + name + '.jpg')
		else:
			# copy image if it isn't already in converted folder
			copyfile(path, 'output/converted_jpgs/' + name + '.jpg',)
			f = open('output/converted_jpgs/' + name + '.jpg')
	finally:
		# if jpg is there skip
	    f.close()

