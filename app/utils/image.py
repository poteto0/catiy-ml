import io

import cv2
from loguru import logger
from PIL import Image
from starlette.status import HTTP_400_BAD_REQUEST

from app.constants.error_code import INVALID_IMAGE
from app.exceptions.app import AppException
from app.types.image import ImageRaw


def transform_raw_image_to_rgb_bytes(
    rawImage: ImageRaw,
    encodeFormat: str = ".jpg",
) -> bytes:
    rgbImage = cv2.cvtColor(rawImage, cv2.COLOR_BGR2RGB)
    return cv2.imencode(encodeFormat, rgbImage)[1].tobytes()


def transform_pil_image_to_bytes(
    img: Image.Image,
    fmt: str = "JPEG",
) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def verify_image(
    imgBytes: bytes,
) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(imgBytes))
        img.verify()
        img = Image.open(io.BytesIO(imgBytes))
    except Exception as exc:
        logger.error(
            INVALID_IMAGE,
            extra={"err": exc},
        )
        raise AppException(
            code=INVALID_IMAGE,
            msg=f"invalid imageBytes: {imgBytes}",
            statusCode=HTTP_400_BAD_REQUEST,
        ) from exc

    return img
