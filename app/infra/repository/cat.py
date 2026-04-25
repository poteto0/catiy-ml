from pydantic.dataclasses import dataclass
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.constants.error_code import SQL_ERROR
from app.ents.schema import Cat
from app.exceptions.app import AppException


def create_cats(db: Session, cats: list[Cat]) -> None:
    try:
        db.add_all(cats)
        db.commit()
    except SQLAlchemyError as esc:
        db.rollback()
        raise AppException(
            code=SQL_ERROR,
            msg="sql error on create cats",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
        ) from esc


@dataclass
class CatUpdate:
    catName: str
    catImageUrl: str
    taskId: str
