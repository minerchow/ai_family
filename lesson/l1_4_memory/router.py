"""提供读取历史和发送问题两个接口，由脚手架自动注册。"""
from fastapi import APIRouter
from common.result import Result
from lesson.l1_4_memory.schemas import ChatRequest
from lesson.l1_4_memory import service

# 本节接口统一使用 /api/memory 前缀。
router = APIRouter(prefix="/api/memory")

# GET 请求用于恢复页面中的历史记录。
@router.get("/messages")
# 无输入参数，返回统一 Result 包装的全部历史。
async def messages():
    # 等待数据库读取完成，消息列表放入 data 字段。
    return Result.success(await service.list_messages())

# POST 请求提交当前问题，不接收前端拼装的历史。
@router.post("/chat")
# 接收校验后的请求，返回回答及历史条数。
async def chat(request: ChatRequest):
    # 将问题交给业务函数，成功结果使用统一格式返回。
    return Result.success(await service.chat(request.question))