"""商品结构化提取接口，成功数据是对象而不是一段 JSON 字符串。"""
from fastapi import APIRouter
from common.result import Result
from lesson.l1_5_structured.schemas import ProductRequest
from lesson.l1_5_structured.service import extract_product

# 接口统一使用 /api/structured 前缀，由脚手架自动注册。
router = APIRouter(prefix="/api/structured")


# POST 请求接收描述，完整路径为 /api/structured/product。
@router.post("/product")
# 输入 ProductRequest，提取成功时返回统一包装的商品对象；异常由脚手架处理。
async def product(request: ProductRequest):
    # 等待提取与校验完成，将对象放入 Result 的 data 字段。
    return Result.success(await extract_product(request))