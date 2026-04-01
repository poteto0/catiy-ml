from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from fastapi import Request

    from app.types.state import AppState


def get_state(request: Request) -> AppState:
    return cast("AppState", request.state)
