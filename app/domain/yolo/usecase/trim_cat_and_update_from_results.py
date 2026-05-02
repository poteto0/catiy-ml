import uuid

from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
from ultralytics.engine.results import Results

from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.scan import trim_all_target
from app.ents import Task
from app.ents.schema import Cat
from app.exceptions.app import AppException
from app.infra.repository.cat import create_cats, upload_cat_image
from app.infra.repository.task import TaskStatusUpdate, update_tasks_status


def trim_cat_and_update_from_results(
    results: list[Results],
    db: Session,
    r2Client: S3Client,
    task: Task,
) -> None:
    allCatImages: list[bytes] = []
    for result in results:
        cats = trim_all_target(
            result=result,
            targetLabel="cat",
        )
        if len(cats) == 0:
            continue

        allCatImages.extend(cats)

    try:
        catEnts: list[Cat] = []
        for catImage in allCatImages:
            fileName = f"{uuid.uuid4()}.jpg"
            catEnt = Cat(
                id=uuid.uuid4(),
                cat_name="",
                cat_image_url=fileName,
                task_id=task.id,
            )
            upload_cat_image(
                r2Client=r2Client,
                fileName=fileName,
                imgBytes=catImage,
            )
            catEnts.append(catEnt)

        create_cats(db, catEnts)

    except AppException:
        query = TaskStatusUpdate(
            taskId=task.id,
            status=TaskStatus.TRIM_CAT_FAILED,
            hasCat=True,
        )
        update_tasks_status(db, [query])
        return

    else:
        query = TaskStatusUpdate(
            taskId=task.id,
            status=TaskStatus.TRIM_CAT_FINISHED,
            hasCat=True,
        )
        update_tasks_status(db, [query])
        return
