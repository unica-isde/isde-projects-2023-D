import json
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
from rq import Connection, Queue
from rq.job import Job
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.ml.classification_utils import classify_image
from app.utils import list_images
from app.transformations.transfomation_utils import transform_image, save_transformed

app = FastAPI()
config = Configuration()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/info")
def info() -> Dict[str, List[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images, }
    return data


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The home page of the service."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/classifications")
def create_classify(request: Request):
    return templates.TemplateResponse(
        "classification_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classifications")
async def request_classification(request: Request):
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    model_id = form.model_id

    color = form.color
    brightness = form.brightness
    contrast = form.contrast
    sharpness = form.sharpness

    classification_scores = classify_image(model_id=model_id, img_id=image_id, )
    enhanced_image = transform_image(image_id, color, brightness, sharpness, contrast)
    save_transformed(enhanced_image)
    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "filename": "enhanced_image.jpg",
            "classification_scores": json.dumps(classification_scores),
        },
    )
