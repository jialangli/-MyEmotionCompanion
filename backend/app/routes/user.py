"""
user.py - 用户相关路由（占位）

第 2 步迁移：把旧接口 /api/user/schedule 等迁移到这里。
"""

from flask import Blueprint, jsonify, request

bp = Blueprint("user", __name__)


@bp.route("/user/schedule", methods=["GET", "POST"])
def user_schedule():
    """
    兼容旧接口：GET/POST /api/user/schedule
    """
    from ..models.user_memory import init_user_schedule_db, get_user_schedule, create_or_update_user_schedule

    init_user_schedule_db()

    user_id = None
    if request.method == "GET":
        user_id = request.args.get("user_id")
    else:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "缺少 user_id"}), 400

    if request.method == "GET":
        schedule = get_user_schedule(user_id)
        if schedule:
            return jsonify({"status": "success", "schedule": schedule})
        return jsonify({"status": "error", "message": "用户不存在"}), 404

    # POST：更新偏好
    data = request.get_json(silent=True) or {}
    allowed_fields = [
        "timezone",
        "enable_morning",
        "morning_time",
        "enable_evening",
        "evening_time",
        "enable_care",
        "care_time",
    ]
    update_data = {k: data.get(k) for k in allowed_fields if k in data}
    if not update_data:
        return jsonify({"status": "error", "message": "没有有效的更新字段"}), 400

    create_or_update_user_schedule(user_id, **update_data)
    schedule = get_user_schedule(user_id)
    return jsonify({"status": "success", "message": "用户偏好已更新", "schedule": schedule})


@bp.post("/user/schedule/disable")
def disable_user_schedule():
    """
    兼容旧接口：POST /api/user/schedule/disable
    """
    from ..models.user_memory import init_user_schedule_db, disable_user_push

    init_user_schedule_db()
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    push_type = data.get("type", "all")

    if not user_id:
        return jsonify({"status": "error", "message": "缺少 user_id"}), 400

    disable_user_push(user_id, push_type)
    return jsonify({"status": "success", "message": f"已禁用 {push_type} 推送"})


