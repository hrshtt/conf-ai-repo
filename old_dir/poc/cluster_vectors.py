from annoy import AnnoyIndex
from nltk import ngrams
import numpy as np
import random, json, glob, os, codecs, random
from scipy import spatial
from shutil import copyfile
import time_util

# data structures
file_index_to_file_name = {}
file_index_to_file_vector = {}
chart_image_positions = {}

# config
dims = 2048
n_nearest_neighbors = 30
trees = 10000
infiles = glob.glob('image_vectors/*.npz')

def nearest_neighboors( run_at, list_data, csv_columns, top_x_likeness, top_x_limit ):

  # create a nearest neighbors json folder for output into

  # create the output/run_at folder if it does not exist
  if not os.path.exists('output/' + run_at + '/nearest_neighbors'):
    # print(time_util.timestamp() + "[INFO] Missing output/run_at/nearest_neighbors folder, creating it...")
    os.makedirs('output/' + run_at + '/nearest_neighbors')

  # create the output/run_at folder if it does not exist
  if not os.path.exists('output/' + run_at + '/duplicates'):
    # print(time_util.timestamp() + "[INFO] Missing output/run_at/nearest_neighbors folder, creating it...")
    os.makedirs('output/' + run_at + '/duplicates')

  list_old = list_data # save old data if needed

  t = AnnoyIndex(dims) # inititialize annoy 
  i = 0 # iterator 

  #print(time_util.timestamp() + "[INFO] Building ANNOY Index...")
  # Build ANN Index from list_data
  for row in list_data:
    file_vector = np.loadtxt(row[csv_columns.index('Vector')]) # the actual vector
    file_name = os.path.basename(row[csv_columns.index('Vector')]).split('.')[0] # where is vector
    file_index_to_file_name[i] = file_name
    file_index_to_file_vector[i] = file_vector
    t.add_item(i, file_vector)
    #print(time_util.timestamp() + "[INFO] Added: Index=" + str(i) + " Vector=" + str(file_vector))
    i = i + 1

  t.build(trees) # build annoy tree
  #print(time_util.timestamp() + "[INFO] ANNOY Index Built")

  i = 0 # iterator
  for row in list_data:

    file_being_checked = row[csv_columns.index('Key')] # what file are we checking
    #print(time_util.timestamp() + "[INFO] Getting Nearest Neighbors...")
    named_nearest_neighbors = [] # initialize response PER VECTOR
    master_file_name = os.path.basename(row[csv_columns.index('Vector')]).split('.')[0] # vector path
    master_vector = np.loadtxt(row[csv_columns.index('Vector')]) # original vector values

    nearest_neighbors = t.get_nns_by_item(i, top_x_likeness) # compare against t return list

    #print(time_util.timestamp() + "[INFO] Nearest Neighbors found: " + str(nearest_neighbors))

    #print(nearest_neighbors)

    for j in nearest_neighbors:
      neighbor_file_name = file_index_to_file_name[j] # define name to response
      neighbor_file_vector = file_index_to_file_vector[j] # given index J what is the original vector file

      #print("Looking for neighboor: " + neighbor_file_name)

      similarity = 1 - spatial.distance.cosine(master_vector, neighbor_file_vector) # how similar
      rounded_similarity = int((similarity * 10000)) / 10000.0 # rounding

      # Store in output
      named_nearest_neighbors.append({
        'filename': neighbor_file_name,
        'similarity': rounded_similarity
      })

      #print("Similarity: " + str(rounded_similarity))

      # If very close copy file to output for review
      if(rounded_similarity > top_x_limit and rounded_similarity != 1.0): 
        # Search List Data for row with matching key as filename
        #print("Searching for " + neighbor_file_name)
        for r in list_data:
          if(r[csv_columns.index('Key')] == neighbor_file_name):
            #print("[FOUND] " + neighbor_file_name + " at " + r[csv_columns.index('JPG Location')])

            # use the path to jpg 
            original = r[csv_columns.index('JPG Location')] # path to scaled jpg
            name = r[csv_columns.index('Key')] # path to scaled jpg

            # create the output/run_at folder if it does not exist
            if not os.path.exists('output/' + run_at + '/duplicates/' + file_being_checked):
              os.makedirs('output/' + run_at + '/duplicates/' + file_being_checked)

            # Use the path to original and paste a copy in output folder
            if not os.path.exists('output/' + run_at + '/duplicates/' + file_being_checked + '/' + str(rounded_similarity) + '_' + neighbor_file_name + '.jpg'):
              copyfile(original, 'output/' + run_at + '/duplicates/' + file_being_checked + '/' + str(rounded_similarity) + '_' + neighbor_file_name + '.jpg')        

    # Write output
    with open('output/' + run_at + '/nearest_neighbors/' + master_file_name + '.json', 'w') as out:
      json.dump(named_nearest_neighbors, out)
      #print(time_util.timestamp() + "[INFO] ANNOY JSON: " + master_file_name + '.json')
      row.append(json.dumps(named_nearest_neighbors))
      #print(time_util.timestamp() + "[INFO] ANNOY JSON Added to CSV")

    i = i + 1 # iterator

  return list_data

def main():
  list_data = []
  csv_columns = []
  nearest_neighboors( list_data, csv_columns )

if __name__ == '__main__':   
    main() # execute main