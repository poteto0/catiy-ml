import io

import cv2
from PIL.Image import Image

from app.types.image import ImageRaw


def transform_raw_image_to_rgb_bytes(
    rawImage: ImageRaw,
    encodeFormat: str = ".jpg",
) -> bytes:
    rgbImage = cv2.cvtColor(rawImage, cv2.COLOR_BGR2RGB)
    return cv2.imencode(encodeFormat, rgbImage)[1].tobytes()


def transform_pil_image_to_bytes(
    img: Image,
    fmt: str = "JPEG",
) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
