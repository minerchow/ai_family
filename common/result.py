from enum import Enum
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class ResultCodeEnum(Enum):
    SUCCESS = ("200", "请求成功")
    PARAM_ERROR = ("400", "请求参数错误")
    NOT_FOUND = ("404", "资源不存在")
    METHOD_NOT_ALLOWED = ("405", "请求方法不支持")
    SYSTEM_ERROR = ("500", "系统异常，请查看后端控制台日志")

    def __init__(self, code: str, msg: str):
        self.code = code
        self.msg = msg


class Result(BaseModel):
    code: str
    msg: str
    data: Any = None

    @classmethod
    def success(cls, data: Any = None) -> "Result":
        return cls(
            code=ResultCodeEnum.SUCCESS.code,
            msg=ResultCodeEnum.SUCCESS.msg,
            data=jsonable_encoder(data),
        )

    @classmethod
    def error(cls, result_code: ResultCodeEnum, msg: str | None = None) -> "Result":
        return cls(code=result_code.code, msg=msg or result_code.msg)
