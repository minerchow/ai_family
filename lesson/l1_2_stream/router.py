"""流式对话接口：接收 POST 请求，把业务生成器交给 SSE 响应工具。"""
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from common.exception_handler import CustomException
from common.result import ResultCodeEnum
from lesson.l1_1_chat.schemas import SyncChatRequest
from lesson.l1_2_stream.service import stream_chat
from settings import settings

# 名为 router 的对象会被脚手架自动发现；设置公共路径前缀。
router = APIRouter(prefix="/api/chat")


# 注册 POST /api/chat/stream。
@router.post("/stream")
# 接收校验后的请求对象，返回持续发送事件的响应。
async def stream(request: SyncChatRequest) -> EventSourceResponse:
    # Key 全为空白时，直接返回配置错误，不开始推流。
    if not settings.bailian_api_key.strip():
        # 使用脚手架已有的异常和业务码，返回明确提示。
        raise CustomException(ResultCodeEnum.SYSTEM_ERROR, "还没有配置百炼 API Key，请检查后端配置")
    # 响应工具设置 text/event-stream，并负责事件分隔和默认心跳。
    return EventSourceResponse(stream_chat(request))