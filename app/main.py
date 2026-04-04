from typing import cast

from fastapi.exceptions import RequestValidationError
from starlette.types import ExceptionHandler

from app.api import health
from app.api.v1 import task as v1task
from app.api.v1 import yolo as v1yolo
from app.exceptions import AppException
from app.factory.app import create_app
from app.infra.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
)
from app.infra.lifespan.ml import set_ml_model
from app.infra.logger import setup_logging
from app.infra.middlewares import (
    RequestIdMiddleware,
    RequestLoggerMiddleware,
)

setup_logging()

app = create_app(
    lifespan=set_ml_model,
)

app.add_middleware(
    RequestIdMiddleware,
)
app.add_middleware(
    RequestLoggerMiddleware,
)

app.add_exception_handler(
    exc_class_or_status_code=AppException,
    handler=cast(ExceptionHandler, app_exception_handler),
)
app.add_exception_handler(
    exc_class_or_status_code=RequestValidationError,
    handler=cast(ExceptionHandler, validation_exception_handler),
)

app.include_router(health.router, tags=["Health"], prefix="/health")
app.include_router(v1yolo.router, tags=["v1", "yolo"], prefix="/v1/yolo")
app.include_router(v1task.router, tags=["v1", "task"], prefix="/v1/task")
