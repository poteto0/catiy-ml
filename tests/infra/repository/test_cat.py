import uuid
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ents import Base
from app.ents.schema import Cat
from app.exceptions.app import AppException
from app.infra.db.engine import engine
from app.infra.depends.db import get_db
from app.infra.repository.cat import create_cats, find_cats_by_task_id


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
def cat_sample() -> list[Cat]:
    return [
        Cat(
            id=uuid.uuid4(),
            cat_name="sample",
            cat_image_url="sample",
            task_id=taskId,
        ),
        Cat(
            id=uuid.uuid4(),
            cat_name="sample",
            cat_image_url="sample",
            task_id=taskId,
        ),
        Cat(
            id=uuid.uuid4(),
            cat_name="sample",
            cat_image_url="sample",
            task_id=uuid.uuid4(),
        ),
    ]


def test_can_create_provided_cats(setup_db: Session, cat_sample: list[Cat]) -> None:
    """catレコードを作成できる"""
    # Arrange
    db = setup_db

    # Act
    create_cats(db, cat_sample)

    # Assert
    cats = db.query(Cat).all()
    assert len(cats) == 3


def test_rollback_on_commit_failed(cat_sample: list[Cat]) -> None:
    """エラー発生時に、ロールバックする"""
    # Arrange
    db = MagicMock()

    def mock_add_all(_: list[Cat]) -> None:
        return

    db.add_all = mock_add_all
    db.commit.side_effect = SQLAlchemyError

    # Act & Assert
    with pytest.raises(AppException):
        create_cats(db, cat_sample)

    assert db.rollback.called


def test_can_find_cats_by_task_id(setup_db: Session, cat_sample: list[Cat]) -> None:
    """taskで発見したcatを見つけることが可能"""
    # Arrange
    db = setup_db
    db.add_all(cat_sample)
    db.commit()

    # Act & Assert
    assert len(find_cats_by_task_id(db, taskId)) == 2


def test_app_exception_raise_on_find_cat_failed() -> None:
    """エラー発生時に、ラップする"""
    # Arrange
    db = MagicMock()
    # Mocking db.query(Cat).filter(...).all()
    db.query.side_effect = SQLAlchemyError

    # Act & Assert
    with pytest.raises(AppException):
        find_cats_by_task_id(db, taskId)
