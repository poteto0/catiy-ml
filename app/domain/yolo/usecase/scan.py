from typing import TYPE_CHECKING, Any

import numpy as np
from torch.fft import Tensor

if TYPE_CHECKING:
    from ultralytics.engine.results import Results


def has_target(
    result: Results,
    targetLabel: str = "cat",
) -> bool:
    targetIdx = detect_target_idx(
        result=result,
        targetLabel=targetLabel,
    )

    if targetIdx is None:
        return False

    return len(targetIdx) > 0


def detect_target_idx(
    result: Results,
    targetLabel: str = "cat",
) -> np.ndarray[tuple[Any, ...], np.dtype[np.int64]] | None:
    classNames = result.names

    targetId = None
    for key, name in classNames.items():
        if name == targetLabel:
            targetId = key
            break

    if targetId is None:
        return None

    boxes = result.boxes
    if boxes is None:
        return None

    classified = boxes.cls
    if not isinstance(classified, Tensor):
        return None

    npClassified = classified.cpu().numpy()
    return np.where(npClassified == targetId)[0]
