# Image Viewer for AI-Cull-Duplicates

A simple flask app to view images from AI-Cull-Duplicates

_Note: It would be better to keep the virtual enviornments of both Ai-Cull-Duplicates and imageviewer seperate. We suggest a new venv is created to handle it._

    1. Create a virtual enviornment to install libraries related to **AI_Cull_Duplicates**
        * Run `python3 -m venv <name of virtual env>`
        * linux: Run source `<name of virtual env>/bin/activate`
        * windows: Run `<name of virtual env>\env\Scripts\activate.bat`
    2. Run `pip install -r imageviewer\requirements.txt`
    3. Run `python imageviewer\app.py`
    4. The Application will diplay the session names present in `data\main_run`
    5. Click on any session and view images as sorted by their similarity.
    6. Use the above arrow keys to navigate to previous or next cluster.
    7. Use the Search bar to find specific clusters using their index.

```
.
├── data
│   ├── dry_run                         -> Folder which stores the output when scripts are run outside app.py
│   ├── main_run                        -> Folder which stores the output when app.py is run, each run gets its own session
│   │   ├── 2020-06-17_19-14-57         -> A Session
│   │   │   ├── reporting
│   │   │   └── vectors
│   │   └── 2020-06-17_21-22-44
│   ├── processed                       -> Folder contains
│   │   └── transformed_images
│   ├── raw
│   │   └── orignal_images
│   ├── reporting
│   └── vectors
├── imageviewer
│   └── templates
├── notebooks
├── old_dir
│   ├── libraw
│   └── poc
│       └── model
│           └── imagenet
└── src
```

![alt text](http://url/to/img.png)