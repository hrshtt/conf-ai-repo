'''
    This script equilizes the histogram of each image
'''

import cv2
import numpy as np
from matplotlib import pyplot as plt
from glob import glob 
from pathlib import Path

img_list = glob('data/raw/orignal_images/*.jpg')

img_list = [Path(path) for path in img_list]

Path('data/processed/transformed_images').mkdir(exist_ok=True)

for img_path in img_list:
    img = cv2.imread(str(img_path), 0)
    hist, bins = np.histogram(img.flatten(),256,[0,256])

    cdf = hist.cumsum()

    cdf_m = np.ma.masked_equal(cdf,0)
    cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
    cdf = np.ma.filled(cdf_m,0).astype('uint8')
    img2 = cdf[img]

    cv2.imwrite(str('transformed_images' / Path(img_path.name)), img2)
