import cv2
import numpy as np
import os
from app.config import Configuration

conf = Configuration()

def get_image_path(img_id):
    '''Function that calculates the image path based on the image id'''
    return os.path.join(conf.image_folder_path, img_id)

def calculate_histogram(image_path):
    '''Function that calculates the histogram values array'''
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    histogram, _ = np.histogram(image.flatten(), bins=256, range=[0, 255])

    return histogram.tolist()