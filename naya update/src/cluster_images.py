"""
This script reads image feature vectors from a folder
and saves the image similarity scores in json file
"""
import numpy as np
import time_util
from pathlib import Path
import json
import pandas as pd
import itertools
from annoy import AnnoyIndex
from scipy import spatial
from collections import defaultdict
import paths_util
import sys


def dfs(adj_list, visited, vertex, result, key):
    visited.add(vertex)
    result[key].append(vertex)
    for neighbor in adj_list[vertex]:
        if neighbor not in visited:
            dfs(adj_list, visited, neighbor, result, key)

def run_dfs(cluster_edges):

    clusters_list = defaultdict(list)
    adj_list = defaultdict(list)
    visited = set()

    for x, y in cluster_edges:
        adj_list[x].append(y)
        adj_list[y].append(x)

    for vertex in adj_list:
        if vertex not in visited:
            dfs(adj_list, visited, vertex, clusters_list, vertex)

    return clusters_list
    

def cluster(vector_matrix_path, 
            out_path,
            similarity_threshold,
            cluster_tracker
            ):
    """
    input:
        vector_matrix_path (string): Path to vector matrix of images vectors;s file of type .npz
        out_path (string): Path where output is to be stored.
        similarity_threshold (float) [range 0 - 1.0]: Threshold to consider image to be a duplicate
        cluster_tracker (time_util.tracker()): time tracker for time keeping
    output:
        creates a file in <out_path>/reporting to store cluster indices.
    """

    vector_matrix = np.loadtxt(vector_matrix_path, delimiter=',')
    total, dims = vector_matrix.shape

    # Configuring annoy parameters
    n_nearest_neighbors = 10
    trees = 10000
    threshold = similarity_threshold

    # Reads all file names which stores feature vectors
    t = AnnoyIndex(dims, metric='angular')

    print(f"[INFO] ANNOY index generation - Initilaized at {time_util.timestamp()}")

    print(f"[INFO] Similarity Threshold = {similarity_threshold}\n")

    for i in range(total):
        file_vector = vector_matrix[i]
        t.add_item(i, file_vector)
        paths_util.printProgressBar(i + 1, total)

    print(f"[INFO] ANNOY index generation - Finished at {time_util.timestamp()}")

    print(f"[INFO] Building Tree from ANNOY indices - Initilaized at {time_util.timestamp()}")

    # Builds annoy index
    t.build(trees)

    print(f"[INFO] Building Tree from ANNOY indices - Finished at {time_util.timestamp()}")

    print(f"[INFO] Building Tree from ANNOY indices - Finished in {cluster_tracker.total_time()}s")

    print(f"[INFO] Similarity score calculation - Started {time_util.timestamp()}\n") 
    
    similarity_util = {}

    cluster_edges = []

    for i in range(total):

        # Calculates the nearest neighbors of the master item
        nearest_neighbors = t.get_nns_by_item(i, n_nearest_neighbors)

        # Loops through the nearest neighbors of the master item
        for j in nearest_neighbors:

            # Calculates the similarity score of the similar item
            similarity = 1 - spatial.distance.cosine(vector_matrix[i], vector_matrix[j])
            rounded_similarity = int((similarity * 10000)) / 10000.0

            # Appends master product id with the similarity score 
            # and the product id of the similar items
            if similarity >= threshold and similarity != 1:
                cluster_edges.append((i, j))

                if i >= j:
                    similarity_util[(j, i)] = rounded_similarity
                else:
                    similarity_util[(i, j)] = rounded_similarity

        paths_util.printProgressBar(i + 1, total)

    try:
        print("[INFO] Running DFS on Cluster Images to Form Final Clusters.")
        clusters_list = run_dfs(cluster_edges)
        
    except RecursionError:
        # Increasing Recursion Limit and running again
        print("[WARNING] Recursion Limit Reached.")
        print("[INFO] Increasing Recursion Limit and Running again.")
        sys.setrecursionlimit(sys.getrecursionlimit()**2)

        clusters_list = run_dfs(cluster_edges)


    clusters_list = [clusters_list[key] for key in clusters_list]

    # print([result[key] for key in result])
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(out_path / 'optimized_cluster_index.json', 'w') as out:
        json.dump(clusters_list, out, indent=4)

    cluster_list_w_indieces = [-1]*total
    cluster_index_util = 0
    for cluster_ in clusters_list:
        for index in cluster_:
            cluster_list_w_indieces[index] = cluster_index_util
        cluster_index_util += 1
    return cluster_list_w_indieces, clusters_list, similarity_util

if __name__ == "__main__":
    print('--------------- This is a Dry Run ---------------')
    cluster_tracker = time_util.time_tracker()

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
    session = time_util.timestamp_simple()
    result, cluster_list, similarity_util = cluster(arg_path, Path('data/dry_run') / session, 0.95, time_util.time_tracker)
    print(result, cluster_list, similarity_util)
