from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    app_name: str = "AI 大模型应用开发全家桶 · FastAPI"
    host: str = "0.0.0.0"
    port: int = 9091

    database_url: str = "mysql://root:123456@localhost:3306/ai_family_fastapi"
    file_storage_path: Path = BASE_DIR.parent / "files"
    max_upload_size: int = 20 * 1024 * 1024

    # 推理模型
    bailian_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    bailian_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("DASHSCOPE_API_KEY", "BAILIAN_API_KEY"),
    )
    bailian_chat_model: str = "qwen-plus"

    # 向量化模型：中转站与推理模型分开配置
    embedding_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-v4"

    @model_validator(mode="after")
    def default_embedding_key(self):
        # 中转站的 key 未单独配置时，退回推理模型的 key
        if not self.embedding_api_key.strip():
            self.embedding_api_key = self.bailian_api_key
        return self

    # 使用绝对路径读取 .env，不受启动目录影响
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
