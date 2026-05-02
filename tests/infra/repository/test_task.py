import uuid
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ents import Base, Task
from app.exceptions.app import AppException
from app.infra.db.engine import engine
from app.infra.depends.db import get_db
from app.infra.repository.task import (
    TaskStatusUpdate,
    create_tasks,
    find_task_by_id,
    update_tasks_status,
)


@pytest.fixture
def setup_db() -> Generator[Session]:
    Base.metadata.create_all(bind=engine)

    db = next(get_db())

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


taskId = uuid.uuid4()


@pytest.fixture
def task_sample() -> list[Task]:
    return [
        Task(id=taskId, status="pending", has_cat=False),
        Task(id=uuid.uuid4(), status="completed", has_cat=True),
    ]


def test_can_create_provided_tasks(setup_db: Session) -> None:
    """taskレコードを作成できる"""
    # Arrange
    db = setup_db
    tasks = [Task(id=taskId, status="pending", has_cat=False)]

    # Act
    create_tasks(db, tasks)

    # Assert
    assert db.query(Task).count() == 1


def test_create_tasks_rollback_on_commit_failed(task_sample: list[Task]) -> None:
    """エラー発生時に、ロールバックする"""
    # Arrange
    db = MagicMock(spec=Session)
    db.commit.side_effect = SQLAlchemyError

    # Act & Assert
    with pytest.raises(AppException):
        create_tasks(db, task_sample)

    assert db.rollback.called


def test_can_find_task_by_id(setup_db: Session, task_sample: list[Task]) -> None:
    """idでtaskを見つけることが可能"""
    # Arrange
    db = setup_db
    db.add_all(task_sample)
    db.commit()

    # Act
    found_task = find_task_by_id(db, taskId)

    # Assert
    assert found_task is not None
    assert found_task.id == taskId


def test_can_update_task_status(setup_db: Session, task_sample: list[Task]) -> None:
    """taskのステータスを更新できる"""
    # Arrange
    db = setup_db
    db.add_all(task_sample)
    db.commit()
    update = TaskStatusUpdate(taskId=taskId, status="completed", hasCat=True)

    # Act
    update_tasks_status(db, [update])

    # Assert
    task = db.query(Task).filter(Task.id == taskId).first()
    assert task is not None
    assert task.status == "completed"
    assert task.has_cat is True


def test_update_tasks_status_rollback_on_commit_failed() -> None:
    """更新エラー発生時に、ロールバックする"""
    # Arrange
    db = MagicMock(spec=Session)
    # Return a real task object for the query mock
    task = Task(id=taskId, status="pending", has_cat=False)
    db.query.return_value.filter.return_value.first.return_value = task
    db.commit.side_effect = SQLAlchemyError
    update = TaskStatusUpdate(taskId=taskId, status="failed", hasCat=False)

    # Act & Assert
    with pytest.raises(AppException):
        update_tasks_status(db, [update])

    assert db.rollback.called
