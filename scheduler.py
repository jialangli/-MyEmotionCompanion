# scheduler.py - APScheduler 任务调度模块

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import pytz

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('scheduler')

# 创建调度器实例
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Shanghai'))


def push_care_message(user_id, message_type="care"):
    """
    主动推送关怀消息的核心函数
    
    参数:
        user_id (str): 用户ID
        message_type (str): 消息类型 (morning/evening/care)
    """
    try:
        from models import get_user_schedule, update_user_last_active
        from services.ai_service import get_ai_reply
        
        # 1. 获取用户偏好设置
        user = get_user_schedule(user_id)
        if not user:
            logger.warning(f"[主动推送] 用户 {user_id} 不存在")
            return
        
        # 检查是否启用了该类型的推送
        enable_key = f'enable_{message_type}'
        if not user.get(enable_key):
            logger.info(f"[主动推送] 用户 {user_id} 未启用 {message_type} 推送")
            return
        
        # 2. 构造系统提示词，让AI生成关怀消息
        current_time = datetime.now().strftime('%H:%M')
        
        if message_type == 'morning':
            context = "现在是早晨，请生成一条温暖的早安问候，关心对方是否休息好，鼓励对方开始美好的一天。"
        elif message_type == 'evening':
            context = "现在是晚上睡前时间，请生成一条温馨的晚安问候，关心对方今天是否辛苦，祝对方好梦。"
        elif message_type == 'care':
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
        
        # 3. 调用AI服务生成消息内容
        ai_reply = get_ai_reply(
            "请生成一条关怀消息",
            conversation_history=[{"role": "system", "content": system_prompt}]
        )
        
        # 4. 推送消息（通过WebSocket）
        from websocket_handler import push_to_user
        push_to_user(user_id, {
            'type': 'care_message',
            'message_type': message_type,
            'content': ai_reply,
            'time': datetime.now().isoformat()
        })
        
        logger.info(f"[主动推送] 已向用户 {user_id} 发送 {message_type} 消息")
        
    except Exception as e:
        logger.error(f"[主动推送] 发送失败: {e}", exc_info=True)


def schedule_user_tasks(user_id, user_config):
    """
    为单个用户安排定时任务
    
    参数:
        user_id (str): 用户ID
        user_config (dict): 用户配置信息
    """
    try:
        # 清除该用户的旧任务
        remove_user_tasks(user_id)
        
        # 早安推送
        if user_config.get('enable_morning'):
            morning_time = user_config.get('morning_time', '08:30')
            hour, minute = map(int, morning_time.split(':'))
            scheduler.add_job(
                func=push_care_message,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=[user_id, 'morning'],
                id=f'morning_{user_id}',
                replace_existing=True
            )
            logger.info(f"[调度器] 已为用户 {user_id} 添加早安任务 ({morning_time})")
        
        # 晚安推送
        if user_config.get('enable_evening'):
            evening_time = user_config.get('evening_time', '22:00')
            hour, minute = map(int, evening_time.split(':'))
            scheduler.add_job(
                func=push_care_message,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=[user_id, 'evening'],
                id=f'evening_{user_id}',
                replace_existing=True
            )
            logger.info(f"[调度器] 已为用户 {user_id} 添加晚安任务 ({evening_time})")
        
        # 关怀推送
        if user_config.get('enable_care'):
            care_time = user_config.get('care_time', '18:00')
            hour, minute = map(int, care_time.split(':'))
            scheduler.add_job(
                func=push_care_message,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=[user_id, 'care'],
                id=f'care_{user_id}',
                replace_existing=True
            )
            logger.info(f"[调度器] 已为用户 {user_id} 添加关怀任务 ({care_time})")
            
    except Exception as e:
        logger.error(f"[调度器] 为用户 {user_id} 安排任务失败: {e}", exc_info=True)


def remove_user_tasks(user_id):
    """移除用户的所有定时任务"""
    task_types = ['morning', 'evening', 'care']
    for task_type in task_types:
        job_id = f'{task_type}_{user_id}'
        try:
            scheduler.remove_job(job_id)
            logger.info(f"[调度器] 已移除任务 {job_id}")
        except Exception:
            pass  # 任务不存在时忽略


def schedule_all_users():
    """为所有启用推送的用户安排定时任务（启动时调用）"""
    try:
        from models import get_all_active_users
        
        users = get_all_active_users()
        logger.info(f"[调度器] 开始为 {len(users)} 个活跃用户安排任务")
        
        for user in users:
            schedule_user_tasks(user['user_id'], user)
        
        logger.info(f"[调度器] 所有用户任务安排完成")
        
    except Exception as e:
        logger.error(f"[调度器] 安排所有用户任务失败: {e}", exc_info=True)


def init_scheduler(app=None):
    """
    初始化调度器（在Flask应用启动时调用）
    
    参数:
        app: Flask应用实例（可选，用于应用上下文）
    """
    if scheduler.running:
        logger.warning("[调度器] 调度器已在运行中")
        return
    
    try:
        # 启动调度器
        scheduler.start()
        logger.info("[调度器] 调度器已启动")
        
        # 为所有用户安排任务
        if app:
            with app.app_context():
                schedule_all_users()
        else:
            schedule_all_users()
        
        # 注册优雅关闭
        import atexit
        atexit.register(lambda: shutdown_scheduler())
        
    except Exception as e:
        logger.error(f"[调度器] 初始化失败: {e}", exc_info=True)


def shutdown_scheduler():
    """优雅关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[调度器] 调度器已关闭")


def get_scheduler_status():
    """获取调度器状态（用于调试）"""
    if not scheduler.running:
        return {"status": "stopped", "jobs": []}
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger)
        })
    
    return {
        "status": "running",
        "jobs_count": len(jobs),
        "jobs": jobs
    }


if __name__ == '__main__':
    # 测试调度器
    from models import init_user_schedule_db, create_or_update_user_schedule
    
    # 初始化数据库
    init_user_schedule_db()
    
    # 创建测试用户
    test_user_id = 'user_test_scheduler'
    create_or_update_user_schedule(
        test_user_id,
        enable_morning=1,
        morning_time='08:30',
        enable_care=1,
        care_time='18:00'
    )
    
    # 初始化调度器
    init_scheduler()
    
    # 打印调度器状态
    status = get_scheduler_status()
    print(f"\n调度器状态: {status['status']}")
    print(f"任务数量: {status['jobs_count']}")
    print("\n任务列表:")
    for job in status['jobs']:
        print(f"  - {job['id']}: 下次运行 {job['next_run_time']}")
    
    # 保持运行以便观察
    print("\n调度器正在运行中... (按 Ctrl+C 退出)")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭调度器...")
        shutdown_scheduler()
