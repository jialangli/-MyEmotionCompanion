"""
persona.py - 人格相关路由（占位）

第 2 步迁移：把旧接口 /api/personas 等迁移到这里。
"""

import json
import os
from flask import Blueprint, jsonify

bp = Blueprint("persona", __name__)

_cached_config = None


def _config_path() -> str:
    # backend/app/routes -> backend/app -> backend
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(this_dir, "..", "config", "persona_config.json"))


def _load_config() -> dict:
    global _cached_config
    if _cached_config is not None:
        return _cached_config
    with open(_config_path(), "r", encoding="utf-8") as f:
        _cached_config = json.load(f)
    return _cached_config


def get_persona_prompt(persona_id: str) -> str:
    cfg = _load_config()
    personas = cfg.get("personas", {})
    default_id = cfg.get("default_persona", "warm_partner")
    persona = personas.get(persona_id) or personas.get(default_id) or {}
    return persona.get("prompt", "")


@bp.get("/personas")
def personas():
    try:
        cfg = _load_config()
        personas_cfg = cfg.get("personas", {})
        personas_list = [
            {"id": pid, "name": info.get("name", pid), "emoji": info.get("emoji", "")}
            for pid, info in personas_cfg.items()
        ]
        return jsonify({"status": "success", "personas": personas_list})
    except Exception:
        return jsonify({"status": "error", "message": "获取人格列表失败"}), 500


