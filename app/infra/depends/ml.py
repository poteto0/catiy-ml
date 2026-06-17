from typing import cast

from fastapi import Request
from transformers import CLIPModel, CLIPProcessor
from ultralytics import YOLO

from app.types.state import AppState


def get_catiy_yolo(request: Request) -> YOLO:
    state = cast("AppState", request.app.state)
    return state.catiyYolo


def get_clip(request: Request) -> tuple[CLIPModel, CLIPProcessor]:
    state = cast("AppState", request.app.state)
    return (state.clipModel, state.clipProcessor)


def get_device(request: Request) -> str:
    state = cast("AppState", request.app.state)
    return state.device
