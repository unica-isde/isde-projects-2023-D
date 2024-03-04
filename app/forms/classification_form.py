from typing import List
from fastapi import Request
from app.transformations.transfomation_utils import transform_image


class ClassificationForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.errors: List = []
        self.image_id: str
        self.model_id: str
        self.color = 1.0
        self.sharpness = 1.0
        self.contrast = 1.0
        self.brightness = 1.0

    async def load_data(self):
        form = await self.request.form()
        self.image_id = form.get("image_id")
        self.model_id = form.get("model_id")
        self.color = form.get("color")
        self.sharpness = form.get("sharpness")
        self.contrast = form.get("contrast")
        self.brightness = form.get("brightness")
        # print(self.color)
        # print(self.brightness)
        # print(self.sharpness)
        # print(self.contrast)

    @property
    def is_valid(self):
        if not self.image_id or not isinstance(self.image_id, str):
            self.errors.append("A valid image id is required")
        if not self.model_id or not isinstance(self.model_id, str):
            self.errors.append("A valid model id is required")
            # Set default values for color, brightness, contrast, and sharpness
        self.color = float(self.color) if self.color and self.color.strip() else 0.1
        self.brightness = float(self.brightness) if self.brightness and self.brightness.strip() else 0.1
        self.sharpness = float(self.sharpness) if self.sharpness and self.sharpness.strip() else 0.1
        self.contrast = float(self.contrast) if self.contrast and self.contrast.strip() else 0.1

        if not self.errors:
            return True
        return False
