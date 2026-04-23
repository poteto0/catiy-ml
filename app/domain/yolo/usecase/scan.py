from typing import Any

import cv2
import numpy as np
from torch.fft import Tensor
from ultralytics.engine.results import Results


def trim_all_target(
    result: Results,
    targetLabel: str = "cat",
) -> list[np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]]] | None:
    targetIndices = _detect_target_idx(
        result=result,
        targetLabel=targetLabel,
    )
    if targetIndices is None:
        return None

    resultBoxes = result.boxes
    if resultBoxes is None:
        return None

    xyBoxes = resultBoxes.xyxy
    if not isinstance(xyBoxes, Tensor):
        return None

    catImages: list[np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]]] = []
    labeledXy = xyBoxes.cpu().numpy()
    for _, targetIdx in enumerate(targetIndices):
        x1, y1, x2, y2 = labeledXy[targetIdx].astype(int)

        trimmedCat = result.orig_img[y1:y2, x1:x2]
        trimmedCatRGB = cv2.cvtColor(trimmedCat, cv2.COLOR_BGR2RGB)
        catImages.append(trimmedCatRGB)
    return catImages


def has_target(
    result: Results,
    targetLabel: str = "cat",
) -> bool:
    targetIdx = _detect_target_idx(
        result=result,
        targetLabel=targetLabel,
    )

    if targetIdx is None:
        return False

    return len(targetIdx) > 0


def _detect_target_idx(
    result: Results,
    targetLabel: str = "cat",
) -> np.ndarray[tuple[Any, ...], np.dtype[np.int64]] | None:
    classNames = result.names

    targetId = _get_target_id(
        classNames=classNames,
        targetLabel=targetLabel,
    )
    if targetId < 0:
        return None

    boxes = result.boxes
    if boxes is None:
        return None

    classified = boxes.cls
    if not isinstance(classified, Tensor):
        return None

    npClassified = classified.cpu().numpy()
    return np.where(npClassified == targetId)[0]


def _get_target_id(
    classNames: dict[int, str],
    targetLabel: str,
) -> int:
    for classId, name in classNames.items():
        if name == targetLabel:
            return classId
    return -1
