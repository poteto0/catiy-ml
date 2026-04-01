from fastapi.applications import Lifespan

from app.types.app import TypedFastAPI
from app.types.state import AppState


def create_app(
    *,
    lifespan: Lifespan[TypedFastAPI],
) -> TypedFastAPI:
    app = TypedFastAPI(
        lifespan=lifespan,
    )
    app.state = AppState()  # ここで初期化
    return app
