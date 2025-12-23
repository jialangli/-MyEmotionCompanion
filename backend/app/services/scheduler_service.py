"""
scheduler_service.py - APScheduler 服务（工厂模式）

目标：
- 在 backend 内运行 BackgroundScheduler
- 提供 get_scheduler_status 给状态接口调用

说明：
- 主动关怀推送的完整迁移可以在下一步继续完善；本次先保证“状态接口可用 + 调度器能启动”。
"""

from __future__ import annotations

import atexit
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .llm_service import get_reply
from .socketio_service import push_to_user
from ..models.user_memory import get_all_active_users, get_user_schedule


logger = logging.getLogger("backend-scheduler")


scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Shanghai"))


def push_care_message(user_id: str, message_type: str = "care") -> None:
    """
    迁移版：生成关怀消息并通过 SocketIO 推送
    """
    try:
        user = get_user_schedule(user_id)
        if not user:
            return

        enable_key = f"enable_{message_type}"
        if not user.get(enable_key):
            return

        if message_type == "morning":
            context = "现在是早晨，请生成一条温暖的早安问候，关心对方是否休息好，鼓励对方开始美好的一天。"
        elif message_type == "evening":
            context = "现在是晚上睡前时间，请生成一条温馨的晚安问候，关心对方今天是否辛苦，祝对方好梦。"
        elif message_type == "care":
            context = "现在是傍晚下班时间，请主动关心对方今天工作是否顺利，是否累了，表达想念和关怀。"
        else:
            context = "请生成一条温暖的关怀消息。"

        system_prompt = f"""你是用户的贴心伴侣。{context}
要求：
1. 语气亲切自然、温暖体贴
2. 使用亲昵称呼（如宝宝、老公等）
3. 长度控制在50字以内
4. 适当使用表情符号
5. 这是主动发起的关怀，不要问问题等待回复，而是表达关心和爱意"""

        ai_reply = get_reply(
            user_message="请生成一条关怀消息",
            conversation_history=[{"role": "system", "content": system_prompt}],
            emotion_data=None,
            system_prompt=None,
        )

        push_to_user(
            user_id,
            {
                "type": "care_message",
                "message_type": message_type,
                "content": ai_reply,
                "time": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.error("push_care_message failed: %s", e, exc_info=True)


def remove_user_tasks(user_id: str) -> None:
    for t in ["morning", "evening", "care"]:
        job_id = f"{t}_{user_id}"
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass


def schedule_user_tasks(user_id: str, user_config: Dict[str, Any]) -> None:
    remove_user_tasks(user_id)

    if user_config.get("enable_morning"):
        t = user_config.get("morning_time", "08:30")
        hour, minute = map(int, t.split(":"))
        scheduler.add_job(
            func=push_care_message,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[user_id, "morning"],
            id=f"morning_{user_id}",
            replace_existing=True,
        )

    if user_config.get("enable_evening"):
        t = user_config.get("evening_time", "22:00")
        hour, minute = map(int, t.split(":"))
        scheduler.add_job(
            func=push_care_message,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[user_id, "evening"],
            id=f"evening_{user_id}",
            replace_existing=True,
        )

    if user_config.get("enable_care"):
        t = user_config.get("care_time", "18:00")
        hour, minute = map(int, t.split(":"))
        scheduler.add_job(
            func=push_care_message,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[user_id, "care"],
            id=f"care_{user_id}",
            replace_existing=True,
        )


def schedule_all_users() -> None:
    users = get_all_active_users()
    for u in users:
        schedule_user_tasks(u["user_id"], u)


def init_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.start()
    try:
        schedule_all_users()
    except Exception:
        # 不让启动失败
        logger.exception("schedule_all_users failed")
    atexit.register(shutdown_scheduler)


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()


def get_scheduler_status() -> Dict[str, Any]:
    if not scheduler.running:
        return {"status": "stopped", "jobs": []}

    jobs: List[Dict[str, Any]] = []
    for job in scheduler.get_jobs():
        jobs.append({"id": job.id, "next_run_time": str(job.next_run_time), "trigger": str(job.trigger)})
    return {"status": "running", "jobs_count": len(jobs), "jobs": jobs}


