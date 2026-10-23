"""读取历史、调用模型、保存问题与回答。"""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from common.exception_handler import CustomException
from common.result import ResultCodeEnum
from lesson.l1_1_chat.chat_model import get_chat_model
from lesson.l1_4_memory.models import MemoryMessage

# 无输入参数，返回数据库中按发言顺序排列的全部消息，供刷新恢复。
async def list_messages():
    # values 只取页面需要的字段，返回字典列表。
    return await MemoryMessage.all().order_by("id").values("id", "role", "content")

# 接收当前问题，读取最近历史，生成并保存回答，返回回答及历史条数。
async def chat(question):
    # 倒序取最新 20 条；数据库仍保留更早的消息。
    rows = await MemoryMessage.all().order_by("-id").limit(20)
    # 将倒序结果反转，恢复较早消息在前的发言顺序。
    rows.reverse()
    # 每次调用都先加入助手身份，System 规则不写入消息表。
    messages = [SystemMessage(content="你是一位数码商城助手，请根据对话历史回答用户。")]
    # 将数据库中的每条发言转换成模型需要的消息对象。
    for row in rows:
        # 用户记录用 HumanMessage，模型记录用 AIMessage。
        message = HumanMessage(content=row.content) if row.role == "user" else AIMessage(content=row.content)
        # 按数据库顺序追加，保证模型能理解先前对话。
        messages.append(message)
    # 本次问题排在历史之后，不能提前保存再重复加入上下文。
    messages.append(HumanMessage(content=question))
    # 异步请求完整回答；复用 1-1 的模型配置，不修改其文件。
    reply = await get_chat_model().ainvoke(messages,
        # 关闭思考模式，限制本次输出长度。
        extra_body={"enable_thinking": False, "max_tokens": 1024})
    # 空白或非文字结果不能作为有效历史保存。
    if not isinstance(reply.content, str) or not reply.content.strip():
        # 由脚手架统一返回明确的业务错误。
        raise CustomException(ResultCodeEnum.SYSTEM_ERROR, "模型没有返回有效回答，请重试")
    # 有效回答生成后，先保存用户问题。
    await MemoryMessage.create(role="user", content=question)
    # 再保存模型回答，本节使用普通顺序写入。
    await MemoryMessage.create(role="assistant", content=reply.content)
    # 返回回答与实际使用的历史条数，不计入 System 和当前问题。
    return {"answer": reply.content, "historyMessages": len(rows)}