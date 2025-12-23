"""
backend/app/__init__.py - 应用工厂（Flask Factory）
"""

import os
from flask import Flask
from flask_cors import CORS

from .config.settings import Settings
from .routes import register_blueprints
from .services.socketio_service import init_socketio
from .services.scheduler_service import init_scheduler


def create_app() -> Flask:
    # 复用现有前端资源（templates/static 在项目根目录下）
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(this_dir, "..", ".."))  # MyEmotionCompanion/backend -> MyEmotionCompanion
    templates_dir = os.path.join(project_root, "templates")
    static_dir = os.path.join(project_root, "static")

    app = Flask(
        __name__,
        template_folder=templates_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )

    # 加载配置（backend/.env）
    settings = Settings.load()
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)

    # 初始化 Socket.IO（让前端在线状态/推送通道可用）
    init_socketio(app)

    # 初始化调度器（用于状态接口与主动关怀推送）
    init_scheduler()

    # 注册蓝图
    register_blueprints(app)
    return app


