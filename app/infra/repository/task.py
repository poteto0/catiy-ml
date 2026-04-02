import uuid

from pydantic.dataclasses import dataclass
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ents import Task


def create_tasks(db: Session, tasks: list[Task]) -> None:
    try:
        db.add_all(tasks)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def find_task_by_id(db: Session, taskId: uuid.UUID) -> Task | None:
    try:
        return db.query(Task).filter(Task.id == taskId).first()
    except SQLAlchemyError:
        raise


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
    except SQLAlchemyError:
        db.rollback()
        raise
