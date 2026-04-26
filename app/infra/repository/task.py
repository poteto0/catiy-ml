import uuid

from loguru import logger
from pydantic.dataclasses import dataclass
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.constants.error_code import SQL_ERROR
from app.ents import Task
from app.exceptions.app import AppException


def create_tasks(db: Session, tasks: list[Task]) -> None:
    try:
        db.add_all(tasks)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise AppException(
            code=SQL_ERROR,
            msg="sql error on create tasks",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
        ) from exc


def find_task_by_id(db: Session, taskId: uuid.UUID) -> Task | None:
    try:
        return db.query(Task).filter(Task.id == taskId).first()
    except SQLAlchemyError as exc:
        raise AppException(
            code=SQL_ERROR,
            msg="sql error on find tasks",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
        ) from exc


@dataclass
class TaskStatusUpdate:
    taskId: uuid.UUID
    status: str
    hasCat: bool | None


def update_tasks_status(db: Session, updateQueries: list[TaskStatusUpdate]) -> None:
    try:
        tasks = []
        for update in updateQueries:
            task = find_task_by_id(db, update.taskId)
            if task is None:
                continue
            task.status = update.status
            if update.hasCat is not None:
                task.has_cat = update.hasCat
            tasks.append(task)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            SQL_ERROR,
            extra={"err": exc},
        )
        raise AppException(
            code=SQL_ERROR,
            msg="sql error on update task",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
        ) from exc
