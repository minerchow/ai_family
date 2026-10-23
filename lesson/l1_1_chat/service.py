"""1-1 同步对话业务：router 传入请求，本文件调用百炼并整理完整回答。"""
# 导入随机整数函数，randbelow(n) 返回 0 到 n-1 之间的整数。
from secrets import randbelow

# 导入用户消息类型，客户端将它转换为 role 为 user 的消息。
from langchain_core.messages import HumanMessage
# 导入 SDK 的认证异常类型，用于单独处理模型服务的认证失败。
from openai import AuthenticationError

# 导入脚手架的业务异常，通过全局处理器返回统一错误结构。
from common.exception_handler import CustomException
# 导入业务状态枚举，SYSTEM_ERROR 表示当前操作未能正常完成。
from common.result import ResultCodeEnum
# 导入客户端获取函数，在调用模型时取得缓存客户端。
from lesson.l1_1_chat.chat_model import get_chat_model
# 导入请求与响应类型，约定业务函数接收和返回的数据结构。
from lesson.l1_1_chat.schemas import SyncChatRequest, SyncChatResponse
# 导入脚手架读取好的配置对象，从中获取地址、Key 和模型名称。
from settings import settings


# 同步对话业务：接收校验后的问题和参数，调用模型并返回响应对象。
# 缺少 Key 或认证失败时抛出业务异常；其他异常交给全局处理器。
def chat(request: SyncChatRequest) -> SyncChatResponse:
    # 先检查 Key 去掉首尾空白后是否为空；为空时不创建客户端、不请求模型。
    if not settings.bailian_api_key.strip():
        # 抛出业务异常，由全局处理器将状态码和提示转换成统一 JSON 响应。
        raise CustomException(
            # 为异常选择系统错误业务码，它与 HTTP 响应状态是不同的字段。
            ResultCodeEnum.SYSTEM_ERROR,
            # 指定页面能看到的配置缺失提示，不暴露 Key 内容。
            "还没有配置百炼 API Key，请检查后端配置",
        )

    # 先生成 0～2147483646 的整数，再加 1，得到 1～2147483647 的种子。
    # 种子影响采样，但不同种子仍然可能得到相同答案。
    seed = randbelow(2147483647) + 1
    # 开始异常捕获范围，把客户端获取和模型调用中的认证失败单独处理。
    try:
        # 取得客户端并同步调用 invoke，等待完整响应，返回 AIMessage 对象。
        message = get_chat_model().invoke(
            # 用问题创建一条用户消息，放进消息列表；本次只发送当前问题。
            [HumanMessage(content=request.question)],
            # 将当前请求的温度传给这次调用，不修改缓存客户端的属性。
            temperature=request.temperature,
            # 把页面字段 topP 映射成模型请求中的 top_p，传入相同数值。
            top_p=request.topP,
            # 给当前调用设置上面生成的随机种子，影响模型采样过程。
            seed=seed,
            # extra_body 的字段合并到实际请求体；enable_thinking=False 关闭思考模式。
            # max_tokens 使用本次输出上限，放在 extra_body 中保留百炼使用的字段名。
            extra_body={"enable_thinking": False, "max_tokens": request.maxTokens},
        )
    # 捕获 SDK 认证异常，将原异常保存到 exception，方便保留错误来源。
    except AuthenticationError as exception:
        # 抛出业务异常，由全局处理器将状态码和提示转换成统一 JSON 响应。
        raise CustomException(
            # 传入系统错误业务码和认证失败提示，由全局处理器返回给页面。
            ResultCodeEnum.SYSTEM_ERROR, "百炼 API Key 无效，请检查配置"
        # 关闭异常构造，并通过 from 保留原认证异常作为原因，便于日志追查。
        ) from exception

    # 读取响应元数据字典，模型名和结束原因保存在这里，正文在 content 中。
    metadata = message.response_metadata
    # 创建响应对象并返回，下面的字段组成页面需要展示的结果。
    return SyncChatResponse(
        # 把模型返回的回答正文保存到 answer。
        answer=message.content,
        # 优先读取元数据中的模型名；缺失或为空时回退到配置中的名称。
        modelName=metadata.get("model_name") or settings.bailian_chat_model,
        # 将当前请求的温度传给这次调用，不修改缓存客户端的属性。
        temperature=request.temperature,
        # 把本次请求的核采样值原样回传，供当前回答展示。
        topP=request.topP,
        # 把本次请求的最大输出 Token 数原样回传，供当前回答展示。
        maxTokens=request.maxTokens,
        # 取结束原因，缺失或为空时使用 UNKNOWN；转成字符串后统一大写。
        finishReason=str(metadata.get("finish_reason") or "UNKNOWN").upper(),
    )