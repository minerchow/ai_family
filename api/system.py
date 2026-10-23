import asyncio
import json
import platform
from datetime import datetime

import fastapi
from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from common.result import Result
from settings import settings

router = APIRouter(prefix="/api/system", tags=["系统"])


@router.get("/health", summary="健康检查")
async def health() -> Result:
    return Result.success(
        {
            "status": "UP",
            "application": settings.app_name,
            "runtime": f"Python {platform.python_version()}",
            "framework": f"FastAPI {fastapi.__version__}",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )


@router.get("/ai-config", summary="模型配置状态")
async def ai_config() -> Result:
    return Result.success(
        {
            "chat": {
                "baseUrl": settings.bailian_base_url,
                "model": settings.bailian_chat_model,
                "apiKeyConfigured": bool(settings.bailian_api_key.strip()),
            },
            "embedding": {
                "baseUrl": settings.embedding_base_url,
                "model": settings.embedding_model,
                "apiKeyConfigured": bool(settings.embedding_api_key.strip()),
            },
        }
    )


def to_json(data: dict) -> str:
    """与 Java 端 Jackson 的输出保持一致：不转义中文、不带空格。"""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


@router.post("/stream", summary="SSE 链路验证")
async def stream() -> EventSourceResponse:
    async def event_generator():
        messages = ["建立 SSE 连接", "推送课程事件", "流式链路验证完成"]
        for index, message in enumerate(messages, start=1):
            yield {
                "event": "step",
                "id": str(index),
                "data": to_json({"index": index, "message": message}),
            }
            await asyncio.sleep(0.35)
        yield {"event": "done", "data": to_json({"completed": True})}

    return EventSourceResponse(event_generator())
