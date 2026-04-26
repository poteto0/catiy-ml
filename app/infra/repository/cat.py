import io

from botocore import exceptions as botexc
from loguru import logger
from mypy_boto3_s3 import S3Client
from pydantic.dataclasses import dataclass
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from app.constants.error_code import (
    R2_CLIENT_ERROR,
    R2_CONNECTION_ERROR,
    R2_RATE_LIMIT,
    R2_VALIDATION_ERROR,
    SQL_ERROR,
)
from app.constants.external import CATIY_BUCKET
from app.ents.schema import Cat
from app.exceptions.app import AppException


def create_cats(db: Session, cats: list[Cat]) -> None:
    try:
        db.add_all(cats)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise AppException(
            code=SQL_ERROR,
            msg="sql error on create cats",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
        ) from exc


@dataclass
class CatUpdate:
    catName: str
    catImageUrl: str
    taskId: str


def upload_cat_image(
    r2Client: S3Client,
    fileName: str,
    imgBytes: bytes,
) -> None:
    try:
        r2Client.upload_fileobj(
            io.BytesIO(imgBytes),
            CATIY_BUCKET,
            fileName,
        )
    except botexc.ClientError as exc:
        if exc.response["Error"]["Code"] == "LimitExceededException":
            logger.error(
                R2_RATE_LIMIT,
                extra={
                    "err": exc,
                },
            )
            raise AppException(
                code=R2_RATE_LIMIT,
                msg="r2 client error",
                statusCode=HTTP_429_TOO_MANY_REQUESTS,
                cause=exc,
            ) from exc

        logger.error(
            R2_CLIENT_ERROR,
            extra={
                "err": exc,
            },
        )
        raise AppException(
            code=R2_CLIENT_ERROR,
            msg="r2 client error",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
            cause=exc,
        ) from exc

    except botexc.ParamValidationError as exc:
        logger.error(
            R2_VALIDATION_ERROR,
            extra={
                "fileName": fileName,
                "imgByteLength": len(imgBytes),
                "err": exc,
            },
        )
        raise AppException(
            code=R2_VALIDATION_ERROR,
            msg="r2 param error",
            statusCode=HTTP_400_BAD_REQUEST,
            cause=exc,
        ) from exc

    except Exception as exc:
        logger.error(
            R2_CONNECTION_ERROR,
            extra={
                "err": exc,
            },
        )
        raise AppException(
            code=R2_CONNECTION_ERROR,
            msg="r2 unknown error",
            statusCode=HTTP_503_SERVICE_UNAVAILABLE,
            cause=exc,
        ) from exc
