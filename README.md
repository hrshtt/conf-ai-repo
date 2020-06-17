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
    4. Running the above will create a new session in `data\main_run`
    5. If any other scripts are running the data will be output in `data\dry_run`
