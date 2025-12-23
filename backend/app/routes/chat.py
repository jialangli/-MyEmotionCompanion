"""
chat.py - 聊天相关路由

已迁移接口：
- GET  /            首页
- GET  /test        测试页
- GET  /health      健康检查（backend 工厂服务标识）
- POST /api/chat    聊天接口（与旧 app.py 保持返回结构兼容）
"""

from flask import Blueprint, jsonify, render_template, request

bp = Blueprint("chat", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/test")
def test_page():
    return render_template("test.html")


@bp.get("/health")
def health():
    return jsonify({"status": "healthy", "backend_factory": True})


@bp.post("/api/chat")
def api_chat():
    """
    兼容旧接口：POST /api/chat
    请求体: {message, session_id, persona_id}
    响应: {status, reply, emotion, session_id, history_length}
    """
    from ..utils.request_utils import get_json_required
    from ..models.chat_record import init_db, get_session_history, save_message, trim_history
    from ..services.emotion_service import analyze_emotion
    from ..services.llm_service import get_reply
    from .persona import get_persona_prompt

    try:
        data = get_json_required(request)
        if "message" not in data:
            return jsonify({"error": "请提供message参数"}), 400

        user_message = data.get("message", "")
        session_id = data.get("session_id", "default_user")
        persona_id = data.get("persona_id", "warm_partner")

        init_db()
        history = get_session_history(session_id)

        emotion_data = analyze_emotion(user_message)
        system_prompt = get_persona_prompt(persona_id)

        ai_reply = get_reply(
            user_message=user_message,
            conversation_history=history,
            emotion_data=emotion_data,
            system_prompt=system_prompt,
        )

        save_message(session_id, "user", user_message)
        save_message(session_id, "assistant", ai_reply)
        trim_history(session_id, max_items=10)
        history2 = get_session_history(session_id)

        return jsonify(
            {
                "reply": ai_reply,
                "status": "success",
                "session_id": session_id,
                "history_length": len(history2),
                "emotion": emotion_data,
                "emotion_type": type(emotion_data).__name__ if emotion_data is not None else "NoneType",
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


