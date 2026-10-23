"""自动发现课程代码。

启动时扫描 api 和 lesson 目录下的全部 .py 文件：
- 模块里有名为 router 的 APIRouter，自动注册接口；
- 模块里定义了 Tortoise 模型，自动注册到数据库。
新增一节课只需要新建文件，不需要修改 main.py 和 database.py。
"""
import importlib
from functools import lru_cache
from pathlib import Path
from types import ModuleType

from fastapi import APIRouter
from tortoise.models import Model

BASE_DIR = Path(__file__).resolve().parent.parent
SCAN_PACKAGES = ("api", "lesson")


@lru_cache
def load_modules() -> tuple[ModuleType, ...]:
    modules = []
    for package in SCAN_PACKAGES:
        for path in sorted((BASE_DIR / package).rglob("*.py")):
            parts = path.relative_to(BASE_DIR).with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            modules.append(importlib.import_module(".".join(parts)))
    return tuple(modules)


def discover_routers() -> list[APIRouter]:
    routers = []
    for module in load_modules():
        router = getattr(module, "router", None)
        # 同一个 router 被其他模块 import 时只注册一次
        if isinstance(router, APIRouter) and router not in routers:
            routers.append(router)
    return routers


def discover_model_modules() -> list[str]:
    return [
        module.__name__
        for module in load_modules()
        if any(
            isinstance(value, type)
            and issubclass(value, Model)
            and value.__module__ == module.__name__
            for value in vars(module).values()
        )
    ]
