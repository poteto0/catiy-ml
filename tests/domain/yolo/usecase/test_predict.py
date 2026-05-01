from unittest.mock import MagicMock

from PIL.Image import Image

from app.domain.yolo.usecase.predict import predict


class TestYoloUsecasePredict:
    def createDummyModel(
        self,
    ) -> MagicMock:
        mockModel = MagicMock()

        def mock_predict(__: Image) -> MagicMock:
            return MagicMock()

        mockModel.predict = mock_predict
        return mockModel

    def test_can_predict_by_model(self) -> None:
        # Arrange
        model = self.createDummyModel()

        # Act & Assert
        assert predict(model, MagicMock()) is not None
