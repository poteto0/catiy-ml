import io
import uuid

from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from ultralytics.models import YOLO

from app.constants.external import CATIY_BUCKET
from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.detect_cat_and_update_from_img import (
    detect_cat_and_update_from_img,
)
from app.domain.yolo.usecase.scan import trim_all_target
from app.domain.yolo.usecase.verify_image import verify_image
from app.ents import Task
from app.ents.schema import Cat
from app.exceptions.app import AppException
from app.infra.repository.cat import create_cats
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

    try:
        (results, hasCat) = detect_cat_and_update_from_img(
            img,
            db,
            model,
            task,
        )
        if not hasCat:
            return

    except AppException:
        query = TaskStatusUpdate(
            taskId=task.id,
            status=TaskStatus.DETECT_CAT_FAILED,
            hasCat=False,
        )
        update_tasks_status(db, [query])
        return

    allCatImages: list[bytes] = []
    for result in results:
        cats = trim_all_target(result=result, targetLabel="cat")
        if cats is None:
            continue

        allCatImages.extend(cats)

    catEnts: list[Cat] = []
    for catImage in allCatImages:
        fileName = f"{uuid.uuid4()}.jpg"
        catEnt = Cat(
            id=uuid.uuid4(),
            cat_name="",
            cat_image_url=fileName,
            task_id=task.id,
        )
        r2Client.upload_fileobj(
            io.BytesIO(catImage),
            CATIY_BUCKET,
            fileName,
        )
        catEnts.append(catEnt)

    create_cats(db, catEnts)
