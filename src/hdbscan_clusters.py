import hdbscan
import numpy as np

vector_matrix = np.loadtxt('data/vectors/vector_matrix.npz', delimiter=',')

model = hdbscan.HDBSCAN(cluster_selection_epsilon = 10).fit(X=vector_matrix)

print(set(model.labels_))