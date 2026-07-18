from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import EfficientNet
from transformers import CLIPModel, CLIPProcessor
from ultralytics import YOLO

from app.types.app import TypedFastAPI


def load_yolo(pt: str) -> YOLO:
    filePath = Path(__file__).resolve().parents[2]
    modelPath = filePath / "config" / "ml" / "weights" / pt
    return YOLO(str(modelPath))


def load_clip() -> tuple[CLIPModel, CLIPProcessor]:
    clipModel = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clipProcessor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return (clipModel, clipProcessor)


def load_effnet(pth: str) -> EfficientNet:
    model = models.efficientnet_v2_s(
        weights=None,
    )
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, 3)
    filePath = Path(__file__).resolve().parents[2]
    modelPath = filePath / "config" / "ml" / "weights" / pth
    checkpoint = torch.load(modelPath, map_location=load_device())
    model.load_state_dict(checkpoint)
    model.eval()  # 検証モード
    return model


def load_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


@asynccontextmanager
async def set_ml_model(app: TypedFastAPI) -> AsyncGenerator[None]:
    app.state.catiyYolo = load_yolo("catiy_yolo.pt")

    (app.state.clipModel, app.state.clipProcessor) = load_clip()

    app.state.effnet = load_effnet("catiy_effnet.pth")

    app.state.device = load_device()

    yield

    # cleanup
    del app.state.catiyYolo
    del app.state.clipModel
    del app.state.clipProcessor
    del app.state.effnet
    del app.state.device
