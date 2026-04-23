import io

from PIL import Image
from starlette.status import HTTP_400_BAD_REQUEST

from app.exceptions.app import AppException


def verify_image(
    imgBytes: bytes,
) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(imgBytes))
        img.verify()
        img = Image.open(io.BytesIO(imgBytes))
    except Exception as esc:
        raise AppException(
            code="INVALID_IMAGE",
            msg=f"invalid imageBytes: {imgBytes}",
            statusCode=HTTP_400_BAD_REQUEST,
        ) from esc

    if img is None:
        raise AppException(
            code="EMPTY_IMAGE",
            msg=f"empty image from imageBytes: {imgBytes}",
            statusCode=HTTP_400_BAD_REQUEST,
        )

    return img
