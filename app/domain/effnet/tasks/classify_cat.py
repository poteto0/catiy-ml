from concurrent.futures import ThreadPoolExecutor
from mypy_boto3_s3 import S3Client
from PIL.ImageFile import ImageFile
from sqlalchemy.orm import Session
from torchvision.models import EfficientNet

import uuid

from app.constants.task_status import TaskStatus
from app.domain.effnet.usecase.classify_cat import classify_cats
from app.infra.repository.cat import find_cats_by_task_id, get_image, CatUpdate, update_cats
from app.infra.repository.task import TaskStatusUpdate, update_tasks_status

def classify_cat_task(
    db: Session,
    r2Client: S3Client,
    model: EfficientNet,
    taskId: uuid.UUID,
) -> None:
    try:
        cats = find_cats_by_task_id(db, taskId)
        if not cats:
            update_tasks_status(db, [TaskStatusUpdate(taskId=taskId, status=TaskStatus.CLASSIFY_CAT_FINISHED, hasCat=None)])
            return

        with ThreadPoolExecutor() as executor:
            images = list(executor.map(lambda cat: get_image(r2Client, cat.catImageUrl), cats))

        cat_names = classify_cats(images, model)
        
        cat_updates = [
            CatUpdate(catId=cat.id, catName=cat_name)
            for cat, cat_name in zip(cats, cat_names, strict=True)
        ]
        
        if cat_updates:
            update_cats(db, cat_updates)
            
        update_tasks_status(db, [TaskStatusUpdate(taskId=taskId, status=TaskStatus.CLASSIFY_CAT_FINISHED, hasCat=None)])
    except Exception as e:
        update_tasks_status(db, [TaskStatusUpdate(taskId=taskId, status=TaskStatus.CLASSIFY_CAT_FAILED, hasCat=None)])

