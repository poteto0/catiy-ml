from unittest.mock import MagicMock

from fastapi import Depends

from app.infra.depends.ml import get_catiy_yolo


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
