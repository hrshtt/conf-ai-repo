# AI-Cull-Duplicates
# Image Clustering

This is the initial phase of the Repo, the structure is subject to change eventually.

```
.
├── data                            <- contains all mutable and immutable data sources
│   ├── dry_run                     <- output for test runs (when scripts are run outside app.py)
│   ├── main_run                    <- output for session for each run of app.py
│   │   ├── 2020-06-17_19-14-57     <- a single session
│   │   └── 2020-06-17_19-21-25
│   ├── processed                   <- data that has gone through some processessing
│   │   └── transformed_images      <- images after being pre-processed
│   ├── raw                         <- immutable data
│   │   └── orignal_images          <- orignal test images to be kept here
│   ├── reporting                   <- data used to record and report changes (when scripts are run outside app.py)
│   └── vectors                     <- vectors data (when scripts are run outside app.py)
├── imageviewer                     <- flask application to see session output, requires flask
│   └── templates
├── notebooks
├── old_dir                         <- experimental code, to test things quickly, requires jupyter
│   └── poc                         <- old Repo
└── src                             <- the final script files
```

### Instructions to Run the Code:
_Note: Instructions to run the flask application are seperate, open **imageviewer** folder to continue with that._

    1. Create a virtual enviornment to install libraries related to **AI_Cull_Duplicates**
        * Run `python3 -m venv <name of virtual env>`
        * linux: Run source `<name of virtual env>/bin/activate`
        * windows: Run `<name of virtual env>\env\Scripts\activate.bat`
    2. Run `pip install -r requirements.txt`
    3. Run `python src\app.py <Path to Image Directory>`
       * The main application runs via app.py, which is implemented with the idea of a session's run.
       * The session Class is the main entry to the application.
       * The session class controls two major logical stages of the appication:
         * preprocessing via the session.preprocess() method.
         * main_run via the session.start_main_run() method.
    4. Running the above will create a new session in `data\main_run`
    5. If any other scripts are running the data will be output in `data\dry_run`


### Points to be noted:

    * Overhauled src/app.py design to accomodate extensibility.
    * Added Decorators to perform time keeping, and performance measurement.
    * Made src/app.py functionally 1:1 with old_dir/poc/app.py.
    * Divided the app into 2 parts preprocessing and main_run
      * Preprocessing Part engages in a lot of I/O related to images and other files
      * Preprocessing Part has been implemented with multiprocessing. [speed boost of 5x - 10x observed]
      * For testing and development, preprocessing part uses custom mode for writing files
      * main_run Part engages in the functional goal of the application, like getting vector representation and clustering images.
    * Added keep_images and cluster_index columns to dataframe
    * optimized_clusters json is written in two flavors: "optimized_clusters_one.json" and "optimized_clusters_all.json"
    * imageviewer only supports optimized_clusters_all.json for now.
    * Each module [like: resize.py, normalize_histogram.py, dng_to_jpg.py etc] is given an interface with the create_session class
    * This'll make it easy to keep logic seperate for all modules and then customizing interface for main application run inside src/app.py.


## Logical Structure of session class

#### Methods:

    * queue_images
        Gets all files from directory and populates a pandas df using the acquired data. 
    * preprocess
        Contains the preprocessing pipeline as required by the application. Runs preprocessing pipeline amd applies preprocessing steps sequentially.
      * run_dng_to_jpg
        Wrapper method to run scripts from dng_to_jpg. Ran by preprocess method.
      * run_normalize_histogram
        Wrapper method to run scripts from normalize_histogram. Ran by preprocess method.
      * run_resize
        Wrapper method to run scripts from resize. Ran by preprocess method.
    * start_main_run
        Maintains the main functional code of the application. Runs the code sequentially to get expected outcome.
      * run_get_vectors
        Wrapper method to run scripts from get_vectors. Ran by start_main_run method.
      * run_cluster_images
        Wrapper method to run scripts from cluster_images. Ran by start_main_run method.
    * save_csv
        Utility method which saves csv files from a pandas dataframe, to the current session/reporting folder.

#### Variables:
    * session
        A timestamp string, with the same use as run_at variable of POC. 
    * images_dir
        Directory given as the main input to the script.
    * session_out_path
        Path to the directory of current session outputs.
    * images_dataframe
        Pandas DataFrame which contains all house keeping values and refrences.
    * total
        Total number of files in the directory.
    * preprocess_flag
        Boolean Variable turns to true if preprocessing was done. 
    * resize_max_length
        A Value used by scripts from resize.py. Currently controlled by constant RESIZE_MAX_LENGTH.
    * similarity_threshold
        A Value used by scripts from cluster_images.py. Currently controlled by constant SIMILARITY_THRESHOLD.

