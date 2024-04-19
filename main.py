from io import BytesIO
import json
import os
from PIL import Image
from typing import Dict, List
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
from rq import Connection, Queue
from rq.job import Job
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.forms.transformation_form import TransformationForm
from app.ml.classification_utils import classify_image, check_errors, convert_UploadFile
from app.forms.histogram_form import HistogramForm
from app.histogram.histogram import calculate_histogram, get_image_path
from app.utils import list_images
from app.transformations.transfomation_utils import transform_image, convert_image
import matplotlib.pyplot as plt

app = FastAPI()
config = Configuration()

IMAGEDIR = "images/"

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/info")
def info() -> Dict[str, List[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images}
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

    classification_scores = classify_image(
        model_id=model_id,
        img_id=image_id,
    )

    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "classification_scores": json.dumps(classification_scores)
        },
    )


@app.get("/classify_transform")
def create_transform(request: Request):
    return templates.TemplateResponse(
        "transformation_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classify_transform")
async def request_transform(request: Request):
    folder_path = "app/static/output/json/"
    # Check if the folder exists
    if not os.path.exists(folder_path):
        # If it doesn't exist, create it
        os.makedirs(folder_path)

    form = TransformationForm(request)
    await form.load_data()

    image_id = form.image_id
    model_id = form.model_id
    color = form.color
    brightness = form.brightness
    contrast = form.contrast
    sharpness = form.sharpness

    try:
        enhanced_image = transform_image(
            image_id, color, brightness, sharpness, contrast
        )

        # Transforming the Image into a byte array to pass it to the frontend without saving it
        image_url = convert_image(img=enhanced_image)
    except Exception as exception:
        # If something goes wrong during image transformation
        error = f"Error: {str(exception)}"
        print(error)
        raise HTTPException(status_code=500, detail=error)

    # Classification on the transformed image
    classification_scores = classify_image(model_id=model_id, img_id=enhanced_image)


    return templates.TemplateResponse(
        "transformation_output.html",
        {
            "request": request,
            "image_id": image_id,
            "img_url": image_url,
            "classification_scores": json.dumps(classification_scores),
        },
    )


# Download JSON file containing prediction output
@app.get("/outputJSON")
def output_json(classification_scores):
    return JSONResponse(content=json.loads(classification_scores), media_type="application/json", headers={"Content-Disposition": "attachment; filename=output.json"})



# Download Image file containing plot
@app.get("/outputPNG", response_class=StreamingResponse)
async def output_png(classification_scores: str):
    print("hello")
    data = json.loads(classification_scores)
    x = [item[0] for item in data]
    y = [item[1] for item in data]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(x, y)
        # setting label of y-axis
    ax.set_xlabel("Y")
        # setting label of x-axis
    ax.set_title("Prediction")
    
    # Save the plot in a buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig)

    # Take the plot from the buffer
    img = Image.open(img_buffer)
    img_byte = BytesIO()
    img.save(img_byte, format='PNG')
    img.close()
    img_byte.seek(0)

    return StreamingResponse(
        content=img_byte,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=plot.png"}
    )

@app.get("/uploadImage")
async def upload_classify(request: Request):
    return templates.TemplateResponse(
        "upload_select.html",
        {"request": request, "models": Configuration.models},
    )


@app.post("/classifyUpload")
async def handle_form(
    request: Request, model_id: str = Form(...), image_id: UploadFile = File(...)
):

    try:
        check_errors(image_id)

        image_id.file.seek(0)
        content = await image_id.read()

        img, img_url = convert_UploadFile(content=content)

        classification_scores = classify_image(model_id=model_id, img_id=img)

        return templates.TemplateResponse(
            "upload_output.html",
            {
                "request": request,
                "image_HTML": img_url,
                "classification_scores": json.dumps(classification_scores),
            },
        )
    except ValueError as e:
        # Handle invalid image format error
        error_message = str(e)
        return templates.TemplateResponse(
            "upload_select.html",
            {
                "request": request,
                "models": Configuration.models,
                "error_message": error_message,
            },
        )


@app.get("/histograms")
def create_histogram(request: Request):
    return templates.TemplateResponse(
        "histogram_select.html",
        {"request": request, "images": list_images()},
    )


@app.post("/histograms")
async def request_histogram(request: Request):
    form = HistogramForm(request)
    await form.load_data()
    image_id = form.image_id
    histogram_data = calculate_histogram(get_image_path(image_id))
    return templates.TemplateResponse(
        "histogram_output.html",
        {"request": request, "image_id": image_id, "histogram_data": histogram_data},
    )
