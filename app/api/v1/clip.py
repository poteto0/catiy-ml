from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile
from transformers import CLIPModel, CLIPProcessor

from app.api.schema.model import ClipRequestLabels, ClipResponse
from app.domain.clip.services.classify_activity_label import classify_activity_label
from app.infra.depends.ml import get_clip, get_device

router = APIRouter()


@router.post("/classify/cat/activity")
async def classify_cat_activity(
    file: UploadFile,
    labels: Annotated[ClipRequestLabels, Form()],
    device: Annotated[str, Depends(get_device)],
    clip: Annotated[tuple[CLIPModel, CLIPProcessor], Depends(get_clip)],
) -> ClipResponse:
    imgBytes = await file.read()

    return await classify_activity_label(
        imgBytes=imgBytes,
        labels=labels,
        device=device,
        clip=clip,
    )
