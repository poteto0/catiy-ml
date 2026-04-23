from PIL.Image import Image
from sqlalchemy.orm import Session
from ultralytics.engine.results import Results
from ultralytics.models import YOLO

from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.predict import predict
from app.domain.yolo.usecase.scan import has_target
from app.ents import Task
from app.infra.repository.task import TaskStatusUpdate, update_tasks_status


def detect_cat_and_update_from_img(
    img: Image,
    db: Session,
    model: YOLO,
    task: Task,
) -> tuple[list[Results], bool]:
    results = predict(model=model, image=img)

    for result in results:
        if has_target(result=result, targetLabel="cat"):
            query = TaskStatusUpdate(
                taskId=task.id,
                status=TaskStatus.DETECT_CAT_FINISHED,
                hasCat=True,
            )
            update_tasks_status(db, [query])
            return ([], False)

    query = TaskStatusUpdate(
        taskId=task.id,
        status=TaskStatus.DETECT_CAT_FINISHED,
        hasCat=False,
    )
    update_tasks_status(db, [query])
    return (results, True)
