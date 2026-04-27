from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from ultralytics.models import YOLO

from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.detect_cat_and_update_from_img import (
    detect_cat_and_update_from_img,
)
from app.domain.yolo.usecase.verify_image import verify_image
from app.ents import Task
from app.exceptions.app import AppException
from app.infra.repository.task import (
    TaskStatusUpdate,
    update_tasks_status,
)


def detect_cat_task(
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

    detect_cat_and_update_from_img(img, db, r2Client, model, task)
    return
