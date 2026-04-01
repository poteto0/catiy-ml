from PIL.Image import Image
from ultralytics import YOLO
from ultralytics.engine.results import Results


def predict(model: YOLO, image: Image) -> list[Results]:
    return model.predict(image)
