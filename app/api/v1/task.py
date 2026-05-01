import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.schema.model import TaskModel
from app.exceptions.app import AppException
from app.infra.depends.db import get_db
from app.infra.repository.cat import find_cats_by_task_id
from app.infra.repository.task import find_task_by_id

router = APIRouter()


@router.get("/status/{taskId}")
async def task_status(
    taskId: Annotated[
        uuid.UUID,
        Path(title="The ID of the item to get", description="A valid UUID v4"),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> TaskModel:
    task = find_task_by_id(db=db, taskId=taskId)
    if task is None:
        raise AppException(
            code="NOT_FOUND_TASK",
            msg=f"not found target taskId: {taskId}",
            statusCode=HTTP_400_BAD_REQUEST,
        )

    cats = find_cats_by_task_id(db=db, taskId=taskId)
    if len(cats) == 0:
        return task

    task.cats = cats
    return task
