from typing import TYPE_CHECKING

from transformers import CLIPModel, CLIPProcessor

if TYPE_CHECKING:
    from ultralytics import YOLO


class AppState:
    catiyYolo: YOLO
    clipModel: CLIPModel
    clipProcessor: CLIPProcessor
    device: str
