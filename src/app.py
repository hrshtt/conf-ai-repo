import pandas as pd



def run():
    # Constants for CSV header lookup so we don't have to use indexes, sort in order of csv row
    CONST_COLUMNS = []
    CONST_KEY = 'Key' # 0 
    CONST_FILE = 'File' # 1
    CONST_LOCATION = 'Location' # 2
    CONST_JPG = 'JPG' # 3
    CONST_JPG_LOCATION = 'JPG Location' # 4
    CONST_SCALED_JPG = 'Scaled JPG' # 5
    CONST_FEATURES = 'Features' # 6
    CONST_VECTOR = 'Vector' # 7
    CONST_NEIGHBORS = 'Neighbors' # 8
    CONST_FACES = 'Faces' # 9
    CONST_FOCUS = 'Focus' # 10
    CONST_BLURRY = 'Blurry' # 11
    CONST_BLINKS = 'Blinks' # 12

if __name__ == "__main__":
    run()