'''
    This script equilizes the histogram of each image
'''
import cv2
import numpy as np
import time_util
import paths_util
from pathlib import Path

def get_preprocessed_images(images_dir, tracker = None):
    images_dir = Path(images_dir)

    output_path = Path('data/processed/transformed_images')
    output_path.mkdir(parents=True, exist_ok=True)

    if tracker is None:
        print('--------------- This is a Dry Run ---------------')
        tracker = time_util.time_tracker()

    total = len(list(images_dir.glob('*.jpg')))

    for i, img_path in enumerate(images_dir.glob('*.jpg')):

        img = cv2.imread(str(img_path), 0)
        hist, bins = np.histogram(img.flatten(),256,[0,256])

        cdf = hist.cumsum()

        cdf_m = np.ma.masked_equal(cdf,0)
        cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
        cdf = np.ma.filled(cdf_m,0).astype('uint8')
        img2 = cdf[img]

        cv2.imwrite(str('transformed_images' / Path(img_path.name)), img2)

        paths_util.printProgressBar(i+1, total)

    
    print("----"*20)
    print(f"Preprocessed {total} Images - Completed at {time_util.timestamp()}")
    print(f"--- {tracker.total_time()} seconds passed ---------")

    return str(output_path)

    