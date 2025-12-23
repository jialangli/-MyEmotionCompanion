"""
socketio_service.py - Socket.IO 服务（让前端 wsStatus 正常、并支持 care_message 推送）

说明：
- 先实现前端所需的最小集：connect/disconnect + register(user_id) + room 推送
- 后续再把 scheduler 的主动关怀推送迁移进来复用 push_to_user()
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room


socketio = SocketIO(cors_allowed_origins="*", async_mode="threading", logger=False, engineio_logger=False)

# {user_id: [sid, ...]}
user_connections: Dict[str, List[str]] = {}


def init_socketio(app) -> SocketIO:
    socketio.init_app(app)
    _register_handlers()
    return socketio


def _register_handlers() -> None:
    @socketio.on("connect")
    def _connect():
        emit("connected", {"message": "连接成功", "sid": request.sid})

    @socketio.on("disconnect")
    def _disconnect():
        for user_id, sids in list(user_connections.items()):
            if request.sid in sids:
                sids.remove(request.sid)
                if not sids:
                    del user_connections[user_id]
                break

    @socketio.on("register")
    def _register(data):
        user_id = (data or {}).get("user_id")
        if not user_id:
            emit("error", {"message": "缺少 user_id"})
            return

        join_room(user_id)
        user_connections.setdefault(user_id, [])
        if request.sid not in user_connections[user_id]:
            user_connections[user_id].append(request.sid)

        emit(
            "registered",
            {"message": f"用户 {user_id} 注册成功", "user_id": user_id, "timestamp": datetime.now().isoformat()},
        )

    @socketio.on("unregister")
    def _unregister(data):
        user_id = (data or {}).get("user_id")
        if not user_id:
            return
        leave_room(user_id)
        if user_id in user_connections and request.sid in user_connections[user_id]:
            user_connections[user_id].remove(request.sid)
            if not user_connections[user_id]:
                del user_connections[user_id]
        emit("unregistered", {"message": f"用户 {user_id} 取消注册成功"})


def push_to_user(user_id: str, payload: dict) -> bool:
    """
    向指定用户房间推送 care_message
    """
    try:
        socketio.emit("care_message", payload, room=user_id)
        return True
    except Exception:
        return False


def get_connection_stats() -> dict:
    total_connections = sum(len(sids) for sids in user_connections.values())
    return {
        "online_users": len(user_connections),
        "total_connections": total_connections,
        "users": [{"user_id": uid, "connections": len(sids)} for uid, sids in user_connections.items()],
    }


