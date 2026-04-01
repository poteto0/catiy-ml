"""猫検出テスト"""

from unittest.mock import MagicMock

import torch

from app.domain.yolo.usecase.scan import has_target


class TestYoloUsecaseScan:
    def createDummyResult(
        self,
        classNames: dict[int, str],
        detectedClasses: list[int] | None = None,
        hasBoxes: bool = True,
    ) -> MagicMock:
        mockResult = MagicMock()
        mockResult.names = classNames

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

        mockResult.boxes = mockBoxes
        return mockResult

    def test_can_scan_target(self) -> None:
        """ターゲットを検出できる"""
        dummy = self.createDummyResult(
            classNames={0: "cat", 1: "dog"},
            detectedClasses=[0, 1, 0],
        )
        assert has_target(dummy, targetLabel="cat")

    def test_not_found_target(self) -> None:
        """ターゲットが存在しない"""
        dummy = self.createDummyResult(
            classNames={0: "cat", 1: "dog"},
            detectedClasses=[1, 1],  # dog のみ
        )
        assert not has_target(dummy, targetLabel="cat")

    def test_fail_to_scan_is_not_found(self) -> None:
        """検出失敗したら存在しない"""
        dummy = self.createDummyResult(
            classNames={0: "cat"},
            hasBoxes=False,
        )
        assert not has_target(dummy, targetLabel="cat")

    def test_unknown_label_is_not_found(self) -> None:
        """知らないラベルでは存在しない"""
        dummy = self.createDummyResult(
            classNames={0: "cat"},
            detectedClasses=[0],
        )
        assert not has_target(dummy, targetLabel="bird")

    def test_tensor_error_is_not_found(self) -> None:
        """tensor周りのエラーで存在しない"""
        dummy = MagicMock()
        dummy.names = {0: "cat"}
        mockBoxes = MagicMock()
        mockBoxes.cls = [0]  # List instead of Tensor
        dummy.boxes = mockBoxes

        assert not has_target(dummy, targetLabel="cat")
