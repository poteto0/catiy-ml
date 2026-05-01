"""猫検出テスト"""

from unittest.mock import MagicMock

import numpy as np
import pytest
import torch

from app.domain.yolo.usecase.scan import has_target, trim_all_target


def create_dummy_result(
    classNames: dict[int, str],
    detectedClasses: list[int] | None = None,
    detectedBoxes: list[list[int]] | None = None,
    origImg: np.ndarray | None = None,
    hasBoxes: bool = True,
) -> MagicMock:
    mockResult = MagicMock()
    mockResult.names = classNames
    mockResult.orig_img = (
        origImg if origImg is not None else np.zeros((100, 100, 3), dtype=np.uint8)
    )

    if not hasBoxes:
        mockResult.boxes = None
        return mockResult

    mockBoxes = MagicMock()
    if detectedClasses is not None:
        # mockBoxes.cls を Tensor として模擬
        mockCls = torch.tensor(detectedClasses, dtype=torch.float32)
        mockBoxes.cls = mockCls
    else:
        mockBoxes.cls = None

    if detectedBoxes is not None:
        mockXyxy = torch.tensor(detectedBoxes, dtype=torch.float32)
        mockBoxes.xyxy = mockXyxy
    elif detectedClasses is not None:
        mockXyxy = torch.zeros((len(detectedClasses), 4), dtype=torch.float32)
        mockBoxes.xyxy = mockXyxy
    else:
        mockBoxes.xyxy = None

    mockResult.boxes = mockBoxes
    return mockResult


@pytest.fixture
def data_with_cat_images() -> MagicMock:
    classNames = {0: "cat", 1: "dog"}
    detectedClasses = [0, 1, 0]
    detectedBoxes = [
        [10, 10, 20, 20],  # cat
        [30, 30, 40, 40],  # dog
        [50, 50, 60, 60],  # cat
    ]
    return create_dummy_result(
        classNames=classNames,
        detectedClasses=detectedClasses,
        detectedBoxes=detectedBoxes,
    )


@pytest.fixture
def data_wo_cat() -> MagicMock:
    return create_dummy_result(
        classNames={0: "cat", 1: "dog"},
        detectedClasses=[1, 1],  # dog のみ
    )


@pytest.fixture
def data_when_detect_failed() -> MagicMock:
    return create_dummy_result(
        classNames={0: "cat"},
        detectedClasses=[0, 1, 0],
        hasBoxes=False,
    )


@pytest.fixture
def data_with_cat_but_wo_axes() -> MagicMock:
    dummy = create_dummy_result(
        classNames={0: "cat", 1: "dog"},
        detectedClasses=[0, 1, 0],
    )
    dummy.boxes.xyxy = 1
    return dummy


def test_can_trim_all_of_targets(data_with_cat_images: MagicMock) -> None:
    """画像中にあるターゲットをcropして出力できる"""
    # Act
    actual = trim_all_target(data_with_cat_images, "cat")

    # Assert
    assert len(actual) == 2


def test_do_nothing_when_target_does_not_exist(
    data_wo_cat: MagicMock,
) -> None:
    """ターゲットが存在しない場合には何もしない"""
    # Act & Assert
    assert len(trim_all_target(data_wo_cat, "cat")) == 0


def test_do_nothing_when_detect_failed(
    data_when_detect_failed: MagicMock,
) -> None:
    """検出失敗したら何もしない"""
    # Act & Assert
    assert len(trim_all_target(data_when_detect_failed, "cat")) == 0


def test_do_nothing_when_target_does_not_has_tensor_axes(
    data_with_cat_but_wo_axes: MagicMock,
) -> None:
    """Tensorのxy座標をもっていなければ何もしない"""
    # Act & Assert
    assert len(trim_all_target(data_with_cat_but_wo_axes, "cat")) == 0


def test_can_scan_target(data_with_cat_images: MagicMock) -> None:
    """ターゲットを検出できる"""
    # Act & Assert
    assert has_target(data_with_cat_images, targetLabel="cat")


def test_not_found_target(data_wo_cat: MagicMock) -> None:
    """ターゲットが存在しない"""
    # Act & Assert
    assert not has_target(data_wo_cat, targetLabel="cat")


def test_fail_to_scan_is_not_found(
    data_when_detect_failed: MagicMock,
) -> None:
    """検出失敗したら存在しないと判定する"""
    # Act & Assert
    assert not has_target(data_when_detect_failed, targetLabel="cat")


def test_unknown_label_is_not_found(
    data_with_cat_images: MagicMock,
) -> None:
    """知らないラベルでは存しないと判定する"""
    # Act & Assert
    assert not has_target(data_with_cat_images, targetLabel="unknown")


def test_tensor_error_is_not_found() -> None:
    """型エラーが生じた場合に、検出失敗とする"""
    # Arrange
    dummy = MagicMock()
    dummy.names = {0: "cat"}
    mockBoxes = MagicMock()
    mockBoxes.cls = [0]  # List instead of Tensor
    dummy.boxes = mockBoxes

    # Act & Assert
    assert not has_target(dummy, targetLabel="cat")
