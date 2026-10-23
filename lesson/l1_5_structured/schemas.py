"""接口使用 ProductRequest 校验描述，提取业务使用 ProductInfo 校验模型结果。"""
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


# 接收页面的商品描述，字段校验失败时由脚手架返回参数错误。
class ProductRequest(BaseModel):
    # 描述必须提供，长度为 1～2000 个字符。
    description: str = Field(min_length=1, max_length=2000)

    # 检查 description 字段，避免空格通过长度校验。
    @field_validator("description")
    # 类方法接收当前类和待校验的字符串。
    @classmethod
    # 输入描述，返回原文；只有空白时抛出校验错误。
    def not_blank(cls, value: str) -> str:
        # strip 仅用于判断，不改变用户原文。
        if not value.strip():
            # Pydantic 将 ValueError 转换为字段校验错误。
            raise ValueError("商品描述不能为空")
        # 有效描述原样传给提取业务。
        return value


# 定义模型必须返回的三个字段，校验后作为接口的商品对象。
class ProductInfo(BaseModel):
    # forbid 表示拒绝这三个字段之外的额外字段。
    model_config = ConfigDict(extra="forbid")
    # 品牌可为 null，字符串最多 80 字；没有默认值，因此字段必须出现。
    brand: str | None = Field(max_length=80, description="输入明确写出的品牌，没有则为 null")
    # 价格可为 null；非空时非负、最多十位数字且最多两位小数。
    price: Decimal | None = Field(ge=0, max_digits=10, decimal_places=2, description="人民币价格，没有则为 null")
    # 卖点字段必须出现，最多八条；description 也会写入生成的 Schema。
    sellingPoints: list[str] = Field(max_length=8, description="输入明确写出的卖点，没有则为空列表")

    # 对品牌执行额外校验，null 合法，空白字符串不合法。
    @field_validator("brand")
    # 类方法接收当前类和字段值。
    @classmethod
    # 输入品牌或 None，返回有效值；空白品牌抛出校验错误。
    def brand_not_blank(cls, value: str | None) -> str | None:
        # 只有非空值需要检查正文。
        if value is not None and not value.strip():
            # 没有品牌应填 null，不能填空格。
            raise ValueError("品牌不能是空白字符串")
        # 保留模型返回的有效品牌或 None。
        return value

    # 检查列表中的每条卖点，而不只是列表条数。
    @field_validator("sellingPoints")
    # 类方法接收当前类和已通过类型校验的列表。
    @classmethod
    # 输入卖点列表，返回有效列表；空白项或超长项抛出校验错误。
    def points_not_blank(cls, values: list[str]) -> list[str]:
        # any 检查是否至少有一项为空白或超过 200 字。
        if any(not item.strip() or len(item) > 200 for item in values):
            # 字段不合格时拒绝整个对象。
            raise ValueError("卖点不能为空或超过 200 字")
        # 空列表可以通过，表示原文未说明卖点。
        return values