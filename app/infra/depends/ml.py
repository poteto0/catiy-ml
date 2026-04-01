from typing import TYPE_CHECKING

from fastapi import Depends

from app.infra.depends.base import get_state
from app.types.state import AppState

if TYPE_CHECKING:
    from ultralytics import YOLO


def get_catiy_yolo(state: AppState = Depends(get_state)) -> YOLO:
    return state.catiyYolo
