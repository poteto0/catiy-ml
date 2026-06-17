from transformers import CLIPModel, CLIPProcessor

from app.api.schema.model import ClipRequestLabels, ClipResponse
from app.domain.clip.usecase.classify_photo import classify_photo
from app.exceptions.app import AppException
from app.utils.image import verify_image


async def classify_activity_label(
    imgBytes: bytes,
    labels: ClipRequestLabels,
    device: str,
    clip: tuple[CLIPModel, CLIPProcessor],
) -> ClipResponse:
    try:
        img = verify_image(imgBytes)
    except AppException:
        raise

    (model, processor) = clip

    results = await classify_photo(
        device=device,
        labels=labels,
        image=img,
        model=model,
        processor=processor,
    )

    return ClipResponse(
        mostLikelyLabel=results[0].label,
        results=results,
    )
