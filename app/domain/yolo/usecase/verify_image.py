import io

from loguru import logger
from PIL import Image
from starlette.status import HTTP_400_BAD_REQUEST

from app.constants.error_code import EMPTY_IMAGE, INVALID_IMAGE
from app.exceptions.app import AppException


def verify_image(
    imgBytes: bytes,
) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(imgBytes))
        img.verify()
        img = Image.open(io.BytesIO(imgBytes))
    except Exception as esc:
        logger.error(
            INVALID_IMAGE,
            extra={"err": esc},
        )
        raise AppException(
            code=INVALID_IMAGE,
            msg=f"invalid imageBytes: {imgBytes}",
            statusCode=HTTP_400_BAD_REQUEST,
        ) from esc

    if img is None:
        logger.error(EMPTY_IMAGE)
        raise AppException(
            code="EMPTY_IMAGE",
            msg=f"empty image from imageBytes: {imgBytes}",
            statusCode=HTTP_400_BAD_REQUEST,
        )

    return img
