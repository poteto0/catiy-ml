import asyncio
from unittest.mock import MagicMock

import torch

from app.domain.clip.usecase.classify_photo import classify_photo


def _make_processor(n_labels: int) -> MagicMock:
    processor = MagicMock()
    proc_out = MagicMock()
    # Return a plain dict so model(**inputs) unpacking works
    proc_out.to.return_value = {"pixel_values": torch.zeros(1, 3, 224, 224)}
    processor.return_value = proc_out
    return processor


def _make_model(logits: list[float]) -> MagicMock:
    model = MagicMock()
    mock_out = MagicMock()
    mock_out.logits_per_image = torch.tensor([logits])
    model.return_value = mock_out
    return model


class TestClassifyPhoto:
    def test_returns_one_result_per_label(self) -> None:
        labels = ["sleeping", "eating", "playing"]
        result = asyncio.run(
            classify_photo(
                device="cpu",
                image=MagicMock(),
                labels=labels,
                model=_make_model([1.0, 3.0, 2.0]),
                processor=_make_processor(len(labels)),
            )
        )
        assert len(result) == len(labels)

    def test_results_are_sorted_by_prob_descending(self) -> None:
        labels = ["sleeping", "eating", "playing"]
        # eating has the highest logit -> highest prob after softmax
        result = asyncio.run(
            classify_photo(
                device="cpu",
                image=MagicMock(),
                labels=labels,
                model=_make_model([1.0, 5.0, 2.0]),
                processor=_make_processor(len(labels)),
            )
        )
        assert result[0].label == "eating"
        assert result[-1].label == "sleeping"

    def test_result_labels_match_input_labels(self) -> None:
        labels = ["grooming", "scratching"]
        result = asyncio.run(
            classify_photo(
                device="cpu",
                image=MagicMock(),
                labels=labels,
                model=_make_model([2.0, 1.0]),
                processor=_make_processor(len(labels)),
            )
        )
        result_labels = {r.label for r in result}
        assert result_labels == set(labels)

    def test_single_label_is_top_result(self) -> None:
        labels = ["sleeping"]
        result = asyncio.run(
            classify_photo(
                device="cpu",
                image=MagicMock(),
                labels=labels,
                model=_make_model([1.0]),
                processor=_make_processor(1),
            )
        )
        assert len(result) == 1
        assert result[0].label == "sleeping"

    def test_prob_values_sum_to_one(self) -> None:
        labels = ["sleeping", "eating", "playing"]
        result = asyncio.run(
            classify_photo(
                device="cpu",
                image=MagicMock(),
                labels=labels,
                model=_make_model([1.0, 3.0, 2.0]),
                processor=_make_processor(len(labels)),
            )
        )
        total = sum(r.prob for r in result)
        assert abs(total - 1.0) < 1e-5
