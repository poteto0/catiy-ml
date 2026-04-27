from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from ultralytics.models import YOLO

from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.detect_cat_and_update_from_img import (
    detect_cat_and_update_from_img,
)
from app.domain.yolo.usecase.trim_cat_and_update_from_results import (
    trim_cat_and_update_from_results,
)
from app.domain.yolo.usecase.verify_image import verify_image
from app.ents import Task
from app.exceptions.app import AppException
from app.infra.repository.task import (
    TaskStatusUpdate,
    update_tasks_status,
)


def trim_cat_task(
    imgBytes: bytes,
    db: Session,
    r2Client: S3Client,
    model: YOLO,
    task: Task,
) -> None:
    try:
        img = verify_image(imgBytes)
    except AppException:
        query = TaskStatusUpdate(
            taskId=task.id,
            status=TaskStatus.READ_IMAGE_FAILED,
            hasCat=False,
        )
        update_tasks_status(db, [query])
        return

    (results, hasCat) = detect_cat_and_update_from_img(
        img=img,
        db=db,
        r2Client=r2Client,
        model=model,
        task=task,
    )
    if not hasCat:
        return

    trim_cat_and_update_from_results(
        results=results,
        db=db,
        r2Client=r2Client,
        task=task,
    )
