import json
import sys
from typing import TYPE_CHECKING

from loguru import logger

from app.infra.middlewares.request_id import requestIdVar

if TYPE_CHECKING:
    from loguru import Record


def setup_logging() -> None:
    logger.remove()

    def serialize(record: Record) -> None:
        subset = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "location": f"{record['file'].path}:{record['line']}",
            "request_id": requestIdVar.get(),
            **record["extra"],
        }
        if record["exception"]:
            subset["exc_info"] = str(record["exception"])
        record["extra"]["serialized"] = json.dumps(subset, ensure_ascii=False)

    logger.add(
        sys.stdout,
        format="{extra[serialized]}\n",
        filter=lambda record: serialize(record) or True,
    )
