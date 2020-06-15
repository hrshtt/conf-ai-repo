import os
import time_util

thislist = []

def find_filetype_in( filetype, path ):
	""" find filetype in the current path recursively returns list of file names

      Typical usage example:

      find_filetype_in( 'dng', '~\somepath\test\' ) 
    """

	for root, dirs, files in os.walk(path):
	    for file in files:
	        if file.endswith(filetype):
	             #print(os.path.join(file))
	             thislist.append(os.path.join(file))

	return thislist

def find_filetype_location_in( filetype, path ):
	""" find filetype in the current path recursively returns list of file paths

      Typical usage example:

      find_filetype_in( 'dng', '~\somepath\test\' ) 
    """
	for root, dirs, files in os.walk(path):
	    for file in files:
	        if file.endswith(filetype):
	             #print(os.path.join(root, file))
	             thislist.append(os.path.join(root, file))

	return thislist