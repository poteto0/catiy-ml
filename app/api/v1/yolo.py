import io
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from mpmath import e
from PIL import Image

from app.domain.yolo.usecase.predict import predict
from app.domain.yolo.usecase.scan import has_target
from app.infra.depends.ml import get_catiy_yolo

if TYPE_CHECKING:
    from ultralytics import YOLO

router = APIRouter()


@router.post("/detect/cat")
async def detect_cat(
    file: UploadFile,
    model: Annotated[YOLO, Depends(get_catiy_yolo)],
) -> JSONResponse:
    imgBytes = await file.read()
    img: Image.Image | None = None
    try:
        img = Image.open(io.BytesIO(imgBytes))
        img.verify()
        img = Image.open(io.BytesIO(imgBytes))
    except e:
        raise

    if img is None:
        return None

    results = predict(model=model, image=img)
    for result in results:
        if has_target(result=result, targetLabel="cat"):
            return JSONResponse(
                content={
                    "result": True,
                },
                status_code=200,
            )

    return JSONResponse(
        content={
            "result": False,
        },
        status_code=200,
    )
