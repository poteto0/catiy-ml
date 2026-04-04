from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger

from app.exceptions import AppException


async def app_exception_handler(_: Request, exc: AppException) -> Response:
    logger.error(exc.msg, extra={"cause": exc.cause})
    return JSONResponse(
        status_code=exc.statusCode,
        content={"code": exc.code},
    )
