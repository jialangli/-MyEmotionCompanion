"""
backend/app/routes - 路由层
"""

from flask import Flask

from .chat import bp as chat_bp
from .persona import bp as persona_bp
from .user import bp as user_bp
from .system import bp as system_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(chat_bp)
    app.register_blueprint(persona_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(system_bp, url_prefix="/api")


