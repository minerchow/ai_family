"""1-3 请求与响应对象；router 接收角色及变量，service 返回回答和实际系统消息。"""
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# 继承 BaseModel，按字段类型和约束校验请求。
class PromptChatRequest(BaseModel):
    """限定三个角色；不同角色使用自己的变量，其他变量保留默认值。"""

    # 角色必填，只能使用下面三个标识。
    role: Literal["java", "translator", "copywriter"] = Field(description="角色标识")
    # 问题必填，长度限制为 1～2000 字符。
    question: str = Field(min_length=1, max_length=2000, description="用户输入")
    # Java 助教使用学习水平，未提交时默认入门。
    audience: Literal["入门", "进阶"] = Field(default="入门", description="Java 学习水平")
    # 翻译官使用目标语言，未提交时默认英语。
    targetLanguage: Literal["英语", "中文", "日语"] = Field(default="英语", description="翻译目标语言")
    # 文案写手使用商品名，默认降噪耳机，最多 80 字符。
    productName: str = Field(default="降噪耳机", min_length=1, max_length=80, description="文案中的商品名")

    # 在字段类型和长度检查后，补充非空白校验。
    @field_validator("question", "productName")
    # 类方法的首个参数 cls 接收当前模型类。
    @classmethod
    def not_blank(cls, value: str) -> str:
        """拒绝只有空白的输入；不改动输入正文和商品名。"""
        # 去掉首尾空白后检查是否还有内容。
        if not value.strip():
            # 抛出校验错误，由脚手架返回统一参数错误提示。
            raise ValueError("输入不能为空")
        # 返回原文，保留输入中的空格和换行。
        return value


# 定义统一响应 data 中的回答、角色、模型名和系统消息。
class PromptChatResponse(BaseModel):
    """保存回答、角色和展开后的系统消息，方便页面观察模板变量。"""

    # 保存模型返回的完整正文。
    answer: str = Field(description="完整回答")
    # 回传本次使用的角色标识。
    role: str = Field(description="本次使用的角色")
    # 保存模型名称，供页面显示。
    modelName: str = Field(description="实际模型名称")
    # 保存实际展开并发送的系统消息。
    systemPrompt: str = Field(description="展开变量后的系统消息，不含 Key")