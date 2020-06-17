#################################################
import pandas as pd
import time_util
import preprocess_images
import get_vectors
import cluster_images
from pathlib import Path
import sys
#################################################

PREPROCESS = False

#################################################
class create_session:
    def __init__(self, images_dir, do_preprocess = PREPROCESS):
        self.session = time_util.timestamp_simple()
        self.tracker = time_util.time_tracker()
        self.images_dir = images_dir
        print(f'--- New Session: {self.session } Created for Directory: {images_dir}')

        # if do_preprocess:
        #     self.images_dir = preprocess_images.get_preprocessed_images(self.images_dir)

    def start_run(self):
        get_vectors.get_image_feature_vectors(self.images_dir, self.tracker, self.session)

        cluster_images.cluster(self.tracker, self.session)

        # self.update_latest()

    # def update_latest()
    #     optimized_cluster_path = 

if __name__ == "__main__":
    args = sys.argv # take in args from system 
    arg_len = len(args) # check how many args came in
 
        # Set arg_path if there are args 
    if (len(args) >= 2):
        arg_path = args[1] # sets arg path for use later

    # arg index 0 is filename, index 1 is the first option. If no args explain correct usage
    if (arg_len != 2):
        # Explain correct usage
        print("\n")
        print(time_util.timestamp() + '[ERROR] No path given, correct usage: Python3 %s $image_directory' % args[0])
        print(time_util.timestamp() + '[Example] Python3 app.py /Applications/XAMPP/xamppfiles/htdocs/AI-Cull/images/dngs-structured-small')
        quit() # quit program if being used incorrectly

    track_total_time = time_util.time_tracker() # start tracking time

    print(time_util.timestamp() + '[INFO] You gave directory path:' + arg_path) # Print path given
    print("\n")
    print('*******************************************')

    new_session = create_session(arg_path)

    new_session.start_run()
    