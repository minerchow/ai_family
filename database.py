from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from common.discovery import discover_model_modules
from settings import settings


@asynccontextmanager
async def database_lifespan(app: FastAPI):
    """应用启动时注册 Tortoise ORM，关闭时释放连接。

    这里只注册连接配置，第一次查询时才真正连接 MySQL，所以没有启动 MySQL 也能运行脚手架。
    """
    model_modules = discover_model_modules()
    # Tortoise 要求至少有一个模型；课程还没建表时跳过注册
    if not model_modules:
        yield
        return

    async with RegisterTortoise(
        app,
        db_url=settings.database_url,
        modules={"models": model_modules},
        use_tz=False,
        timezone="Asia/Shanghai",
    ):
        yield
