import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from common.result import Result, ResultCodeEnum

logger = logging.getLogger(__name__)


class CustomException(Exception):
    """业务异常：返回 HTTP 200，错误码和提示写在 Result 里。"""

    def __init__(self, result_code: ResultCodeEnum, msg: str | None = None):
        self.code = result_code.code
        self.msg = msg or result_code.msg
        super().__init__(self.msg)


def result_response(result: Result, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=result.model_dump())


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CustomException)
    async def custom_exception_handler(_: Request, exc: CustomException):
        return result_response(Result(code=exc.code, msg=exc.msg))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        logger.warning("请求参数错误: %s", exc.errors())
        return result_response(Result.error(ResultCodeEnum.PARAM_ERROR))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            result = Result.error(ResultCodeEnum.NOT_FOUND, "接口不存在")
        elif exc.status_code == 405:
            result = Result.error(ResultCodeEnum.METHOD_NOT_ALLOWED)
        else:
            result = Result(code=str(exc.status_code), msg=str(exc.detail))
        return result_response(result, exc.status_code)

    # 未知异常不能交给 @app.exception_handler(Exception)：那样响应会绕过 CORS 中间件，
    # 浏览器只会看到跨域错误。这里用中间件兜底，并且必须在 CORS 中间件之前注册。
    @app.middleware("http")
    async def catch_unknown_exception(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("系统异常")
            return result_response(Result.error(ResultCodeEnum.SYSTEM_ERROR), 500)
