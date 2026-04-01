from typing import cast

from fastapi import Request
from ultralytics import YOLO

from app.types.state import AppState


def get_catiy_yolo(request: Request) -> YOLO:
    state = cast("AppState", request.app.state)
    return state.catiyYolo
