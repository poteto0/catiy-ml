from typing import TYPE_CHECKING

from torchvision.models import EfficientNet
from transformers import CLIPModel, CLIPProcessor

if TYPE_CHECKING:
    from ultralytics import YOLO


class AppState:
    catiyYolo: YOLO
    clipModel: CLIPModel
    clipProcessor: CLIPProcessor
    effnet: EfficientNet
    device: str
