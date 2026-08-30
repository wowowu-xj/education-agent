"""应用配置。

通过环境变量或 .env 文件加载。

字段命名规则：**全部大写，与环境变量名逐字一致**。
因为 model_config 使用 case_sensitive=True，字段名就是环境变量名——
写成小写的 `jwt_secret_key` 会导致 `JWT_SECRET_KEY=xxx` 静默失效、
继续沿用代码库里的默认占位密钥。新增字段时务必保持大写。
"""
from __future__ import annotations

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 仅供本地开发的占位密钥。APP_ENV=prod 时会被校验器拒绝。
DEFAULT_JWT_SECRET = "dev-secret-change-me-in-production"

# 生产密钥最小长度（HS256 建议 >= 32 字符熵）。
MIN_PROD_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """全局设置。

    生产环境必须设置 APP_ENV=prod 且通过环境变量提供 JWT_SECRET_KEY。
    生成密钥：python -c "import secrets; print(secrets.token_urlsafe(48))"
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # 运行环境
    # dev：本地开发；test：自动化测试；prod：生产。
    # prod 会强校验密钥强度，并关闭 API 文档（见 app/main.py）。
    APP_ENV: Literal["dev", "test", "prod"] = "dev"
    APP_NAME: str = "ChemAI"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "sqlite:///./chemai.db"

    # JWT
    JWT_SECRET_KEY: str = DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    # 逗号分隔的允许来源，如 "https://app.chemai.com,https://admin.chemai.com"。
    # 留空表示不注册 CORS 中间件（同源部署时的默认状态）。
    CORS_ORIGINS: str = ""

    # 向量检索
    # ChromaDB 持久化目录（已加入 .gitignore）。
    CHROMA_DB_PATH: str = "./chroma_db"
    # dashscope 嵌入服务 API Key（留空则回退到环境变量 / MD5 伪向量降级）。
    DASHSCOPE_API_KEY: str = ""
    # dashscope text-embedding-v3 输出维度。
    EMBEDDING_DIMENSION: int = 1024

    @property
    def is_production(self) -> bool:
        """是否生产环境。用于决定是否暴露 API 文档等敏感入口。"""
        return self.APP_ENV == "prod"

    @property
    def cors_origins_list(self) -> list[str]:
        """把逗号分隔的 CORS_ORIGINS 解析成列表。"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @model_validator(mode="after")
    def _guard_production_config(self) -> Settings:
        """生产环境启动期硬校验：宁可起不来，也不要带着默认密钥上线。"""
        if not self.is_production:
            return self

        if self.JWT_SECRET_KEY == DEFAULT_JWT_SECRET:
            raise ValueError(
                "APP_ENV=prod 时必须通过环境变量 JWT_SECRET_KEY 提供真实密钥，"
                "不能沿用代码库中的默认占位值——该值是公开的，任何人都能伪造 token。"
            )
        if len(self.JWT_SECRET_KEY) < MIN_PROD_SECRET_LENGTH:
            raise ValueError(
                f"JWT_SECRET_KEY 长度为 {len(self.JWT_SECRET_KEY)}，"
                f"生产环境要求至少 {MIN_PROD_SECRET_LENGTH} 个字符。"
            )
        if self.DEBUG:
            raise ValueError("APP_ENV=prod 时不允许 DEBUG=True。")
        return self


settings = Settings()
