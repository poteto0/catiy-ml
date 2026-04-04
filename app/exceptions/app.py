from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class AppException(Exception):
    def __init__(
        self,
        code: str,
        msg: str,
        statusCode: int = HTTP_500_INTERNAL_SERVER_ERROR,
        cause: Exception | None = None,
    ) -> None:
        self.code = code
        self.msg = msg
        self.statusCode = statusCode
        self.cause = cause
