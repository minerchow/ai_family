"""流式对话业务：接收问题和参数，调用百炼，逐块返回 SSE 事件。"""
import json
import logging
from secrets import randbelow

from langchain_core.messages import HumanMessage
from lesson.l1_1_chat.chat_model import get_chat_model
from lesson.l1_1_chat.schemas import SyncChatRequest

# 用当前模块名创建日志对象。
logger = logging.getLogger(__name__)


# 接收事件名和数据字典，返回 SSE 响应工具需要的事件字典。
def event(name: str, data: dict) -> dict:
    # event 是事件名称；data 编码为 JSON，ensure_ascii=False 保留中文字符。
    return {"event": name, "data": json.dumps(data, ensure_ascii=False)}


# 异步生成器：每次 yield 返回一条事件，由接口持续发送给页面。
async def stream_chat(request: SyncChatRequest):
    # 先记录结束原因，生成过程中会从模型响应更新这个值。
    finish_reason = "UNKNOWN"
    # 将客户端获取和模型调用放在异常处理范围内。
    try:
        # 复制模型配置并启用流式，复用底层连接，不修改同步对话的共享对象。
        model = get_chat_model().model_copy(update={"streaming": True})
        # 调用异步流接口；每次迭代取得一块结果，不等待完整答案。
        async for chunk in model.astream(
            # 只发送本次问题，HumanMessage 对应 user 消息。
            [HumanMessage(content=request.question)],
            # 传入本次温度，不修改共享客户端。
            temperature=request.temperature,
            # 页面 topP 对应模型的 top_p。
            top_p=request.topP,
            # 随机种子影响采样，不保证每次答案不同。
            seed=randbelow(2147483647) + 1,
            # 关闭思考模式，并保留百炼使用的 max_tokens 字段名。
            extra_body={"enable_thinking": False, "max_tokens": request.maxTokens},
        ):
            # 本节文本模型返回字符串；结束块可能没有正文。
            if chunk.content:
                # 把当前增量交给 SSE 响应，不拼成完整回答再返回。
                yield event("message", {"content": chunk.content})
            # 即使正文为空，也读取该块可能携带的结束原因。
            reason = chunk.response_metadata.get("finish_reason")
            # 只有模型提供了结束原因，才更新记录。
            if reason:
                # 转成大写，供页面判断 STOP 或 LENGTH。
                finish_reason = str(reason).upper()
        # 所有增量读取完后发送结束事件。
        yield event("done", {"finishReason": finish_reason})
    # 推流开始后不能改成普通 JSON 响应，失败信息也通过 SSE 返回。
    except Exception:
        # 保存完整异常信息，不把内部异常细节直接展示给用户。
        logger.exception("流式模型调用失败")
        # 发送错误事件，不再发送 done。
        yield event("error", {"message": "生成失败，请检查后端日志"})