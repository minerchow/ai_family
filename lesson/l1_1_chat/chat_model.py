"""1-1 模型连接：service 调用 get_chat_model，取得可复用的百炼客户端。"""
# 导入标准库缓存装饰器，复用已创建的模型客户端。
from functools import lru_cache

# 导入 LangChain 的 OpenAI 兼容客户端，用它连接百炼模型接口。
from langchain_openai import ChatOpenAI

# 导入脚手架读取好的配置对象，从中获取地址、Key 和模型名称。
from settings import settings


# 缓存函数成功返回的对象；函数无参数，因此后续调用复用同一个客户端。
# 缓存不保存回答，修改配置后需要重启后端重新创建客户端。
@lru_cache
# 提供模型客户端，无输入参数，返回 ChatOpenAI 对象。
# 首次调用时创建，后续复用；创建客户端本身不会向模型发送问题。
def get_chat_model() -> ChatOpenAI:
    # 创建并返回客户端对象，下面的参数配置连接方式和调用选项。
    return ChatOpenAI(
        # 读取完整 Base URL；客户端按 Chat Completions 协议拼接接口路径。
        base_url=settings.bailian_base_url,
        # 读取后端 Key，客户端将其用于请求认证，不发送给前端。
        api_key=settings.bailian_api_key,
        # 指定请求使用的模型名称，例如 qwen-plus。
        model=settings.bailian_chat_model,
        # 设置底层 HTTP 请求超时为 45 秒；前端超时为 60 秒。
        # 这是 HTTP 超时配置，不是对整个函数耗时的硬性截止计时。
        timeout=45,
        # 关闭 SDK 自动重试，失败后交给异常处理，避免一次操作重复发送请求。
        max_retries=0,
        # 使用非流式调用，等待服务端返回完整响应后读取回答。
        streaming=False,
        # 指定使用 /chat/completions，不切换到另一套 Responses 接口。
        use_responses_api=False,
    )