from loguru import logger
from PIL.Image import Image
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from torchvision.models import EfficientNet

from app.domain.effnet.data.labels import nyansLabel
from app.domain.effnet.usecase.predict import predict_batch
from app.exceptions.app import AppException


def classify_cats(
    images: list[Image],
    model: EfficientNet,
) -> list[str]:
    if not images:
        return []
        
    logger.info("classify_cats:start")

    logger.info("classify_cats > predict: start")
    results = predict_batch(model, images, nyansLabel)
    
    labels = []
    for result in results:
        mostLikely = result.mostLikely
        if mostLikely.label is None or (mostLikely.label not in nyansLabel):
            raise AppException(
                code="NOT_FOUND_LABEL",
                msg=f"unexpected not found label: {mostLikely.label}",
                statusCode=HTTP_500_INTERNAL_SERVER_ERROR,
            )
        labels.append(mostLikely.label)

    return labels
