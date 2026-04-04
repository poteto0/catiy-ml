from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.status import HTTP_400_BAD_REQUEST


async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> Response:
    logger.error(exc)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"code": "bad request"},
    )
