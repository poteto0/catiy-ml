from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import torch
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


@asynccontextmanager
async def set_ml_model(app: TypedFastAPI) -> AsyncGenerator[None]:
    app.state.catiyYolo = load_yolo("catiy_yolo.pt")

    (app.state.clipModel, app.state.clipProcessor) = load_clip()

    app.state.device = "cuda" if torch.cuda.is_available() else "cpu"

    yield

    # cleanup
    del app.state.catiyYolo
