from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
import json
from collections import defaultdict

df = pd.read_json('/data/reporting/images_set.json')

vector_matrix = np.loadtxt('data/vectors/vector_matrix.npz', delimiter=',')

print(f'Got {len(df)} of {len(df)} the vectors!')

clustering = DBSCAN(eps=10, min_samples=2).fit(vector_matrix)

clusters = defaultdict(list)

for i, val in enumerate(clustering.labels_):
    
    clusters[int(val)].append(str(int(df.iloc[i]['file_name'])))

print(f'Got {len(set(clustering.labels_))} of {len(set(clustering.labels_))} Clusters!')

del clusters[-1]

with open('nearest_neighbors_1.json', 'w') as out:
    json.dump(clusters, out, indent=4)