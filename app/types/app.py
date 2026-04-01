from typing import TYPE_CHECKING

from fastapi import FastAPI

if TYPE_CHECKING:
    from app.types.state import AppState


class TypedFastAPI(FastAPI):
    # 標準の state を AppState 型として再定義
    state: AppState
