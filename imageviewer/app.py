from flask import Flask, render_template, request, redirect, url_for
import requests
from pager import Pager
from pandas import read_json
import numpy as np
import json
from pathlib import Path
from pprint import pprint

def read_table(path):
    """Return a list of dict"""
    # r = requests.get(url)
    with open(path) as f:
        json_data = json.load(f)
        for row in json_data:
            for image in row['cluster']:
                jpg_path = Path(image['jpg_path'])
                # removing data/ from all paths for working with flask STATIC FOLDER
                image['jpg_path'] = str(Path(*jpg_path.parts[1:]))
    return json_data

APPNAME = "ImageViewer"
STATIC_FOLDER = '../data'

# Getting all sessions where any optimized_clusters json exists (all/one).
temp_sessions = [session for session in list(Path("data/main_run").glob("*")) if len(list(session.glob("reporting/optimized_clusters*.json"))) ]

SESSIONS = {session.stem: str(list(session.glob("reporting/optimized_clusters*.json"))[0]) for session in temp_sessions}

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
            cluster=table[ind]['cluster'],
            sess=sess)

@app.route('/goto', methods=['POST', 'GET'])    
def goto():
    return redirect(f"/{request.form['session']}/{request.form['index']}")
    
if __name__ == '__main__':
    app.run(debug=True)
