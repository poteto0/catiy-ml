from typing import Any

import numpy as np
from sqlalchemy.orm import Session
from ultralytics.models import YOLO

from app.constants.task_status import TaskStatus
from app.domain.yolo.usecase.detect_cat_and_update_from_img import (
    detect_cat_and_update_from_img,
)
from app.domain.yolo.usecase.scan import trim_all_target
from app.domain.yolo.usecase.verify_image import verify_image
from app.ents import Task
from app.exceptions.app import AppException
from app.infra.repository.task import (
    TaskStatusUpdate,
    update_tasks_status,
)


def trim_cat_task(imgBytes: bytes, db: Session, model: YOLO, task: Task) -> None:
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

    allCats: list[np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]]] = []
    for result in results:
        cats = trim_all_target(result=result, targetLabel="cat")
        if cats is None:
            continue

        allCats.extend(cats)
