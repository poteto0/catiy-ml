from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from ultralytics import YOLO

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from app.types.app import TypedFastAPI


def load_yolo(pt: str) -> YOLO:
    filePath = Path(__file__).resolve().parents[2]
    modelPath = filePath / "config" / "ml" / "weights" / pt
    return YOLO(str(modelPath))


@asynccontextmanager
async def set_ml_model(app: TypedFastAPI) -> AsyncGenerator[None]:
    catiyYolo = load_yolo("catiy_yolo.pt")
    app.state.catiyYolo = catiyYolo

    yield

    # cleanup
    del app.state.catiyYolo
