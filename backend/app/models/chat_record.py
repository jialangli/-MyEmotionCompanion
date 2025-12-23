"""
chat_record.py - 聊天记录模型（SQLite）

兼容旧 app.py 的 chat_history.db 表结构：messages(session_id, role, content, created_at)
"""

from __future__ import annotations

import os
import sqlite3
from typing import List, Dict


def _db_path() -> str:
    # 使用项目根的 chat_history.db（沿用旧实现）
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(this_dir, "..", "..", ".."))
    return os.path.join(project_root, "chat_history.db")


def init_db() -> None:
    conn = sqlite3.connect(_db_path())
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def save_message(session_id: str, role: str, content: str) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )
        conn.commit()
    finally:
        conn.close()


def get_session_history(session_id: str, limit: int = 50) -> List[Dict[str, str]]:
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        )
        rows = cur.fetchall()
        history = [{"role": r["role"], "content": r["content"]} for r in rows]
        if len(history) > limit:
            history = history[-limit:]
        return history
    finally:
        conn.close()


def trim_history(session_id: str, max_items: int = 10) -> None:
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT id FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        ids = [r["id"] for r in cur.fetchall()]
        if len(ids) > max_items:
            delete_ids = ids[0 : len(ids) - max_items]
            conn.executemany("DELETE FROM messages WHERE id = ?", [(i,) for i in delete_ids])
            conn.commit()
    finally:
        conn.close()


def clear_history(session_id: str) -> None:
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()


