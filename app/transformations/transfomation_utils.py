from app.ml.classification_utils import fetch_image
from PIL import ImageEnhance, Image
from PIL.ImageEnhance import Color, Brightness, Sharpness, Contrast
from io import BytesIO
import base64


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


def convert_image(img):
    """
    Converts an Image to a Byte array to pass it to the frontend
    without saving it.
    """
    img_byte_array = BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    image_64 = base64.b64encode(img_byte_array.getvalue()).decode("utf-8")
    image_url = f"data:image/png;base64,{image_64}"

    return image_url

