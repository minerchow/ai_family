"""临时复现脚本：初始化 Tortoise 后直接调用 service.chat 拿真实异常。"""
import asyncio
import sys
from tortoise import Tortoise
from settings import settings
from lesson.l1_4_memory import service


async def main():
    await Tortoise.init(db_url=settings.database_url, modules={"models": ["lesson.l1_4_memory.models"]})
    await Tortoise.generate_schemas()
    try:
        result = await service.chat("有什么推荐的手机？")
        print("OK:", result)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
