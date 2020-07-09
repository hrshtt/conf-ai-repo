#################################################
import time_util
import normalize_histogram
import get_vectors
import cluster_images
import dng_to_jpg
import resize
import paths_util

import pandas as pd
from pathlib import Path
import sys
from itertools import repeat
import multiprocessing as mp
import json
#################################################

INDEX = 'index'
KEY = 'key'
FILE_NAME = 'file_name'
FILE_PATH = 'file_path'
JPG_PATH = 'jpg_path'
FEATURES = 'Features'
VECTOR = 'Vector'
CLUSTER_INDEX = 'cluster_index'
CONVERT_JPG_PATH = 'convert_jpg_path'
SCALED_JPG_PATH = 'scaled_jpg_path'
NORMALIZED_JPG_PATH = 'normalized_jpg_path'
KEEP_IMAGE = 'keep_image'

RESIZE_MAX_LENGTH = 1800
SIMILARITY_THRESHOLD = 0.95

#################################################

# Initializing a checkpoint_tracker to get performance stats
track_checkpoints = time_util.checkpoint_tracker()

# The Decorator @time_util.checkpoint_tracker().create_checkpoint("header_here")
# adds a checkpoint as seen in the code below.
# Each checkpoint stage should be defined by a unique header.
# This header holds the total time usage of the function the
# Decorator w the unique header is placed on.
# The performance stats can be accessed by:
# checkpoint_tracker().get_performance() which returns a dict.

# Syntactic Sugar to make a prettier decorator
create_checkpoint = track_checkpoints.create_checkpoint


class create_session:
    def __init__(self, images_dir):
        self.print_start()
        self.session = time_util.timestamp_simple()
        self.tracker = time_util.time_tracker()
        print(
            f'--- New Session: {self.session }, Created for Directory: {images_dir} ---')
        self.images_dir = images_dir
        self.session_out_path = Path("data") / "main_run" / self.session
        self.images_dataframe = self.queue_images(images_dir)
        self.total = len(self.images_dataframe)

        self.images_dataframe[JPG_PATH] = self.images_dataframe[FILE_PATH]

        self.preprocess_flag = False

        self.resize_max_length = RESIZE_MAX_LENGTH
        self.similarity_threshold = SIMILARITY_THRESHOLD

    @create_checkpoint("queue_images")
    def queue_images(self, files_dir):
        """
        input:
            files_dir: Path to the Directory containing files/images.
        output: 
            images_dataframe with values initialized
        """
        files_dir = Path(files_dir)

        total = len(list(files_dir.glob("*")))

        print(f"[INFO] Running queue_images for session: {self.session}\n")
        temp_list = []
        for i, image_path in enumerate(files_dir.glob("*")):
            temp_list.append([i, image_path.stem,
                              image_path.name, str(image_path), str(image_path)])
            paths_util.printProgressBar(i+1, total)
        images_dataframe = pd.DataFrame(
            data=temp_list,
            columns=[INDEX, KEY, FILE_NAME, FILE_PATH, JPG_PATH])

        return images_dataframe

    @create_checkpoint("preprocessing")
    def preprocess(
        self,
        mode="hard overwrite",
        dng_convert_flag=True,
        normalize_histogram_flag=True,
        resize_max_length = RESIZE_MAX_LENGTH,
        resize_flag=True
    ):
        """
        input:
            mode [default = "hard overwrite"]: an option to select the way preprocessed output is generated.
                "hard overwrite" -> Does not care about session, dumps and overwrites 
                    all files into: data/processed
                "soft overwrite" -> Takes Session into account, but dumps and overwrites 
                    files into: data/<session>/processed
                "no overwrite" -> Consumes the most disk space, creates a new folder for 
                    each preprocessing step and stores all images at each step
        output:
            stores list of jpg paths for each file in self.imagedataframe["jpg_path"]
        """
        self.preprocess_flag = True

        file_list = self.images_dataframe[FILE_PATH]

        out_path = self.session_out_path / "processed"

        # Defining a pipeline
        # Each step or function is made of a single dictionary
        # Add new steps and fill all values
        # name -> name of the step
        # flag -> variable to boolean controlling weather the step is run or not
        # function -> create a function inside the class and add its refrence here
        # out_path -> default out_path for "no overwrite", unique path to a folder
        #   inside data/main_run/<session>/processed/<new step folder>
        # key -> key for storing list of paths inside self.images_dataframe

        pipeline = [
            {"name": "dng_to_jpg",
                "flag": dng_convert_flag,
                "function": self.run_dng_to_jpg,
                "out_path": str(out_path / "converted_images"),
                "key": CONVERT_JPG_PATH
             },
            {"name": "normalize_histogram",
                "flag": normalize_histogram_flag,
                "function": self.run_normalize_histogram,
                "out_path": str(out_path / "normalized_images"),
                "key": NORMALIZED_JPG_PATH
             },
            {"name": "resize",
                "flag": resize_flag,
                "function": self.run_resize,
                "out_path": str(out_path / "resized_bw_images"),
                "key": SCALED_JPG_PATH
             }
        ]

        steps_name = '\n\t-> '.join([step['name'] for step in pipeline])
        print(
            f"[INFO] Running preprocess() with mode = \"{mode}\" and steps: \n\t-> {steps_name}")

        if mode.lower() == "hard overwrite":
            out_path = Path("data") / "processed" / "transformed_images"
            for step in pipeline:
                if step["flag"]:
                    jpg_path_list = step["function"](file_list, str(out_path))
                    file_list = jpg_path_list

        elif mode.lower() == "soft overwrite":
            out_path = self.session_out_path / "processed"
            for step in pipeline:
                if step["flag"]:
                    jpg_path_list = step["function"](file_list, str(out_path))
                    file_list = jpg_path_list

        elif mode.lower() == "no overwrite":
            # default value in pipeline is for no overwrite.
            for step in pipeline:
                if step["flag"]:
                    jpg_path_list = step["function"](
                        file_list, step['out_path'])
                    file_list = jpg_path_list
                    self.images_dataframe[step["key"]] = jpg_path_list

        else:
            print(
                f"[ERROR] Wrong Choice Selected for preprocess(mode = '${mode}').\n${mode} is not a choice.")
            exit(0)

        # # Running all functions inside the pipeline
        # for step in pipeline:
        #     if step["flag"]:
        #         jpg_path_list = step["function"](file_list, step['out_path'])
        #         file_list = jpg_path_list

        self.images_dataframe[JPG_PATH] = jpg_path_list

        self.save_csv(self.images_dataframe, "images_dataset.csv")

    @create_checkpoint("dng_to_jpg_convert")
    def run_dng_to_jpg(self, file_list, out_path):
        if any([file_.endswith(".dng") for file_ in file_list]):

            out_path = Path(out_path)
            out_path.mkdir(exist_ok=True, parents=True)

            print(f"[INFO] Running dng_to_jpg for session: {self.session}\n")

            with mp.Pool(mp.cpu_count()) as p:
                jpg_path_list = p.starmap(resize.resize_image, zip(
                    file_list, repeat(str(out_path))))

            # jpg_path_list = []
            # for i, file_path in enumerate(file_list):
            #     jpg_path_temp = dng_to_jpg.convert(
            #         file_path, str(out_path))  # dng path
            #     jpg_path_list.append(jpg_path_temp)
            #     paths_util.printProgressBar(i+1, self.total)

            return jpg_path_list
        else:
            print(
                f"[INFO] NO .dng files found in directory for Session: {self.session}")
            print("[INFO] Skipping dng_to_jpg_convert")
            return file_list

    @create_checkpoint("normalize_histogram")
    def run_normalize_histogram(self, jpg_path_list, out_path):
        out_path = Path(out_path)
        out_path.mkdir(exist_ok=True, parents=True)
        print(
            f"[INFO] Running normalize_histogram for session: {self.session}\n")
        new_jpg_list = []

        with mp.Pool(mp.cpu_count()) as p:
            new_jpg_list = p.starmap(normalize_histogram.normalize_image, zip(
                jpg_path_list, repeat(str(out_path))))

        # for i, jpg_path in enumerate(jpg_path_list):
        #     new_jpg_path = normalize_histogram.normalize_image(
        #         jpg_path, str(out_path))
        #     new_jpg_list.append(new_jpg_path)
        #     paths_util.printProgressBar(i+1, self.total)

        return new_jpg_list

    @create_checkpoint("resize_images")
    def run_resize(self, jpg_path_list, out_path):

        out_path = Path(out_path)
        out_path.mkdir(exist_ok=True, parents=True)

        print(f"[INFO] Running resize_images for session: {self.session}\n")

        new_jpg_path_list = []

        with mp.Pool(mp.cpu_count()) as p:
            new_jpg_path_list = p.starmap(resize.resize_image, zip(
                jpg_path_list, repeat(str(out_path)), repeat(self.resize_max_length)))

        # for i, jpg_path in enumerate(jpg_path_list):
        #     new_jpg_path = resize.resize_image(jpg_path, str(
        #         out_path), self.resize_max_length)  # jpg path
        #     new_jpg_path_list.append(new_jpg_path)
        #     paths_util.printProgressBar(i+1, self.total)

        return new_jpg_path_list

    @create_checkpoint("main_run")
    def start_main_run(self, cluster_output='all'):
        """
        Runs Main Application Functions
        """

        if not self.preprocess_flag:
            print(
                "[WARNING] Preprocessing has not been done, might lead to Unexpected results.")
            if any([file_.endswith(".dng") for file_ in self.images_dataframe[JPG_PATH].to_list()]):
                print(f"[ERROR] .dng file found inside {self.images_dir}")
                print(
                    "[INFO] Run preprocess with dng_convert_flag = True and Try Again.")
                exit(0)

        # Gets Vector Matrix from get_vectors
        vector_matrix_path = self.run_get_vectors(
            self.tracker)

        # Passes Vectors to cluster_images, and Adds Cluster
        # Indices to images_dataframe
        self.run_cluster_images(
            vector_matrix_path,
            cluster_output)

        # Save CSV
        self.save_csv(self.images_dataframe, "images_dataset.csv")

        self.print_end()

    @create_checkpoint("get_vectors")
    def run_get_vectors(self, tracker):
        jpg_path_list = self.images_dataframe[JPG_PATH].to_list()
        out_path = str(self.session_out_path)
        return get_vectors.get_image_feature_vectors(jpg_path_list, out_path, tracker)

    @create_checkpoint("cluster_vectors")
    def run_cluster_images(self, vector_matrix_path, cluster_output):
        out_path = self.session_out_path / "reporting"

        # Run cluster images and get cluster index list and optimized cluster indices
        cluster_index_list, optimized_clusters_indices, similarity_list = cluster_images.cluster(
            vector_matrix_path,
            str(out_path),
            self.similarity_threshold,
            self.tracker
        )

        # Save optimized clusters with Image Key and Image JPG Path
        # More data can be appended to each cluster unit as required
        write_list = []
        for cluster_indices in optimized_clusters_indices:
            temp_list = []
            for index in cluster_indices:

                temp_dict = {
                    KEY: self.images_dataframe.loc[index][KEY],
                    JPG_PATH: self.images_dataframe.loc[index][JPG_PATH]
                    # Append more data here as required.
                }

                if cluster_output == 'one':
                    temp_list = temp_dict
                    break

                elif cluster_output == 'all':
                    temp_list.append(temp_dict)

                else:
                    print(f"[ERROR] Wrong Choice, No such input for cluster_output: {cluster_output}")
                    print(f"[INFO] Use cluster_output with: \"all\" or \"one\"")
                    print(f"[WARNING] Changing cluster_output to default \"all\" for now.")
                    cluster_output = 'all'
                    temp_list.append(temp_dict)

            write_list.append(temp_list)

        out_path.mkdir(exist_ok=True, parents=True)
        # Save Usable Optimized Clusters
        with open(out_path / f"optimized_clusters_{cluster_output}.json", "w") as f:
            json.dump(write_list, f, indent=4)

        self.images_dataframe[CLUSTER_INDEX] = cluster_index_list

        # Initializing T/F list for images as False
        keep_image_list = [False]*self.total 

        # For only the FIRST Index of each Cluster Make Value True
        for cluster_indices in optimized_clusters_indices:
            for index in cluster_indices:
                keep_image_list[index] = True
                break
        
        self.images_dataframe[KEEP_IMAGE] = keep_image_list

    def save_csv(self, dataframe, csv_file_name):
        """
        Saves a CSV inside a session, taking in a DataFrame, and CSV file Name
        """
        out_path = Path(self.session_out_path) / "reporting"
        out_path.mkdir(exist_ok=True, parents=True)
        dataframe.to_csv(out_path / csv_file_name)

    def print_end(self):
        print("\n")
        print('*******************************************')
        print('*************** PROGRAM END ***************')
        print('*******************************************')

    def print_start(self):
        print('*********************************************')
        print('*************** PROGRAM START ***************')
        print('*********************************************')
        print("\n")


if __name__ == "__main__":
    args = sys.argv  # take in args from system
    arg_len = len(args)  # check how many args came in

    # Set arg_path if there are args
    if (len(args) >= 2):
        arg_path = args[1]  # sets arg path for use later

    # arg index 0 is filename, index 1 is the first option. If no args explain correct usage
    if (arg_len != 2):
        # Explain correct usage
        print("\n")
        print(time_util.timestamp(
        ) + '[ERROR] No path given, correct usage: Python3 %s $image_directory' % args[0])
        print(time_util.timestamp(
        ) + '[Example] Python3 app.py /Applications/XAMPP/xamppfiles/htdocs/AI-Cull/images/dngs-structured-small')
        quit()  # quit program if being used incorrectly

    track_total_time = time_util.time_tracker()  # start tracking time

    # Print path given
    print(time_util.timestamp() + '[INFO] You gave directory path:' + arg_path)
    print("\n")
    print('****'*20)

    new_session = create_session(arg_path)

    # new_session.preprocess()

    new_session.start_main_run(cluster_output = "one")

    performance = track_checkpoints.get_performance()

    performance_df = pd.DataFrame(
        data=[performance.values()], columns=performance.keys())

    new_session.save_csv(performance_df, "performance.csv")
