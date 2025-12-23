"""
backend/app/config/settings.py - 配置层

本阶段目标：先把配置统一从 backend/.env 读取，后续迁移旧 config.py 的所有字段。
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


def _backend_env_path() -> str:
    # 当前文件：MyEmotionCompanion/backend/app/config/settings.py
    # backend 目录：MyEmotionCompanion/backend
    this_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.normpath(os.path.join(this_dir, "..", "..", ".."))
    return os.path.join(backend_dir, ".env")

def _project_env_path() -> str:
    # MyEmotionCompanion/.env（沿用你现有项目的配置文件）
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(this_dir, "..", "..", "..", ".."))
    return os.path.join(project_root, ".env")


@dataclass(frozen=True)
class Settings:
    SECRET_KEY: str
    DEBUG: bool

    # AI / 其他配置：先预留字段，后续逐步迁移
    AI_PROVIDER: str
    DEEPSEEK_API_KEY: str | None
    VOLCENGINE_API_KEY: str | None
    VOLCENGINE_MODEL: str | None
    VOLCENGINE_BASE_URL: str | None

    BAIDU_API_KEY: str | None
    BAIDU_SECRET_KEY: str | None

    # C3KG
    C3KG_DATA_PATH: str | None

    @staticmethod
    def load() -> "Settings":
        # 1) 先加载 backend/.env（如果你未来要独立部署后端，可只维护 backend/.env）
        # 2) 再加载项目根 .env（与你现有项目兼容；当 backend/.env 不存在时仍能运行）
        load_dotenv(_backend_env_path(), override=False)
        load_dotenv(_project_env_path(), override=False)

        def _get_bool(name: str, default: bool) -> bool:
            v = os.getenv(name)
            if v is None:
                return default
            return v.strip().lower() in {"1", "true", "yes", "y", "on"}

        # 默认使用项目根 data/c3kg_data.json（不依赖项目根代码，只是读数据文件）
        this_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.normpath(os.path.join(this_dir, "..", "..", "..", ".."))
        default_c3kg_path = os.path.join(project_root, "data", "c3kg_data.json")

        return Settings(
            SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            DEBUG=_get_bool("DEBUG", False),
            AI_PROVIDER=os.getenv("AI_PROVIDER", "deepseek"),
            DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY"),
            VOLCENGINE_API_KEY=os.getenv("VOLCENGINE_API_KEY"),
            VOLCENGINE_MODEL=os.getenv("VOLCENGINE_MODEL"),
            VOLCENGINE_BASE_URL=os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            BAIDU_API_KEY=os.getenv("BAIDU_API_KEY"),
            BAIDU_SECRET_KEY=os.getenv("BAIDU_SECRET_KEY"),
            C3KG_DATA_PATH=os.getenv("C3KG_DATA_PATH", default_c3kg_path),
        )


