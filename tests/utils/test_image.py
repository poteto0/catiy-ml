import io

import numpy as np
import pytest
from PIL import Image

from app.exceptions.app import AppException
from app.utils.image import (
    transform_pil_image_to_bytes,
    transform_raw_image_to_rgb_bytes,
    verify_image,
)


def _make_image_bytes(fmt: str = "JPEG") -> bytes:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class TestTransformRawImageToRgbBytes:
    def test_returns_bytes(self) -> None:
        raw = np.zeros((10, 10, 3), dtype=np.uint8)
        result = transform_raw_image_to_rgb_bytes(raw)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_accepts_custom_encode_format(self) -> None:
        raw = np.zeros((10, 10, 3), dtype=np.uint8)
        result = transform_raw_image_to_rgb_bytes(raw, encodeFormat=".png")
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestTransformPilImageToBytes:
    def test_returns_bytes(self) -> None:
        img = Image.new("RGB", (10, 10), color=(0, 255, 0))
        result = transform_pil_image_to_bytes(img)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_returns_png_bytes_when_fmt_is_png(self) -> None:
        img = Image.new("RGB", (10, 10), color=(0, 255, 0))
        result = transform_pil_image_to_bytes(img, fmt="PNG")
        # PNG magic bytes: \x89PNG
        assert result[:4] == b"\x89PNG"

    def test_roundtrip_preserves_image(self) -> None:
        original = Image.new("RGB", (20, 20), color=(128, 64, 32))
        result_bytes = transform_pil_image_to_bytes(original, fmt="PNG")
        recovered = Image.open(io.BytesIO(result_bytes))
        assert recovered.size == original.size


class TestVerifyImage:
    def test_returns_pil_image_for_valid_bytes(self) -> None:
        result = verify_image(_make_image_bytes())
        assert isinstance(result, Image.Image)

    def test_returned_image_is_usable(self) -> None:
        result = verify_image(_make_image_bytes())
        assert result.size == (10, 10)

    def test_raises_app_exception_for_invalid_bytes(self) -> None:
        with pytest.raises(AppException) as exc_info:
            verify_image(b"not an image")
        assert exc_info.value.statusCode == 400

    def test_raises_app_exception_for_empty_bytes(self) -> None:
        with pytest.raises(AppException):
            verify_image(b"")
