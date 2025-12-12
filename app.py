# app.py - Flask主应用文件（集成AI服务版 + 百度情感分析 + WebSocket + 主动关怀）
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import config
from services.ai_service import get_ai_reply
from services.emotion_analyzer import BaiduEmotionAnalyzer
import sqlite3
import os

# 导入 WebSocket 和调度器模块
from websocket_handler import init_socketio, get_connection_stats, get_online_users
from scheduler import init_scheduler, get_scheduler_status, schedule_user_tasks, remove_user_tasks
from models import init_user_schedule_db, get_user_schedule, create_or_update_user_schedule

# 数据库文件（项目根目录）
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat_history.db')

# 初始化百度情感分析器（如果API Key已配置）
emotion_analyzer = None
if config.BAIDU_API_KEY and config.BAIDU_SECRET_KEY:
    emotion_analyzer = BaiduEmotionAnalyzer(config.BAIDU_API_KEY, config.BAIDU_SECRET_KEY)



def init_db():
    """初始化SQLite数据库和表"""
    conn = sqlite3.connect(DB_PATH)
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


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_message(session_id, role, content):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)',
            (session_id, role, content)
        )
        conn.commit()
    finally:
        conn.close()


def get_session_history(session_id, limit=50):
    """从数据库读取会话历史，按时间升序返回最近的 `limit` 条消息（role/content 列表）。"""
    conn = get_db_connection()
    try:
        cur = conn.execute(
            'SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC',
            (session_id,)
        )
        rows = cur.fetchall()
        history = [{'role': r['role'], 'content': r['content']} for r in rows]
        # 只保留最近 limit 条
        if len(history) > limit:
            history = history[-limit:]
        return history
    finally:
        conn.close()


def trim_history(session_id, max_items=10):
    """裁剪数据库中指定会话的历史消息，保留最近 max_items 条，其余删除。"""
    conn = get_db_connection()
    try:
        cur = conn.execute('SELECT id FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
        ids = [r['id'] for r in cur.fetchall()]
        if len(ids) > max_items:
            # 删除最旧的部分
            delete_ids = ids[0:len(ids) - max_items]
            conn.executemany('DELETE FROM messages WHERE id = ?', [(i,) for i in delete_ids])
            conn.commit()
    finally:
        conn.close()


def clear_history_db(session_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        conn.commit()
    finally:
        conn.close()

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY if hasattr(config, 'SECRET_KEY') else 'your-secret-key-here'
CORS(app)

# 初始化数据库
init_db()
init_user_schedule_db()

# 初始化 WebSocket
socketio = init_socketio(app)

# 初始化调度器（在非调试模式下或主进程中）
import sys
if '--no-scheduler' not in sys.argv:
    init_scheduler(app)

# 保留内存字典作为快速缓存（可选）
conversation_sessions = {}

# NOTE: 现在优先使用数据库持久化；get_session_history 会从数据库读取历史
def get_session_history_db(session_id):
    return get_session_history(session_id, limit=50)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test_page():
    """测试主动关怀功能的页面"""
    return render_template('test.html')

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        'status': 'success',
        'message': 'API接口工作正常！',
        'service': 'MyEmotionCompanion Backend (AI Integrated)',
        'version': '2.0.0'
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """接收用户消息，进行情感分析，并调用AI生成回复"""
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': '请提供message参数'}), 400
        
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default_user')  # 简单的会话标识
        
        # 获取该会话的历史记录（从数据库）
        history = get_session_history_db(session_id)
        
        print(f"[App] 收到消息: '{user_message[:30]}...' (会话: {session_id}, 历史长度: {len(history)})")
        
        # ========== 新增：情感分析 ==========
        emotion_data = None
        if emotion_analyzer:
            try:
                emotion_data = emotion_analyzer.analyze_emotion(user_message)
                print(f"[情感分析] 结果: {emotion_data}")
            except Exception as e:
                print(f"[情感分析] 失败: {e}")
                emotion_data = None

        # 调试信息：打印分析器对象及最终 emotion_data 值，便于追查为何未返回到前端
        try:
            print(f"[Debug] emotion_analyzer 对象: {emotion_analyzer}")
            print(f"[Debug] emotion_data 最终值: {emotion_data}")
        except Exception:
            pass
        
        # 调用AI服务，并传递情感数据作为额外上下文
        # AI 会根据用户情绪状态调整回复方式
        ai_reply = get_ai_reply(user_message, history, emotion_data=emotion_data)
        
        # 持久化到数据库（保存用户消息和AI回复）
        save_message(session_id, 'user', user_message)
        save_message(session_id, 'assistant', ai_reply)
        # 裁剪历史，保留最近5轮（10条消息）
        trim_history(session_id, max_items=10)
        # 重新读取当前历史长度以返回给客户端
        history = get_session_history_db(session_id)
        
        response_payload = {
            'reply': ai_reply,
            'status': 'success',
            'session_id': session_id,
            'history_length': len(history),
            'emotion': emotion_data,  # 返回情感分析结果给前端（可选）
            'emotion_type': type(emotion_data).__name__ if emotion_data is not None else 'NoneType'
        }
        try:
            print(f"[Debug] 返回给客户端的 payload: {response_payload}")
        except Exception:
            pass
        return jsonify(response_payload)
        
    except Exception as e:
        print(f"[App] 错误: {e}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """清空指定会话的历史记录"""
    data = request.json
    session_id = data.get('session_id', 'default_user')
    # 清理数据库中的历史
    clear_history_db(session_id)
    # 清理内存缓存（如果存在）
    if session_id in conversation_sessions:
        conversation_sessions.pop(session_id, None)

    return jsonify({
        'status': 'success',
        'message': f'已清空会话 {session_id} 的历史记录'
    })


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'ai_integrated': True}), 200


@app.route('/api/websocket/status', methods=['GET'])
def websocket_status():
    """获取 WebSocket 连接状态"""
    stats = get_connection_stats()
    return jsonify({
        'status': 'success',
        'websocket': stats
    })


@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """获取调度器状态"""
    status = get_scheduler_status()
    return jsonify({
        'status': 'success',
        'scheduler': status
    })


@app.route('/api/user/schedule', methods=['GET', 'POST'])
def user_schedule():
    """获取或设置用户的推送偏好"""
    user_id = request.args.get('user_id') or request.json.get('user_id') if request.method == 'POST' else None
    
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少 user_id'}), 400
    
    if request.method == 'GET':
        # 获取用户偏好
        schedule = get_user_schedule(user_id)
        if schedule:
            return jsonify({'status': 'success', 'schedule': schedule})
        else:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    elif request.method == 'POST':
        # 设置用户偏好
        data = request.json
        allowed_fields = ['timezone', 'enable_morning', 'morning_time', 
                         'enable_evening', 'evening_time', 'enable_care', 'care_time']
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'status': 'error', 'message': '没有有效的更新字段'}), 400
        
        # 更新数据库
        create_or_update_user_schedule(user_id, **update_data)
        
        # 重新安排定时任务
        schedule = get_user_schedule(user_id)
        if schedule:
            schedule_user_tasks(user_id, schedule)
        
        return jsonify({
            'status': 'success',
            'message': '用户偏好已更新',
            'schedule': schedule
        })


@app.route('/api/user/schedule/disable', methods=['POST'])
def disable_user_schedule():
    """禁用用户的推送功能"""
    data = request.json
    user_id = data.get('user_id')
    push_type = data.get('type', 'all')  # all, morning, evening, care
    
    if not user_id:
        return jsonify({'status': 'error', 'message': '缺少 user_id'}), 400
    
    # 禁用推送
    from models import disable_user_push
    disable_user_push(user_id, push_type)
    
    # 移除对应的定时任务
    if push_type == 'all':
        remove_user_tasks(user_id)
    else:
        from scheduler import scheduler
        try:
            scheduler.remove_job(f'{push_type}_{user_id}')
        except:
            pass
    
    return jsonify({
        'status': 'success',
        'message': f'已禁用 {push_type} 推送'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("MyEmotionCompanion 情感陪伴程序 (AI集成版 + 主动关怀)")
    print("服务器启动中...")
    print(f"API Key 已配置: {'是' if config.DEEPSEEK_API_KEY else '否（请检查）'}")
    print("访问地址: http://127.0.0.1:5000")
    print("WebSocket 地址: ws://127.0.0.1:5000")
    print("=" * 60)
    
    # 使用 socketio.run 而不是 app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
