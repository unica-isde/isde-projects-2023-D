from app.ml.classification_utils import fetch_image
from PIL import ImageEnhance, Image
from PIL.ImageEnhance import Color, Brightness, Sharpness, Contrast
import os
import shutil


def transform_image(image_id, color, brightness, sharpness, contrast):
    enhanced_image: Image = fetch_image(image_id)

    if not color:
        color = 1.0
    color_enhancer = ImageEnhance.Color(enhanced_image)
    enhanced_image = color_enhancer.enhance(float(color))

    if not brightness:
        brightness = 1.0
    brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
    enhanced_image = brightness_enhancer.enhance(float(brightness))

    if not sharpness:
        sharpness = 1.0
    sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
    enhanced_image = sharpness_enhancer.enhance(float(sharpness))

    if not contrast:
        contrast = 1.0
    contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
    enhanced_image = contrast_enhancer.enhance(float(contrast))

    return enhanced_image


def save_transformed(enhanced_image: Image):
    try:
        folder_path = "app/static/transformed_image/"
        # Check if the folder exists
        if not os.path.exists(folder_path):
            # If it doesn't exist, create it
            os.makedirs(folder_path)
        destination_path = os.path.join(folder_path, "enhanced_image.jpg")
        enhanced_image.save(destination_path)

    except:
        print('saving error')

