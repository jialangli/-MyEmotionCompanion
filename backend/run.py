"""
backend/run.py - 启动入口（工厂模式）

说明：
- 本阶段先保证“能启动、能访问首页/health”，后续再把旧 app.py 的全部路由迁移进来。
"""

import os

from app import create_app
from app.services.socketio_service import socketio


app = create_app()

if __name__ == "__main__":
    # 先用 Flask 内置开发服务器跑通（后续迁移 websocket 后再接入 socketio.run）
    # 默认端口改为 5001，避免与你现有的 MyEmotionCompanion/app.py(5000) 冲突
    port = int(os.getenv("PORT", "5001"))
    debug = os.getenv("DEBUG", "false").strip().lower() in {"1", "true", "yes", "y", "on"}
    socketio.run(app, host="0.0.0.0", port=port, debug=debug, allow_unsafe_werkzeug=True)


