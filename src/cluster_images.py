"""
This script reads image feature vectors from a folder
and saves the image similarity scores in json file
"""

import numpy as np
import time
import glob
import os.path
import json
import pandas as pd
import itertools
from annoy import AnnoyIndex
from scipy import spatial
from collections import defaultdict

def cluster():
    images_set = pd.read_json('data/reporting/images_set.json')
    start_time = time.time()

    print("--"*25)
    print(f"ANNOY index generation - Initilaized at {time.ctime()}")
    print("--"*25)

    # Defining data structures as empty dict
    file_dict = defaultdict(dict)

    vector_matrix = np.loadtxt('data/vectors/vector_matrix.npz', delimiter=',')

    # Configuring annoy parameters
    dims = vector_matrix.shape[1]
    n_nearest_neighbors = 10
    trees = 10000
    threshold = 0.95

    final_list = []

    # Reads all file names which stores feature vectors

    t = AnnoyIndex(dims, metric='angular')


    for i in range(len(images_set)):

        # Assigns file_name, feature_vectors and corresponding product_id
        file_name = str(images_set.iloc[i]['file_name'])

        file_vector = vector_matrix[i]

        file_dict[i]['vector'] = file_vector
        file_dict[i]['file_name'] = file_name
        file_dict[i]['img_path'] = str(images_set.iloc[i]['img_path'])

        final_list.append(set([file_dict[i]['file_name']]))

        # Adds image feature vectors into annoy index   
        t.add_item(i, file_vector)

        print("---------------------------------")
        print(f"Annoy index     : {i}")
        print(f"Image file name : {file_name}")
        print(f"--- {((time.time() - start_time)/60)} minutes passed ---------")

    # Builds annoy index

    print("ANNOY index generation - Finished")


    print("Building Tree from ANNOY indices - started")

    t.build(trees)

    print("Building Tree from ANNOY indices - Finished")

    print("Similarity score calculation - Started ") 
    
    named_nearest_neighbors = []

    # Loops through all indexed items
    for i in file_dict:

        # Calculates the nearest neighbors of the master item
        nearest_neighbors = t.get_nns_by_item(i, n_nearest_neighbors)

        nearest_neighbors_dict = {
            'file_name': file_dict[i]['file_name'],
            'img_path': str(images_set.iloc[i]['img_path']),
            'nearest_neigbors': []
        }

        # Loops through the nearest neighbors of the master item
        for j in nearest_neighbors:

            # Calculates the similarity score of the similar item
            similarity = 1 - spatial.distance.cosine(file_dict[i]['vector'], file_dict[j]['vector'])
            rounded_similarity = int((similarity * 10000)) / 10000.0

            # Appends master product id with the similarity score 
            # and the product id of the similar items
            if similarity >= threshold and similarity!= 1:
                nearest_neighbors_dict['nearest_neigbors'].append({
                    'file_name': file_dict[j]['file_name']
                    , 'similarity': float(rounded_similarity)
                    , 'img_path': str(images_set.iloc[j]['img_path'])
                    })

                for set_ in final_list:
                    if file_dict[i]['file_name'] in set_:
                        set_.add(file_dict[j]['file_name'])

        if len(nearest_neighbors_dict['nearest_neigbors']) != 0:
            named_nearest_neighbors.append(nearest_neighbors_dict)

        print("---------------------------------") 
        print("Similarity index       : %s" %i)
        print("Master Image file name : %s" %file_dict[i]['file_name']) 
        print("Nearest Neighbors.     : %s" %nearest_neighbors) 
        print("--- %.2f minutes passed ---------" % ((time.time() - start_time)/60))

    
    print ("Step.2 - Similarity score calculation - Finished ") 

    final_list.sort()
    final_list = list(final_list for final_list, _ in itertools.groupby(final_list))
    final_list = [list(item) for item in final_list if len(item) > 1]

    # Writes the 'named_nearest_neighbors' to a json file
    with open('data/reporting/optimized_clusters.json', 'w') as out:
        json.dump(final_list, out, indent=4)

    with open('data/reporting/nearest_neighbors.json', 'w') as out:
        json.dump(named_nearest_neighbors, out, indent=4)

    print("--- Process completed in %.2f minutes ---------" % ((time.time() - start_time)/60))

cluster()