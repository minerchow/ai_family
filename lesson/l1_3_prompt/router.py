"""1-3 角色对话接口；返回脚手架统一 Result，自动注册路由。"""
from fastapi import APIRouter

from common.result import Result
from lesson.l1_3_prompt.schemas import PromptChatRequest
from lesson.l1_3_prompt.service import chat

# router 由脚手架自动发现，prefix 设置公共路径。
router = APIRouter(prefix="/api/prompt")


# 注册 POST /api/prompt/chat，使用统一响应结构。
@router.post("/chat")
# FastAPI 先校验请求，再执行异步接口函数。
async def prompt_chat(request: PromptChatRequest) -> Result:
    """校验角色和变量后调用异步业务，将完整回答放在 data 中。"""
    # 等待业务结果，将回答对象放进统一响应的 data。
    return Result.success(await chat(request))