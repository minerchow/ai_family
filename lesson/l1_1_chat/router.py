"""1-1 同步对话接口；脚手架自动扫描名为 router 的 APIRouter 并注册。"""
# 导入接口分组类，把本节接口组织成一个可注册的 router。
from fastapi import APIRouter

# 导入统一返回对象，用 code、msg、data 包装业务结果。
from common.result import Result
# 导入请求类型，FastAPI 按它解析并校验请求体 JSON。
from lesson.l1_1_chat.schemas import SyncChatRequest
# 导入同步对话函数，接口收到合法参数后调用它。
from lesson.l1_1_chat.service import chat

# prefix 设置这组接口共用的路径前缀。
# 变量名 router 供脚手架自动发现和注册，不需要手动改入口。
router = APIRouter(prefix="/api/chat")


# 注册 POST /api/chat/sync，把请求交给下面的接口函数。
@router.post("/sync")
# 接口函数：request 是已通过校验的请求对象，返回值是 Result。
# 使用普通 def，FastAPI 在线程池中执行阻塞调用，避免直接阻塞异步事件循环。
def sync_chat(request: SyncChatRequest) -> Result:
    # 先调用 chat 获得回答对象，再由 success 放入 data，补上成功码和提示。
    return Result.success(chat(request))