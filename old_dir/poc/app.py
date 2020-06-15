# Imports sorted alphabetically
#import blur_detect
#import blink_detect
import classify_images
import clean_up
import cluster_vectors
import csv_generator
import directory_check
import dng_to_jpg
#import face_detect
import fnmatch
import os
import resize
from shutil import copyfile
import sys
import time_util
import subprocess

""" TEMPLATE One liner Documentation
********************************
1. Step by step what does this do

  Typical usage example:

  Example
********************************
"""

def main(resize_max_length_c, top_x_features_c, top_x_likeness_c, top_x_limit_c, face_scale_c, face_neighbors_c, face_min_c, face_resize_c, blur_threshold_c):
    """ This program takes a directory path of images and processes them for cull flags
    ********************************
    1. Take directory path for Smart Previews. DONE
    2. Recursively parse directory into List. DONE
    3. Convert DNG to JPG. DONE
    4. Resize images smaller. DONE
    5. Process list of images for Duplicates. 
    6. Process list of images for Faces. DONE
    7. Process list of images for Blurs. DONE
    8. Process list of images for Blinks. DONE
    9. Process list of images for Distortions (later feature).
    10. Convert list to CSV for interpretation by other programs. DONE
    
      Typical usage example:

      Python3 app.py $path_to_smart_preview_directory 
      python3 app.py /Applications/XAMPP/xamppfiles/htdocs/AI-Cull/images/dngs-structured-small

    Will store intermediary steps and performance in the output folder 
    ********************************
    """

    # Constants for CSV header lookup so we don't have to use indexes, sort in order of csv row
    CONST_KEY = 'Key' # 0 
    CONST_FILE = 'File' # 1
    CONST_LOCATION = 'Location' # 2
    CONST_JPG = 'JPG' # 3
    CONST_JPG_LOCATION = 'JPG Location' # 4
    CONST_SCALED_JPG = 'Scaled JPG' # 5
    CONST_FEATURES = 'Features' # 6
    CONST_VECTOR = 'Vector' # 7
    CONST_NEIGHBORS = 'Neighbors' # 8
    CONST_FACES = 'Faces' # 9
    CONST_FOCUS = 'Focus' # 10
    CONST_BLURRY = 'Blurry' # 11
    CONST_BLINKS = 'Blinks' # 12

    # Instance variables
    args = sys.argv # take in args from system 
    arg_len = len(args) # check how many args came in
    run_at = time_util.timestamp_simple()
    csv_title = 'Results_' + run_at # title of csv file being output
    csv_performance = "All_Performance.csv" # title of performance csv
    csv_columns = [] # initialize column headers for csv
    list_data = [] # inititalize list data as empty
    progress = 1 # initialize progress to 1st item 
    queue = 0 # initialize size of queue to 0
    root_dir = os.getcwd() # initialize root directory location
    verbose = 0 

    # Clean Up Old Run Before Starting New One
    #clean_up.folder('converted_jpgs')
    #clean_up.folder('faces/individuals')
    #clean_up.folder('faces/overlays')
    #clean_up.folder('image_vectors')
    #clean_up.folder('nearest_neighbors')
    #clean_up.folder('scaled_bw_jpgs')
    #print(time_util.timestamp() + '[INFO] Clean Up Done') # Print path given

    # Performance Metrics
    resize_max_length = resize_max_length_c # this is the long edge size of our resized images
    top_x_features = top_x_features_c
    top_x_likeness = top_x_likeness_c
    top_x_limit = top_x_limit_c
    face_scale = face_scale_c
    face_neighbors = face_neighbors_c 
    face_min = face_min_c
    face_resize = face_resize_c
    face_cascade = 'haarcascade_frontalface_default.xml' # not implemented yet 
    blur_threshold = blur_threshold_c 
    eyes_min = 20 # not implemented in blinks 
    image_count = 0
    face_found = 0 
    eyes_found = 0 # not implemented in blinks 
    blinks_found = 0 
    blurs_found = 0 

    # Total Time Amounts for Each Step
    total_time = 0.0
    queue_time = 0.0
    convert_time = 0.0
    resize_time = 0.0
    feature_time = 0.0
    likeness_time = 0.0
    face_time = 0.0
    blink_time = 0.0
    blur_time = 0.0
    csv_time = 0.0

    # Set arg_path if there are args 
    if (len(args) >= 2):
        arg_path = args[1] # sets arg path for use later

    # arg index 0 is filename, index 1 is the first option. If no args explain correct usage
    if (arg_len != 2):
        # Explain correct usage
        print("\n")
        print(time_util.timestamp() + '[ERROR] No path given, correct usage: Python3 %s $image_directory' % args[0])
        print(time_util.timestamp() + '[Example] Python3 app.py /Applications/XAMPP/xamppfiles/htdocs/AI-Cull/images/dngs-structured-small')
        print('*******************************************')
        print('*************** PROGRAM END ***************')
        print('*******************************************')
        quit() # quit program if being used incorrectly

    track_total_time = time_util.time_tracker() # start tracking time

    if(verbose == 1):
        # Confirm path given in args
        print(time_util.timestamp() + '[INFO] You gave directory path:' + arg_path) # Print path given
        print("\n")
        print('*******************************************')

        """ Let user know that we are generating a queue of "n" size based on the contents of folder path given
        ********************************
        INPUT = directory of files
        1. This code block will look through the path given and find all dng files
        OUTPUT = List Data is updated with file and location of the dng files
        PRINTS = Each time item is added to queue for processing
        ********************************
        """
        print("\n")
        print(time_util.timestamp() + '[STEP] Genearting Queue of files from directory path...')
        print("\n")

    # create the output/run_at folder if it does not exist
    if not os.path.exists('output/'):
        if(verbose == 1):
            print(time_util.timestamp() + "[INFO] Missing output folder, creating it...")
        os.makedirs('output/')

    # create the output/run_at folder if it does not exist
    if not os.path.exists('output/' + run_at):
        if(verbose == 1):
            print(time_util.timestamp() + "[INFO] Missing output/run_at folder, creating it...")
        os.makedirs('output/' + run_at)

    # Add headers for File and Location
    csv_columns.append(CONST_KEY)
    csv_columns.append(CONST_FILE)
    csv_columns.append(CONST_LOCATION)

    track_queue_time = time_util.time_tracker() # start tracking time
    # Add data for File and Location
    xi = 0
    for root, dirs, files in os.walk(arg_path):
        for _file in files:
            if xi < 10:
                if (fnmatch.fnmatch(_file, '*.dng') or fnmatch.fnmatch(_file, '*.jpg')):
                    xi = xi + 1
                    print(f'{xi + 1} file added to queue')
                    key = _file[:-4] # is the non extension name
                    add_item = [key, os.path.join(_file), os.path.join(root, _file)]
                    list_data.append(add_item)
                    if(verbose == 1):
                        print(time_util.timestamp() + "[INFO] Added to Queue: " + key)
                    queue = queue + 1

    total_images = queue # set queue size

    print(time_util.timestamp() + "[INFO] Queue Size: " + str(queue))
    print("\n")
    print(time_util.timestamp() + "[INFO] Total Time to generate queue: " + str(track_queue_time.total_time()))

    queue_time = track_queue_time.total_time() # how long did it take to generate queue

    if(verbose == 1):
        print("\n")
        print('*******************************************')
        """ Convert DNG to JPG
        ********************************
        INPUT = queue of files in list data
        1. This code block will look through the queue in list data and convert dngs to jpg
        OUTPUT = JPG files from the DNGs
        OUTPUT = List Data is updated with file and location of the jpg files
        PRINTS = Each time item is converted to jpg
        ********************************
        """
        print("\n")
        print(time_util.timestamp() + '[STEP] Converting DNGs to JPG from queue...')
        print("\n")

    progress = progress # this doesn't do anything it is just to keep pattern

    # Add header for jpg file and location
    csv_columns.append(CONST_JPG)
    csv_columns.append(CONST_JPG_LOCATION)

    track_convert_time = time_util.time_tracker() # start tracking time

    # create the output/ folder if it does not exist
    if not os.path.exists('output/converted_jpgs'):
        #print(time_util.timestamp() + "[INFO] Missing output/converted_jpgs folder, creating it...")
        os.makedirs('output/converted_jpgs')

    # create the output/run_at folder if it does not exist
    if not os.path.exists('output/' + run_at + '/converted_jpgs'):
        #print(time_util.timestamp() + "[INFO] Missing output/run_at/converted_jpgs folder, creating it...")
        os.makedirs('output/' + run_at + '/converted_jpgs')

    # Convert all DNGs to JPG
    for row in list_data:
        name = row[csv_columns.index(CONST_KEY)]
        dng_to_jpg.convert(run_at, row[csv_columns.index(CONST_LOCATION)],name) # dng path
        if(verbose == 1):
            print(time_util.timestamp() + "[INFO] DNG to JPG (" + str(progress) + " of " + str(queue) +"): " + name)
        progress = progress + 1

        # Add New Data
        row.append(name + '.jpg')
        # Convert DNG every time row.append("output/"+ str(run_at) + "/converted_jpgs/" + name + ".jpg")
        # Convert DNG once
        row.append("output/converted_jpgs/" + name + ".jpg")

    print("\n")
    print(time_util.timestamp() + "[INFO] Total Time to Convert DNG to JPG: " + str(track_convert_time.total_time()))
    convert_time = track_convert_time.total_time() # how long did it take to convert to JPG
    print("\n")

    if(verbose == 1):
        print('*******************************************')
        """ Scale down JPG and Convert to Grayscale
        ********************************
        INPUT = queue of files in list data
        1. This code block will look through the queue in list data and resize down jpgs
        OUTPUT = Scaled / BW JPG files
        OUTPUT = List Data is updated with file and location of the jpg files
        PRINTS = Each time item is converted to jpg
        ********************************
        """
        print("\n")
        print(time_util.timestamp() + '[STEP] Converting JPG to ' + str(resize_max_length) + 'px long edge and grayscale from queue...')
        print("\n")

    progress = 1 # reset progress for this step

    # Add header for scale bw jpgs
    csv_columns.append(CONST_SCALED_JPG)

    track_resize_time = time_util.time_tracker() # start tracking time

    # Black white and resize all JPG
    for row in list_data:
        name = row[csv_columns.index(CONST_KEY)] # name key
        resize.resize_image(run_at, row[csv_columns.index(CONST_JPG_LOCATION)],name, resize_max_length) # jpg path
        if(verbose == 1):
            print(time_util.timestamp() + "[INFO] BW Resize Complete on (" + str(progress) + " of " + str(queue) +"): " + name)
        progress = progress + 1

        # Add New Data
        # if scaling every time 
        row.append("output/"+ str(run_at) + "/scaled_bw_jpgs/" + name + "_bw.jpg")
        # if scaling just one time 
        # row.append("output/scaled_bw_jpgs/" + name + "_bw.jpg")

    print("\n")
    print(time_util.timestamp() + "[INFO] Total Time to Scale JPG: " + str(track_resize_time.total_time()))
    resize_time = track_resize_time.total_time() # how long did it take to resize
    print("\n")

    if(verbose == 1):
        print('*******************************************')
        """ Run Feature Detection to Vectorize Images for Comparison
        ********************************
        INPUT = directory of files
        1. This code block will look through the queue in list data and find features (things)
        OUTPUT = image vectors based on feature detection
        OUTPUT = List Data is updated with feature confidence
        PRINTS = Each time feature is found
        ********************************
        """
        print("\n")
        print(time_util.timestamp() + '[STEP] Running Feature detection on scaled JPGs...')
        print("\n")

    progress = 1 # reset progress for this step

    # Add headers for duplicates data
    # csv_columns.append(CONST_FEATURES)
    csv_columns.append(CONST_VECTOR)

    track_feature_time = time_util.time_tracker() # start tracking time

    # Run whole directory at once
    # subprocess.run(["python", "classify_images.py", arg_path])
    list_data = classify_images.classify_image(run_at, list_data, csv_columns)

    print("\n")
    print(time_util.timestamp() + "[INFO] Total Time to Feature Detect: " + str(track_feature_time.total_time()))
    feature_time = track_feature_time.total_time() # how long did it take to generate features
    print("\n")
    print(list_data)
    if(verbose == 1):
        print('*******************************************')
        """ Run Nearest Neighbor for Likeness Comparison
        ********************************
        INPUT = directory of files
        1. This will check the image_vectors directory and return json list of nearest neighboors
        OUTPUT = json file of nearest neighbor
        OUTPUT = List data of nearest neighbor
        PRINTS = Each json object
        ********************************
        """
        print("\n")
        print(time_util.timestamp() + '[STEP] Running nearest ' + str(top_x_likeness) + ' likeness detection on image vectors...')
        print("\n")

    progress = 1 # reset progress for this step

    # Add header for duplicates data
    csv_columns.append(CONST_NEIGHBORS)

    track_likeness_time = time_util.time_tracker() # start tracking time

    # Duplicates detection will find vectorize based on feature detect
    # Images with the same features at similar confidence levels will be believed to be the same 
    # Add to list an array of duplicate data

    # Run whole directory at once
    list_data = cluster_vectors.nearest_neighboors(run_at, list_data, csv_columns, top_x_likeness, top_x_limit)

    print("\n")
    print(time_util.timestamp() + "[INFO] Total Time to Likeness Detect: " + str(track_likeness_time.total_time()))
    likeness_time = track_likeness_time.total_time() # how long did it take to generate likeness data
    print("\n")

    # """ TEMP DISABLED as not needed for APP 3"""
    # if(verbose == 1):
    #     print('*******************************************')
    #     """ #Find faces in images and save cropped faces
    #     #********************************
    #     #INPUT = directory of files
    #     #1. This code block will look through the queue in list data and find faces
    #     #OUTPUT = face cropped jpgs
    #     #OUTPUT = List Data is updated with face details
    #     #PRINTS = Each time face is found
    #     #********************************
    #     """
    #     print("\n")
    #     print(time_util.timestamp() + '[STEP] Running Face detection on converted full size JPGs...')
    #     print("\n")

    # progress = 1 # reset progress for this step

    # # Add header for faces data
    # csv_columns.append(CONST_FACES)

    # track_face_time = time_util.time_tracker() # start tracking time

    # # create the output/run_at folder if it does not exist
    # if not os.path.exists('output/' + run_at + '/faces'):
    #     #print(time_util.timestamp() + "[INFO] Missing output/run_at/faces folder, creating it...")
    #     os.makedirs('output/' + run_at + '/faces')

    # # create the output/run_at folder if it does not exist
    # if not os.path.exists('output/' + run_at + '/faces/individuals/'):
    #     #print(time_util.timestamp() + "[INFO] Missing output/run_at/faces/individuals/ folder, creating it...")
    #     os.makedirs('output/' + run_at + '/faces/individuals/')

    # # create the output/run_at folder if it does not exist
    # if not os.path.exists('output/' + run_at + '/faces/overlays/'):
    #     #print(time_util.timestamp() + "[INFO] Missing output/run_at/ffaces/overlays/ folder, creating it...")
    #     os.makedirs('output/' + run_at + '/faces/overlays/')

    # # Face images will be used for both blur and blink detection
    # # Save all faces to their own JPGs
    # # Add to list an array of face photo locations
    # # TODO add profile face detection
    # # TODO eventually move to a RNN model rather than haarcascade
    # for row in list_data:
    #     name = row[csv_columns.index(CONST_KEY)] # name key
    #     faces = face_detect.get_faces(run_at, row[csv_columns.index(CONST_SCALED_JPG)], name, face_scale, face_neighbors, face_min, face_resize) # jpg path
    #     if(verbose == 1):
    #         print(time_util.timestamp() + "[INFO] Face Detection Complete on (" + str(progress) + " of " + str(queue) +"): " + name)
    #     progress = progress + 1

    #     face_num = len(faces)
    #     # Add New Data
    #     row.append(faces) # faces
    #     face_found = face_found + int(face_num)
    # print(time_util.timestamp() + "[INFO] Total Faces Found: " + str(face_found))

    # print("\n")
    # print(time_util.timestamp() + "[INFO] Total Time to Face Detect: " + str(track_face_time.total_time()))
    # face_time = track_face_time.total_time() # how long did it take to generate likeness data
    # print("\n")

    # """ TEMP DISABLED do not need for APP3 """ 

    # if(verbose == 1):
    #     print('*******************************************')
    #     """ #Check all faces found if they are blurry
    #     #********************************
    #     #INPUT = directory of files
    #     #1. This code block will look through the queue in list data and determine if faces are blurry
    #     #OUTPUT = focus measure and blur decision
    #     #PRINTS = Each time a photo is reviewed
    #     #********************************
    #     """
    #     print("\n")
    #     print(time_util.timestamp() + '[STEP] Running Blur Detection...')
    #     print("\n")

    # progress = 1 # reset progress for this step

    # # Add header for Blur Check
    # csv_columns.append(CONST_FOCUS)
    # csv_columns.append(CONST_BLURRY)

    # track_blur_time = time_util.time_tracker() # start tracking time

    # # Blur Check Images
    # # TODO also check profile faces
    # # ADD RNN model rather than laplacian only (need to categorize the cropped faces we have)
    # for row in list_data:

    #     blur_check = "image" # faces or image

    #     faces = row[csv_columns.index(CONST_FACES)] # List of faces
    #     # Ex faces
    #     # [
    #     #   ['0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_1_196x196_faces', 'faces/individuals/0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_1_196x196_faces.jpg', '196', '196'], 
    #     #   ['0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_2_194x194_faces', 'faces/individuals/0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_2_194x194_faces.jpg', '194', '194'], 
    #     #   ['0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_3_90x90_faces', 'faces/individuals/0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_3_90x90_faces.jpg', '90', '90']
    #     #]

    #     focus = 0
    #     blurry = 0
    #     blurry_faces = 0 
    #     name = row[csv_columns.index(CONST_KEY)] # name key
    #     original = row[csv_columns.index('Scaled JPG')]

    #     if( len(faces) > 0 and blur_check == "faces"):
    #         for face in faces:
    #             face_result = blur_detect.check_image_for_blur(run_at, name, face[0], original, face[1], blur_threshold) # index 1 is the location of the face file

    #             # Add New Data for Focus and Blur
    #             face.append("%0.2f" % face_result[0]) # focus
    #             face.append(face_result[1]) # blur

    #             focus = focus + int(face_result[0]) # add up all focus results 
    #             blurry_faces = blurry_faces + int(face_result[1]) # add up number of blurry faces

    #         focus = focus / len(faces) # average focus measure

    #     else: 
    #         # Check the whole image if no faces found or if blur_check is NOT set to faces
    #         image_result = blur_detect.check_image_for_blur(run_at, name, name, original, original, blur_threshold) # index 1 is the location of the face file

    #         focus = focus + int(image_result[0]) # add up all focus results 
    #         blurry = blurry + int(image_result[1]) # add up number of blurry faces
        
    #     # If focus was calculated 
    #     if( focus>0 ):
    #         row.append("%0.0f" % focus) # focus average

    #         # If average focus for the image is below threshold then image is blurry, save sample
    #         if( focus < blur_threshold):

    #             # create the output/run_at folder if it does not exist
    #             if not os.path.exists('output/' + run_at + "/blurs/blurry_images/" + str("%0.2f" % focus) + '_' +  name + '.jpg'):
    #                 copyfile(original, 'output/' + run_at + "/blurs/blurry_images/" + str("%0.2f" % focus) + '_' +  name + '.jpg')
    #         else:
    #             # create the output/run_at folder if it does not exist
    #             if not os.path.exists('output/' + run_at + "/blurs/not_blurry_images/" + str("%0.2f" % focus) + '_' +  name  + '.jpg'):
    #                 copyfile(original, 'output/' + run_at + "/blurs/not_blurry_images/" + str("%0.2f" % focus) + '_' + name  + '.jpg')
    #     # If focus was NOT calculated
    #     else: 
    #         row.append('') # focus

    #     row.append(blurry) # blur
    #     blurs_found = blurs_found + blurry         

    #     if(verbose == 1):
    #         print(time_util.timestamp() + "[INFO] Blur Check Complete on (" + str(progress) + " of " + str(queue) +"): " + name)
    #     progress = progress + 1

    # print("\n")
    # print(time_util.timestamp() + "[INFO] Total Time to Blur Detect: " + str(track_blur_time.total_time()))
    # blur_time = track_blur_time.total_time() # how long did it take to generate likeness data
    # print("\n")

    # """ TEMP DISABLED DO NOT NEED for APP3 """ 

    # if(verbose == 1):
    #     print('*******************************************')
    #     """ #Check all faces found if they are blinking
    #     #********************************
    #     #INPUT = directory of files
    #     #1. This code block will look through the queue in list data and determine if faces are blinking
    #     #OUTPUT = blink decision decision
    #     #PRINTS = Each time a photo is reviewed
    #     #********************************
    #     """
    #     print("\n")
    #     print(time_util.timestamp() + '[STEP] Running Blink Detection on all faces found...')
    #     print("\n")

    # progress = 1 # reset progress for this step

    # # Add header for Blink Check
    # csv_columns.append(CONST_BLINKS)

    # track_blink_time = time_util.time_tracker() # start tracking time

    # # Run whole directory at once
    # results = blink_detect.check_list_for_blink(run_at, list_data, csv_columns, face_cascade, face_scale, face_neighbors, face_min)

    # eyes_found = results[0]
    # blinks_found = results[1]
    # list_data = results[2]

    # """ 
    # # Move Blink Detection to BULK
    # # Blink Check Images
    # # TODO also check profile faces
    # """
    # for row in list_data:
    #     faces = row[csv_columns.index(CONST_FACES)] # List of faces
    #     # Ex faces
    #     # [
    #     #   ['0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_1_196x196_faces', 'faces/individuals/0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_1_196x196_faces.jpg', '196', '196'], 
    #     #   ['0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_2_194x194_faces', 'faces/individuals/0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_2_194x194_faces.jpg', '194', '194'], 
    #     #   ['0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_3_90x90_faces', 'faces/individuals/0AC0C99D-0B40-4331-AC92-CF6BC9C60D34_Face_3_90x90_faces.jpg', '90', '90']
    #     #]

    #     blinks = 0
    #     name = row[csv_columns.index(CONST_KEY)] # name key

    #     if( len(faces) > 0):
    #         for face in faces:
    #             face_result = blink_detect.check_image_for_blink(face[1], face_cascade, face_scale, face_neighbors, face_min) # index 1 is the location of the face file

    #             # Add New Data for confidence and blink
    #             face.append("%0.2f" % face_result[0]) # blink confidence
    #             face.append(face_result[1]) # blink count

    #             blinks = blinks + int(face_result[1])
        
    #     row.append(blinks) # focus
    #     blinks_found = blinks_found + blinks          

    #     print(time_util.timestamp() + "[INFO] Blink Check Complete on (" + str(progress) + " of " + str(queue) +"): " + name)
    #     progress = progress + 1

    # """ TEMP DISABLED NOT NEEDED in APP3 """ 

    # print("\n")
    # print(time_util.timestamp() + "[INFO] Total Time to Blink Detect: " + str(track_blink_time.total_time()))
    # blink_time = track_blink_time.total_time() # how long did it take to generate likeness data
    # print("\n")

    # if(verbose == 1):
    #     print('*******************************************')
    #     """ Output data to CSV
    #     ********************************
    #     INPUT = list data
    #     1. This code block will convert list data into csv format
    #     OUTPUT = csv
    #     PRINTS = name of csv
    #     ********************************
    #     """
    #     print("\n")
    #     print(time_util.timestamp() + "[STEP] Generating CSV...")
    #     print("\n")
   
    # listToStr = ' '.join(map(str, csv_columns)) # Convert headers list to string
    # if(verbose == 1):
    #     print(time_util.timestamp() + "[INFO] CSV Headers: " + listToStr) # Display csv headers

    # # Convert list to csv
    # track_csv_time = time_util.time_tracker() # start tracking time
    # csv_generator.list_to_csv( csv_title, csv_columns, list_data)  
    # print(time_util.timestamp() + '[INFO] Your CSV File is: ' + csv_title + ".csv")
    # print(time_util.timestamp() + "[INFO] Total Time to generate csv: " + str(track_csv_time.total_time()))
    # csv_time = track_csv_time.total_time() # how long did it take to generate likeness data

    # print(time_util.timestamp() + "[INFO] Total Time to Run AI: " + str(track_total_time.total_time()))
    # total_time = track_total_time.total_time() # how long did it take to generate likeness data

    # # Log Performance
    # performance_tracking_headers = ["run_at", "image_count", "resize_max_length", "top_x_features", "top_x_likeness", "top_x_limit", "face_scale", "face_neighbors", "face_min", "face_resize", "face_cascade", "face_found", "blur_threshold", "eyes_min", "eyes_found", "blinks_found", "blurs_found", "Total Time", "Generate Queue Time", "Convert to JPG Time","Resize JPG Time","Feature Time","Likeness Time","Face Time","Blink Time","Blur Time","Csv Time"]
    
    # try:
    #     f = open("output/" + csv_performance)
    # except IOError:
    #     print(time_util.timestamp() + '[ERROR] Could not find performance CSV, creating new one...')
    #     csv_generator.append_to_csv("all_performance.csv",performance_tracking_headers) # this will always add headers which will need to be scrubbed in review
    #     f = open("output/" + csv_performance)
    # finally:
    #     f.close()

    # performance_row = [run_at, queue, resize_max_length, top_x_features, top_x_likeness, top_x_limit, face_scale, face_neighbors, face_min, face_resize, face_cascade, face_found, blur_threshold, eyes_min, eyes_found, blinks_found, blurs_found, total_time, queue_time, convert_time, resize_time, feature_time, likeness_time, face_time, blink_time, blur_time, csv_time]
    # csv_generator.append_to_csv("all_performance.csv",performance_row) # this will always add headers which will need to be scrubbed in review


    # This is the end of the porgram
    print('*******************************************')
    print('*************** PROGRAM END ***************')
    print('*******************************************')

if __name__ == '__main__':
    # This is the start of the program
    print('*******************************************')
    print('*************** PROGRAM START *************')
    print('*******************************************')
    print("\n")
    
    # Default run
    # print(time_util.timestamp() + "[INFO] Default Settings Run: 2400, 10, 50, 1.25, 4, 80, 120, 180.0")
    # main(resize_max_length_c, top_x_features_c, top_x_likeness_c, face_scale_c, face_neighbors_c, face_min_c, face_resize_c, blur_threshold_c):
    # main(2400, 10, 50, 1.25, 4, 80, 120, 180.0) # execute main

    # Benchmark Resize
    resize_options = [1800]
    for n in resize_options:
      resize_max_length = n

      # Benchmark Top Features Count
      top_x_f = [10]
      for m in top_x_f:
        top_x_features = m

        # Benchmark Nearest Neighbors
        top_x_l = [30]
        for o in top_x_l:
          top_x_likeness = o

          # Benchmark Limit Neighbors
          top_x_l = [0.9]
          for u in top_x_l:
            top_x_limit = u

            # Benchmark Face Scale
            face_scale_options = [1.05]
            for p in face_scale_options:
              face_scale = p

              # Benchmark Face Neighboors
              face_neighbors_options = [20]
              for q in face_neighbors_options:
                face_neighbors = q

                # Benchmark Face Min Size
                face_min_options = [60]
                for r in face_min_options:
                  face_min = r

                  # Benchmark Face Min Size
                  face_resize_options = [0]
                  for s in face_resize_options:
                    face_resize = s

                    # Benchmark Blur
                    blur_thresh = [35.00]
                    for t in blur_thresh:
                      blur_threshold = t

                      print(time_util.timestamp() + "[INFO] Resize Benchmarking: " + str(resize_max_length))
                      print(time_util.timestamp() + "[INFO] Top Features Benchmarking: " + str(top_x_features))
                      print(time_util.timestamp() + "[INFO] Top Likeness Benchmarking: " + str(top_x_likeness))
                      print(time_util.timestamp() + "[INFO] Top Likeness Benchmarking: " + str(top_x_limit))
                      print(time_util.timestamp() + "[INFO] Face Scale Benchmarking: " + str(face_scale))
                      print(time_util.timestamp() + "[INFO] Face Neighbors Benchmarking: " + str(face_neighbors))
                      print(time_util.timestamp() + "[INFO] Face Min Benchmarking: " + str(face_min))
                      print(time_util.timestamp() + "[INFO] Face Resize Benchmarking: " + str(face_resize))
                      print(time_util.timestamp() + "[INFO] Blur Benchmarking: " + str(blur_threshold))

                      # Run Benchmark
                      main(resize_max_length, top_x_features, top_x_likeness, top_x_limit, face_scale, face_neighbors, face_min, face_resize, blur_threshold) # execute main