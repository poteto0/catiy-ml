from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from ultralytics.models import YOLO

from app.api.schema.model import TaskModel
from app.domain.yolo.tasks.detect_cat import detect_cat_task
from app.domain.yolo.tasks.trim_cat import trim_cat_task
from app.factory.task import init_task
from app.infra.depends.db import get_db
from app.infra.depends.ml import get_catiy_yolo
from app.infra.depends.r2 import get_r2
from app.infra.repository.task import create_tasks

router = APIRouter()


@router.post("/detect/cat")
async def detect_cat(
    backgroundTasks: BackgroundTasks,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    model: Annotated[YOLO, Depends(get_catiy_yolo)],
) -> TaskModel:
    imgBytes = await file.read()
    task = init_task()
    create_tasks(db=db, tasks=[task])

    backgroundTasks.add_task(
        detect_cat_task,
        imgBytes=imgBytes,
        db=db,
        model=model,
        task=task,
    )

    return TaskModel(
        id=task.id,
        status=task.status,
        hasCat=task.has_cat,
        cats=[],
    )


@router.post("/trim/cat")
async def trim_cat(
    backgroundTasks: BackgroundTasks,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    r2Client: Annotated[S3Client, Depends(get_r2)],
    model: Annotated[YOLO, Depends(get_catiy_yolo)],
) -> TaskModel:
    imgBytes = await file.read()
    task = init_task()
    create_tasks(db=db, tasks=[task])

    backgroundTasks.add_task(
        trim_cat_task,
        imgBytes=imgBytes,
        db=db,
        r2Client=r2Client,
        model=model,
        task=task,
    )

    return TaskModel(
        id=task.id,
        status=task.status,
        hasCat=task.has_cat,
        cats=[],
    )
