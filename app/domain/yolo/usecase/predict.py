from typing import TYPE_CHECKING

from PIL.Image import Image

if TYPE_CHECKING:
    from ultralytics import YOLO
    from ultralytics.engine.results import Results


def predict(model: YOLO, image: Image) -> list[Results]:
    return model.predict(image)
