from flask import Flask, render_template, request, redirect, url_for
import requests
from pager import Pager
from pandas import read_json
import numpy as np
import json
from pathlib import Path

def read_table(path):
    """Return a list of dict"""
    # r = requests.get(url)
    with open(path) as f:
        json_data = json.load(f)
        for cluster in json_data:
            for row in cluster:
                row['jpg_path'] = row['jpg_path'].replace("data/", '')
        return json_data

APPNAME = "ImageViewer"
STATIC_FOLDER = '../data'
# TABLE_FILE = "../AI-Cull-Duplicates/data/reporting/optimized_clusters.json"
# Getting all sessions where optimized_clusters.json exists.
temp_sessions = [session for session in list(Path("data/main_run").glob("*")) if len(list(session.glob("reporting/optimized_clusters.json"))) ]

SESSIONS = {session.stem: str(list(session.glob("reporting/optimized_clusters.json"))[0]) for session in temp_sessions}

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.update(
    APPNAME=APPNAME,
    )

@app.route('/')
def index():
    return render_template(
        'sessionsview.html',
        sessions=SESSIONS
    )

@app.route('/<sess>/<int:ind>/')
def image_view(sess = None, ind=None):
    if sess not in SESSIONS.keys():
        return render_template("404.html"), 404

    table = read_table(SESSIONS[sess])
    # print(len(table))
    pager = Pager(len(table))
    if ind >= pager.count:
        return render_template("404.html"), 404
    else:
        pager.current = ind
        return render_template(
            'imageview.html',
            index=ind,
            pager=pager,
            cluster=table[ind],
            sess=sess)

@app.route('/goto', methods=['POST', 'GET'])    
def goto():
    return redirect(f"/{request.form['session']}/{request.form['index']}")
    
if __name__ == '__main__':
    app.run(debug=True)
