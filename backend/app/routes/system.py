"""
system.py - 系统状态相关路由
提供：
- /api/websocket/status
- /api/scheduler/status
"""

from flask import Blueprint, jsonify

from ..services.socketio_service import get_connection_stats
from ..services.scheduler_service import get_scheduler_status


bp = Blueprint("system", __name__)


@bp.get("/websocket/status")
def websocket_status():
    return jsonify({"status": "success", "websocket": get_connection_stats()})


@bp.get("/scheduler/status")
def scheduler_status():
    return jsonify({"status": "success", "scheduler": get_scheduler_status()})


