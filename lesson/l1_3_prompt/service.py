"""1-3 Prompt 业务；router 传入变量，本文件展开角色模板并调用模型。"""
from openai import AuthenticationError

from common.exception_handler import CustomException
from common.result import ResultCodeEnum
from lesson.l1_1_chat.chat_model import get_chat_model
from lesson.l1_3_prompt.prompts import PROMPTS
from lesson.l1_3_prompt.schemas import PromptChatRequest, PromptChatResponse
from settings import settings


# 展开角色模板，异步等待完整模型回答。
async def chat(request: PromptChatRequest) -> PromptChatResponse:
    """根据角色生成 system/human 消息，异步等待完整回答并返回实际提示词。"""
    # Key 为空时直接返回配置提示，不请求模型。
    if not settings.bailian_api_key.strip():
        raise CustomException(ResultCodeEnum.SYSTEM_ERROR, "还没有配置百炼 API Key，请先完成 0-3 节的配置")
    # Pydantic 已限制 role 范围，不会访问到不存在的模板。
    # invoke 在这里仅展开文本，并没有调用模型；to_messages 返回消息对象列表。
    messages = PROMPTS[request.role].invoke(request.model_dump()).to_messages()
    try:
        # ainvoke 发起一次模型请求，await 等待完整 AIMessage。
        answer = await get_chat_model().ainvoke(
            messages,
            # 固定温度，集中观察角色与变量的作用。
            temperature=0.7,
            # 固定核采样，与同步对话默认值一致。
            top_p=0.8,
            # 关闭思考模式；最大输出为 1024 Token，足够观察角色的简短回答。
            extra_body={"enable_thinking": False, "max_tokens": 1024},
        )
    # 认证失败时转换为页面可读的业务提示。
    except AuthenticationError as exception:
        raise CustomException(ResultCodeEnum.SYSTEM_ERROR, "百炼 API Key 无效，请检查配置") from exception
    # 整理回答和实际提示词，交给接口返回。
    return PromptChatResponse(
        # AIMessage.content 保存回答正文。
        answer=answer.content,
        # 回传本次选择的角色。
        role=request.role,
        # 未返回模型名时，回退到后端配置值。
        modelName=answer.response_metadata.get("model_name") or settings.bailian_chat_model,
        # 第一条消息是实际发送的 System 消息。
        systemPrompt=messages[0].content,
    )