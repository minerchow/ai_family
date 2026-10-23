"""1-1 请求与响应对象，由 router 接收参数、由 service 返回回答。"""
# BaseModel 定义数据对象；Field 声明字段约束；field_validator 为字段添加自定义校验。
from pydantic import BaseModel, Field, field_validator


# 请求对象：继承 BaseModel，让 FastAPI 将请求 JSON 解析为对象并校验。
# 四个字段都没有默认值，因此必须提交；业务函数收到的是校验通过后的对象。
class SyncChatRequest(BaseModel):

    # question 是字符串；min_length=1、max_length=2000 限制长度为 1～2000。
    question: str = Field(min_length=1, max_length=2000)
    # temperature 是浮点数；ge=0、le=1.9 表示包含边界的 0～1.9。
    temperature: float = Field(ge=0, le=1.9)
    # topP 是浮点数；ge=0.1、le=1 限制累计概率阈值为 0.1～1。
    # 页面使用 topP 命名，调用模型时再转换为 top_p。
    topP: float = Field(ge=0.1, le=1)
    # maxTokens 是整数，范围是 1～4096；它限制输出 Token 数，不是汉字数。
    # strict=True 拒绝小数、布尔值和数字字符串，要求请求直接提供 JSON 整数。
    maxTokens: int = Field(ge=1, le=4096, strict=True)

    # 为 question 字段注册校验器；默认在字段类型和 Field 约束检查后调用。
    @field_validator("question")
    # 将校验器定义为类方法，首个参数 cls 接收当前模型类，而不是对象实例。
    @classmethod
    # 检查问题是否全为空白。cls 是模型类，value 是已解析的字符串。
    # 通过时返回原文；失败时抛出 ValueError，由 Pydantic 汇总为校验错误。
    def check_question(cls, value: str) -> str:
        # strip 去掉首尾空白，空字符串在条件判断中为 False；not 将其反转。
        if not value.strip():
            # 终止字段校验并说明原因，FastAPI 将校验错误交给全局异常处理器。
            raise ValueError("问题不能为空")
        # 返回未经 strip 修改的原文，保留用户输入的空格和换行。
        return value


# 响应对象：保存回答、模型名、本次参数和结束原因，作为接口 data 返回。
# 继承 BaseModel 后，这些字段可以被统一返回工具转换为 JSON 数据。
class SyncChatResponse(BaseModel):

    # answer 是回答字符串，业务函数从 AIMessage.content 取值。
    answer: str
    # modelName 保存响应中的模型名；服务端未提供时使用本地配置值。
    modelName: str
    # 回传本次请求的温度，页面据此显示每条回答当时使用的参数。
    temperature: float
    # 回传本次请求的核采样值，展示本次请求实际使用的参数。
    topP: float
    # 回传本次设置的输出上限；这个值不是实际生成的 Token 数量。
    maxTokens: int
    # 保存大写结束原因，页面通过 LENGTH 判断是否达到上限。
    finishReason: str