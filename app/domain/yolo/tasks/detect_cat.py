import io

from PIL import Image
from sqlalchemy.orm import Session
from ultralytics.models import YOLO

from app.domain.yolo.usecase.predict import predict
from app.domain.yolo.usecase.scan import has_target
from app.ents import Task
from app.infra.repository.task import (
    TaskStatusUpdate,
    update_tasks_status,
)


def detect_cat_task(imgBytes: bytes, db: Session, model: YOLO, task: Task) -> None:
    img: Image.Image | None = None

    try:
        img = Image.open(io.BytesIO(imgBytes))
        img.verify()
        img = Image.open(io.BytesIO(imgBytes))
    except Exception:
        query = TaskStatusUpdate(
            taskId=task.id,
            status="detect_cat:failed",
            hasCat=False,
        )
        update_tasks_status(db, [query])
        return

    if img is None:
        return

    results = predict(model=model, image=img)

    for result in results:
        if has_target(result=result, targetLabel="cat"):
            query = TaskStatusUpdate(
                taskId=task.id,
                status="detect_cat:finished",
                hasCat=True,
            )
            update_tasks_status(db, [query])
            return

    query = TaskStatusUpdate(
        taskId=task.id,
        status="detect_cat:finished",
        hasCat=False,
    )
    update_tasks_status(db, [query])
    return
