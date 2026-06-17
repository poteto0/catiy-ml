import asyncio
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from app.api.schema.model import ClipResult
from app.domain.clip.services.classify_activity_label import classify_activity_label
from app.exceptions.app import AppException


def _make_image_bytes() -> bytes:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestClassifyActivityLabel:
    def test_raises_app_exception_for_invalid_image(self) -> None:
        with pytest.raises(AppException):
            asyncio.run(
                classify_activity_label(
                    imgBytes=b"invalid",
                    labels=["sleeping"],
                    device="cpu",
                    clip=(MagicMock(), MagicMock()),
                ),
            )

    def test_returns_clip_response_with_most_likely_label(self) -> None:
        fake_results = [
            ClipResult(label="sleeping", prob=0.7),
            ClipResult(label="eating", prob=0.3),
        ]
        with patch(
            "app.domain.clip.services.classify_activity_label.classify_photo",
            new=AsyncMock(return_value=fake_results),
        ):
            result = asyncio.run(
                classify_activity_label(
                    imgBytes=_make_image_bytes(),
                    labels=["sleeping", "eating"],
                    device="cpu",
                    clip=(MagicMock(), MagicMock()),
                ),
            )

        assert result.mostLikelyLabel == "sleeping"
        assert result.results == fake_results

    def test_most_likely_label_is_first_result(self) -> None:
        fake_results = [
            ClipResult(label="grooming", prob=0.9),
            ClipResult(label="scratching", prob=0.1),
        ]
        with patch(
            "app.domain.clip.services.classify_activity_label.classify_photo",
            new=AsyncMock(return_value=fake_results),
        ):
            result = asyncio.run(
                classify_activity_label(
                    imgBytes=_make_image_bytes(),
                    labels=["grooming", "scratching"],
                    device="cpu",
                    clip=(MagicMock(), MagicMock()),
                ),
            )

        assert result.mostLikelyLabel == result.results[0].label

    def test_passes_labels_and_device_to_classify_photo(self) -> None:
        fake_results = [ClipResult(label="sleeping", prob=1.0)]
        mock_classify = AsyncMock(return_value=fake_results)

        with patch(
            "app.domain.clip.services.classify_activity_label.classify_photo",
            new=mock_classify,
        ):
            asyncio.run(
                classify_activity_label(
                    imgBytes=_make_image_bytes(),
                    labels=["sleeping"],
                    device="cuda",
                    clip=(MagicMock(), MagicMock()),
                ),
            )

        call_kwargs = mock_classify.call_args.kwargs
        assert call_kwargs["device"] == "cuda"
        assert call_kwargs["labels"] == ["sleeping"]
