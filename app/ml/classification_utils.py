"""
This is a simple classification service. It accepts an url of an
image and returns the top-5 classification labels and scores.
"""

import importlib
import json
import logging
import os
import torch
from io import BytesIO
from PIL import Image
import base64
import imghdr
from torchvision import transforms

from app.config import Configuration


conf = Configuration()


def fetch_image(image_id):
    """Gets the image from the specified ID. It returns only images
    downloaded in the folder specified in the configuration object."""
    image_path = os.path.join(conf.image_folder_path, image_id)
    img = Image.open(image_path)
    return img


# comment
def get_labels():
    """Returns the labels of Imagenet dataset as a list, where
    the index of the list corresponds to the output class."""
    labels_path = os.path.join(conf.image_folder_path, "imagenet_labels.json")
    with open(labels_path) as f:
        labels = json.load(f)
    return labels


def get_model(model_id):
    """Imports a pretrained model from the ones that are specified in
    the configuration file. This is needed as we want to pre-download the
    specified model in order to avoid unnecessary waits for the user."""
    if model_id in conf.models:
        try:
            module = importlib.import_module("torchvision.models")
            return module.__getattribute__(model_id)(weights="DEFAULT")
        except ImportError:
            logging.error("Model {} not found".format(model_id))
    else:
        raise ImportError


def classify_image(model_id, img_id):
    """Returns the top-5 classification score output from the
    model specified in model_id when it is fed with the
    image corresponding to img_id."""

    # if the user uploads an image or if it is an Enhanced image, the fetch_image is not necessary
    if isinstance(img_id, str):
        img = fetch_image(img_id)
    else:
        img = img_id

    model = get_model(model_id)
    model.eval()
    transform = transforms.Compose(
        (
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        )
    )

    # apply transform from torchvision
    img = img.convert("RGB")
    preprocessed = transform(img).unsqueeze(0)

    # gets the output from the model
    out = model(preprocessed)
    _, indices = torch.sort(out, descending=True)

    # transforms scores as percentages
    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100

    # gets the labels
    labels = get_labels()

    # takes the top-5 classification output and returns it
    # as a list of tuples (label_name, score)
    output = [[labels[idx], percentage[idx].item()] for idx in indices[0][:5]]

    img.close()
    return output


def check_errors(image_id):
    """
    Raises an exception if the parameter is not an Image
    """
    try:
        image_type = imghdr.what(None, h=image_id.file.read(2048))
        image_id.file.seek(0)  # Reset file pointer

        if not image_type:
            raise ValueError("Invalid image format. Please upload a valid image file.")
    except Exception as e:
        raise ValueError(f"Upload Error: {e}")


def convert_UploadFile(content):
    """
    Converts UploadFile.read() to a PIL Image and then to a Byte array to pass it to the frontend
    without saving it.
    """
    image_bytes = BytesIO(content)
    img = Image.open(image_bytes)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    img_url = f"data:image/png;base64,{image_64}"

    return (img, img_url)
