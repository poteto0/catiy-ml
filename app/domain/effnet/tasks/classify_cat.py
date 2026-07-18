from mypy_boto3_s3 import S3Client
from PIL.ImageFile import ImageFile
from sqlalchemy.orm import Session
from torchvision.models import EfficientNet

from app.ents import Task


def classify_cat_task(
    imgFile: ImageFile,
    db: Session,
    r2Client: S3Client,
    model: EfficientNet,
    task: Task,
) -> None:
    pass
