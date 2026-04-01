from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ultralytics import YOLO


class AppState:
    catiyYolo: YOLO

