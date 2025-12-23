"""
user_memory.py - 用户推送偏好/记忆（SQLite）

兼容旧 models.py 的 companion.db(user_schedule 表)。
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List


def _db_path() -> str:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(this_dir, "..", "..", ".."))
    return os.path.join(project_root, "companion.db")


def _get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_user_schedule_db() -> None:
    conn = _get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_schedule (
                user_id TEXT PRIMARY KEY,
                timezone TEXT DEFAULT 'Asia/Shanghai',
                enable_morning INTEGER DEFAULT 1,
                morning_time TEXT DEFAULT '08:30',
                enable_evening INTEGER DEFAULT 1,
                evening_time TEXT DEFAULT '22:00',
                enable_care INTEGER DEFAULT 1,
                care_time TEXT DEFAULT '18:00',
                last_push_date TEXT,
                last_active_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_user_schedule(user_id: str) -> Optional[Dict]:
    conn = _get_conn()
    try:
        user = conn.execute("SELECT * FROM user_schedule WHERE user_id = ?", (user_id,)).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def create_or_update_user_schedule(user_id: str, **kwargs) -> None:
    conn = _get_conn()
    try:
        existing = conn.execute("SELECT user_id FROM user_schedule WHERE user_id = ?", (user_id,)).fetchone()
        if existing:
            fields = []
            values = []
            for k, v in kwargs.items():
                fields.append(f"{k} = ?")
                values.append(v)
            if fields:
                fields.append("updated_at = ?")
                values.append(datetime.now().isoformat())
                values.append(user_id)
                query = f"UPDATE user_schedule SET {', '.join(fields)} WHERE user_id = ?"
                conn.execute(query, values)
        else:
            kwargs["user_id"] = user_id
            kwargs["created_at"] = datetime.now().isoformat()
            kwargs["updated_at"] = datetime.now().isoformat()
            columns = ", ".join(kwargs.keys())
            placeholders = ", ".join(["?"] * len(kwargs))
            query = f"INSERT INTO user_schedule ({columns}) VALUES ({placeholders})"
            conn.execute(query, list(kwargs.values()))
        conn.commit()
    finally:
        conn.close()


def disable_user_push(user_id: str, push_type: str = "all") -> None:
    conn = _get_conn()
    try:
        if push_type == "all":
            conn.execute(
                """
                UPDATE user_schedule
                SET enable_morning = 0, enable_evening = 0, enable_care = 0
                WHERE user_id = ?
                """,
                (user_id,),
            )
        else:
            conn.execute(f"UPDATE user_schedule SET enable_{push_type} = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def update_user_last_active(user_id: str) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            "UPDATE user_schedule SET last_active_time = ? WHERE user_id = ?",
            (datetime.now().isoformat(), user_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_active_users() -> List[Dict]:
    """
    获取所有启用了推送的用户列表（用于 scheduler 启动时恢复任务）
    """
    conn = _get_conn()
    try:
        users = conn.execute(
            """
            SELECT user_id, timezone,
                   enable_morning, morning_time,
                   enable_evening, evening_time,
                   enable_care, care_time
            FROM user_schedule
            WHERE enable_morning = 1 OR enable_evening = 1 OR enable_care = 1
            """
        ).fetchall()
        return [dict(u) for u in users]
    finally:
        conn.close()


