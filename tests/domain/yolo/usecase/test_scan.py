"""猫検出テスト"""

from unittest.mock import MagicMock

import numpy as np
import torch

from app.domain.yolo.usecase.scan import has_target, trim_all_target


class TestYoloUsecasexcan:
    def createDummyResult(
        self,
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

    def test_can_trim_all_of_targets(self) -> None:
        """画像中にあるターゲットをcropして出力できる"""
        # Arrange
        classNames = {0: "cat", 1: "dog"}
        detectedClasses = [0, 1, 0]
        detectedBoxes = [
            [10, 10, 20, 20],  # cat
            [30, 30, 40, 40],  # dog
            [50, 50, 60, 60],  # cat
        ]
        dummy = self.createDummyResult(
            classNames=classNames,
            detectedClasses=detectedClasses,
            detectedBoxes=detectedBoxes,
        )

        # Act
        actual = trim_all_target(dummy, "cat")

        # Assert
        assert len(actual) == 2

    def test_do_nothing_when_target_does_not_exist(self) -> None:
        """ターゲットが存在しない場合には何もしない"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat", 1: "dog"},
            detectedClasses=[1, 1],  # dog のみ
        )

        # Act & Assert
        assert len(trim_all_target(dummy, "cat")) == 0

    def test_do_nothing_when_detect_failed(self) -> None:
        """検出失敗したら何もしない"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat"},
            detectedClasses=[0, 1, 0],
            hasBoxes=False,
        )

        # Act & Assert
        assert len(trim_all_target(dummy, "cat")) == 0

    def test_do_nothing_when_target_does_not_has_tensor_axes(self) -> None:
        """Tensorのxy座標をもっていなければ何もしない"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat", 1: "dog"},
            detectedClasses=[0, 1, 0],
        )
        dummy.boxes.xyxy = 1

        # Act & Assert
        assert len(trim_all_target(dummy, "cat")) == 0

    def test_can_scan_target(self) -> None:
        """ターゲットを検出できる"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat", 1: "dog"},
            detectedClasses=[0, 1, 0],
        )

        # Act & Assert
        assert has_target(dummy, targetLabel="cat")

    def test_not_found_target(self) -> None:
        """ターゲットが存在しない"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat", 1: "dog"},
            detectedClasses=[1, 1],  # dog のみ
        )

        # Act & Assert
        assert not has_target(dummy, targetLabel="cat")

    def test_fail_to_scan_is_not_found(self) -> None:
        """検出失敗したら存在しないと判定する"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat"},
            hasBoxes=False,
        )

        # Act & Assert
        assert not has_target(dummy, targetLabel="cat")

    def test_unknown_label_is_not_found(self) -> None:
        """知らないラベルでは存しないと判定する"""
        # Arrange
        dummy = self.createDummyResult(
            classNames={0: "cat"},
            detectedClasses=[0],
        )

        # Act & Assert
        assert not has_target(dummy, targetLabel="bird")

    def test_tensor_error_is_not_found(self) -> None:
        """型エラーが生じた場合に、検出失敗とする"""
        # Arrange
        dummy = MagicMock()
        dummy.names = {0: "cat"}
        mockBoxes = MagicMock()
        mockBoxes.cls = [0]  # List instead of Tensor
        dummy.boxes = mockBoxes

        # Act & Assert
        assert not has_target(dummy, targetLabel="cat")
