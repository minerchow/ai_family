"""校验页面提交的问题。"""
from pydantic import BaseModel, Field, field_validator

# 接收当前问题；校验失败时由脚手架返回参数错误。
class ChatRequest(BaseModel):
    # 问题至少一个字符，最长 2000 个字符。
    question: str = Field(min_length=1, max_length=2000)

    # 校验 question 的内容，避免只输入空格也调用模型。
    @field_validator("question")
    # 类方法接收当前模型类与待检查的字段值。
    @classmethod
    # 输入问题字符串，返回原文；空白内容抛出校验错误。
    def not_blank(cls, value):
        # strip 仅用于检查，不修改用户正文中的缩进和换行。
        if not value.strip():
            # Pydantic 将此异常作为请求参数错误处理。
            raise ValueError("问题不能为空")
        # 有效问题原样交给业务函数。
        return value