from unittest.mock import MagicMock

from fastapi import Depends

from app.infra.depends.ml import get_catiy_yolo, get_clip, get_device


def test_can_get_yolo_model_from_state() -> None:
    """stateからモデルを取得できる"""
    # Arrange
    request = MagicMock()
    state = MagicMock()
    request.app.state = state

    # Act
    actual = Depends(get_catiy_yolo(request))

    # Assert
    assert actual is not None


def test_can_get_clip_model_and_processor_from_state() -> None:
    """stateからclipのモデルと前処理器を取得できる"""
    # Arrange
    request = MagicMock()
    state = MagicMock()
    request.app.state = state

    # Act
    (model, processor) = get_clip(request)

    # Assert
    assert model is not None
    assert processor is not None


def test_get_device() -> None:
    """stateからデバイスを取得できる"""
    # Arrange
    request = MagicMock()
    state = MagicMock()
    state.device = "cpu"
    request.app.state = state

    # Act
    actual = get_device(request)

    # Assert
    assert actual == "cpu"
