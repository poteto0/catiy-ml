import uuid

from loguru import logger
from mypy_boto3_s3 import S3Client
from PIL.Image import Image
from sqlalchemy.orm import Session
from ultralytics.engine.results import Results
from ultralytics.models import YOLO

from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.predict import predict
from app.domain.yolo.usecase.scan import has_target
from app.ents import Task
from app.ents.schema import Cat
from app.infra.repository.cat import create_cats, upload_cat_image
from app.infra.repository.task import TaskStatusUpdate, update_tasks_status
from app.utils.image import transform_pil_image_to_bytes


def detect_cat_and_update_from_img(
    img: Image,
    db: Session,
    r2Client: S3Client,
    model: YOLO,
    task: Task,
) -> tuple[list[Results], bool]:
    logger.info("detect_cat_and_update_from_img:start")

    try:
        results = predict(model=model, image=img)

        for result in results:
            if has_target(result=result, targetLabel="cat"):
                fileName = f"{uuid.uuid4()}.jpg"
                upload_cat_image(
                    r2Client=r2Client,
                    imgBytes=transform_pil_image_to_bytes(img),
                    fileName=fileName,
                )
                catEnt = Cat(
                    id=uuid.uuid4(),
                    cat_name="",
                    cat_image_url=fileName,
                    task_id=task.id,
                )
                create_cats(db, [catEnt])
                query = TaskStatusUpdate(
                    taskId=task.id,
                    status=TaskStatus.DETECT_CAT_FINISHED,
                    hasCat=True,
                )
                update_tasks_status(db, [query])
                logger.info(
                    "detect_cat_and_update_from_img:finish",
                    extra={
                        "result": "found cat",
                    },
                )
                return (results, True)

        query = TaskStatusUpdate(
            taskId=task.id,
            status=TaskStatus.DETECT_CAT_FINISHED,
            hasCat=False,
        )
        update_tasks_status(db, [query])
    except Exception:
        query = TaskStatusUpdate(
            taskId=task.id,
            status=TaskStatus.DETECT_CAT_FAILED,
            hasCat=False,
        )
        update_tasks_status(db, [query])
        return ([], False)
    else:
        logger.info(
            "detect_cat_and_update_from_img:finish",
            extra={
                "result": "not found cat",
            },
        )
        return ([], False)
