from loguru import logger
from mypy_boto3_s3 import S3Client
from PIL.Image import Image
from sqlalchemy.orm import Session
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from torchvision.models import EfficientNet

from app.domain.effnet.data.labels import nyansLabel
from app.domain.effnet.usecase.predict import predict
from app.ents import Task
from app.exceptions.app import AppException


def classify_cat_and_update_task(
    image: Image,
    db: Session,
    r2Client: S3Client,
    model: EfficientNet,
    task: Task,
) -> None:
    logger.info("classify_cat_and_update_task:start")

    logger.info("classify_cat_and_update_task > predict: start")
    result = predict(model, image, nyansLabel)
    mostLikely = result.mostLikely

    if mostLikely.label is None or (mostLikely.label not in nyansLabel):
        raise AppException(
            code="NOT_FOUND_LABEL",
            msg=f"unexpected not found label: {mostLikely.label}",
            statusCode=HTTP_500_INTERNAL_SERVER_ERROR,
        )
