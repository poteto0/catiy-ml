# middleware/request_id.py
import uuid
from contextvars import ContextVar
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send

requestIdVar: ContextVar[str] = ContextVar("requestId", default="-")


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        requestId = str(uuid.uuid4())
        requestIdVar.set(requestId)
        scope["state"]["request_id"] = requestId

        async def send_with_header(message: dict[Any, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", requestId.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(
            scope,
            receive,
            send_with_header,  # ty:ignore
        )
