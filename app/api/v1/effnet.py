from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from torchvision.models import EfficientNet

from app.api.schema.model import CatClassifyRequest
from app.domain.effnet.usecase.classify_cat_and_update_task import (
    classify_cat_and_update_task,
)
from app.ents.schema import Task
from app.infra.depends.db import get_db
from app.infra.depends.ml import get_effnet
from app.infra.depends.r2 import get_r2
from app.infra.repository.cat import get_image

router = APIRouter()


@router.post("/classify/cat")
async def classify_cat(
    backgroundTasks: BackgroundTasks,
    body: CatClassifyRequest,
    db: Annotated[Session, Depends(get_db)],
    r2Client: Annotated[S3Client, Depends(get_r2)],
    model: Annotated[EfficientNet, Depends(get_effnet)],
):
    img = get_image(
        r2Client=r2Client,
        fileName=body.catImageUrl,
    )

    backgroundTasks.add_task(
        classify_cat_and_update_task,
        image=img,
        db=db,
        r2Client=r2Client,
        model=model,
        task=Task(),
    )
