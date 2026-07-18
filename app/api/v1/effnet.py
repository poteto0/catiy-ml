from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from torchvision.models import EfficientNet

from app.api.schema.model import CatClassifyRequest, TaskModel
from app.domain.effnet.tasks.classify_cat import classify_cat_task
from app.ents.schema import Task
from app.infra.depends.db import get_db
from app.infra.depends.ml import get_effnet
from app.infra.depends.r2 import get_r2
from app.infra.repository.task import find_task_by_id
from app.exceptions.app import AppException
from starlette.status import HTTP_404_NOT_FOUND

router = APIRouter()


@router.post("/classify/cat")
async def classify_cat(
    backgroundTasks: BackgroundTasks,
    body: CatClassifyRequest,
    db: Annotated[Session, Depends(get_db)],
    r2Client: Annotated[S3Client, Depends(get_r2)],
    model: Annotated[EfficientNet, Depends(get_effnet)],
) -> TaskModel:
    task = find_task_by_id(db, body.taskId)
    if task is None:
        raise AppException(
            code="TASK_NOT_FOUND",
            msg="Task not found",
            statusCode=HTTP_404_NOT_FOUND,
        )

    backgroundTasks.add_task(
        classify_cat_task,
        db=db,
        r2Client=r2Client,
        model=model,
        taskId=body.taskId,
    )

    return task
