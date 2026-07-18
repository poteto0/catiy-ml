import torch
import torch.nn.functional as F
import torchvision.transforms as T
from loguru import logger
from PIL.Image import Image
from torchvision import transforms
from torchvision.models import EfficientNet

from app.api.schema.model import ClassifyResult, ClassifyResultUnit


def predict(
    model: EfficientNet,
    image: Image,
    classes: list[str] | None = None,
) -> ClassifyResult:
    preprocess = T.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225],
            ),  # Res
        ],
    )
    x = preprocess(image)
    x = x.unsqueeze(0)

    model.eval()
    with torch.no_grad():
        outputs = model(x)

    # Softmaxで確率に変換
    probabilities = F.softmax(outputs, dim=1)[0]

    # 確率が高い順にソート
    sorted_probs, sorted_indices = torch.sort(probabilities, descending=True)

    results = []
    for prob, idx in zip(sorted_probs, sorted_indices, strict=True):
        idx_val = idx.item()
        prob_val = prob.item()
        label_str = classes[idx_val] if (classes and idx_val < len(classes)) else None

        results.append(
            ClassifyResultUnit(
                idx=idx_val,
                prob=prob_val,
                label=label_str,
            ),
        )

    mostLikely = results[0]

    if mostLikely.label:
        logger.info(
            f"Top prediction: {mostLikely.label} (prob: {mostLikely.prob:.2%})",
        )
    else:
        logger.info(
            f"Top prediction: index {mostLikely.idx} (prob: {mostLikely.prob:.2%})",
        )

    return ClassifyResult(
        mostLikely=mostLikely,
        results=results,
    )
