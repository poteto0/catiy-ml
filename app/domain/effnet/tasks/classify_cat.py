from mypy_boto3_s3 import S3Client
from PIL.ImageFile import ImageFile
from sqlalchemy.orm import Session
from torchvision.models import EfficientNet

import uuid

from app.constants.task_status import TaskStatus
from app.domain.effnet.usecase.classify_cat_and_update_task import classify_cat_and_update_task
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
        cat_updates = []
        for cat in cats:
            img = get_image(r2Client, cat.catImageUrl)
            cat_name = classify_cat_and_update_task(img, model)
            cat_updates.append(CatUpdate(catId=cat.id, catName=cat_name))
        
        if cat_updates:
            update_cats(db, cat_updates)
            
        update_tasks_status(db, [TaskStatusUpdate(taskId=taskId, status=TaskStatus.CLASSIFY_CAT_FINISHED, hasCat=None)])
    except Exception as e:
        update_tasks_status(db, [TaskStatusUpdate(taskId=taskId, status=TaskStatus.CLASSIFY_CAT_FAILED, hasCat=None)])
