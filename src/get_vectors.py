#################################################
# For running inference on the TF-Hub module.
import tensorflow as tf
import tensorflow_hub as hub

# For working with Vectors
import numpy as np

# Time for measuring the process time
import time_util

# pathlib to handle paths
from pathlib import Path
import paths_util

# Default Dict to create Json Data, and json to save it
import json
from collections import defaultdict
#################################################

#################################################
# TensorFlow Hub Model Being used: mobilenet_v2_140_224
# Input Requirement: image of dimension height (224) x length (224) x channels (3)
# The dtype of teh Image Tensor has to be float32 for mobilenet model
MODEL_NAME = 'mobilenet_v2_140_224'
HEIGHT, WEIGHT, CHANNELS = 224, 224, 3
DTYPE = tf.float32
MODULE_HANDLE = "https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/4"
#################################################

def load_img(path):
    """
    input:
        path (str): Image Path
    output:
        tf.tensor: A Tensor of the Transformed Image
    This function:
    Loads the JPG image at the given path
    Decodes the JPG image to a uint8 W X H X 3 tensor
    Resizes the image based on the Constants
    Returns the pre processed image tensor
    """
    img = tf.io.read_file(path)

    img = tf.io.decode_jpeg(img, channels=CHANNELS)

    img = tf.image.resize_with_pad(img, HEIGHT, WEIGHT)

    img  = tf.image.convert_image_dtype(img, DTYPE)[tf.newaxis, ...]

    return img

#################################################

def get_image_feature_vectors(jpg_list, out_path, track_vectorizer_time):
    """
    input:
        image_dir_path (string): path to the directory containing the set of images
            to be vectorized
        track_vecorizer_time: tracker object to track time from the begining of the run
        session: timestamp to note the session accordingly
    output:
        session: The output is noted in a session folder created during the run of the program
        files:
            data/<session>/reporting/images_set.json: Notes the indices of the files, their name and path.
            data/<session>/vectors/vector_matrix.npz: File containing all the image vectors verticaly stacked.
    This function:
    Loads the a model from TF.HUB
    Makes an inference for all images stored in a local folder
    Saves each of the feature vectors in a file
    """
    # Creates New Session Folders if not exist

    print(f"[INFO] Model {MODEL_NAME} - Loading Started @ {time_util.timestamp()}")

    # Load the module
    module = hub.load(MODULE_HANDLE)

    print(f"[INFO] Model {MODEL_NAME} - Loading Completed @ {time_util.timestamp()}")

    print(f"--- {track_vectorizer_time.total_time()} seconds passed ---------")
    
    print(f"[INFO] Generating Feature Vector Matrix - Started @ {time_util.timestamp()}\n")

    total = len(jpg_list)
    # Loops through all images in the given folder
    for i, filename in enumerate(jpg_list): #assuming gif

        # Loads and pre-process the image
        img = load_img(str(filename))

        # Calculate the image feature vector of the img
        features = module(img)   
    
        # Remove single-dimensional entries from the 'features' array
        feature_set = np.squeeze(features)  

        if i == 0:
            # Initialize Vector Matrix
            vector_matrix = feature_set
        else:
            # Add Image Vector to Vector Matrix
            vector_matrix = np.vstack([vector_matrix, feature_set])

        # Add Image index, name and img_path to Data Structure
        # file_dict = {
        #     'index': i,
        #     'file_name': filename.stem,
        #     'img_path': str(filename)
        # }

        # file_list.append(file_dict)

        paths_util.printProgressBar(i + 1, total)

    print(f"[INFO] Generating Feature Vectors - Completed @ {time_util.timestamp()}")

    print(f"--- {track_vectorizer_time.total_time()} seconds passed ---------")

    out_path = Path(out_path)

    (out_path / 'vectors').mkdir(parents=True, exist_ok=True)

    # Saves the image feature vectors into a file for later use

    np.savetxt(out_path / f'vectors/{MODEL_NAME}_vector_matrix.npz', vector_matrix, delimiter=',')

    return str(out_path / f'vectors/{MODEL_NAME}_vector_matrix.npz')

if __name__ == "__main__":

    print('--------------- This is a Dry Run ---------------')
    jpg_list = list(Path("data/raw/orignal_images").glob("*.jpg"))
    vector_matrix_path = get_image_feature_vectors(jpg_list, "data/vectors", time_util.time_tracker())

    print(f"Vector Matrix Creates as: {vector_matrix_path}")