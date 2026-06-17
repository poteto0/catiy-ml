from typing import cast

import torch
from PIL.Image import Image
from transformers import CLIPModel, CLIPProcessor

from app.api.schema.model import ClipResult, LabelStr


async def classify_photo(
    device: str,
    image: Image,
    labels: list[LabelStr],
    model: CLIPModel,
    processor: CLIPProcessor,
) -> list[ClipResult]:
    texts = [f"a photo of a {label} cat" for label in labels]

    inputs = processor(
        text=texts,
        images=image,
        return_tensors="pt",
        padding=True,
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)[0]

    results = cast(list[ClipResult], [])
    for label, prob in zip(labels, probs.cpu().numpy(), strict=True):
        results.append(
            ClipResult(
                label=label,
                prob=prob,
            ),
        )

    return sorted(results, reverse=True)
