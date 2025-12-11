# app.py - Flask主应用文件（集成AI服务版）
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import config
from services.ai_service import get_ai_reply
import sqlite3
import os

# 数据库文件（项目根目录）
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat_history.db')


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
CORS(app)

# 初始化数据库
init_db()

# 保留内存字典作为快速缓存（可选）
conversation_sessions = {}

# NOTE: 现在优先使用数据库持久化；get_session_history 会从数据库读取历史
def get_session_history_db(session_id):
    return get_session_history(session_id, limit=50)

@app.route('/')
def home():
    return render_template('index.html')

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
    """接收用户消息并调用真正的AI回复"""
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': '请提供message参数'}), 400
        
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default_user')  # 简单的会话标识
        
        # 获取该会话的历史记录（从数据库）
        history = get_session_history_db(session_id)
        
        print(f"[App] 收到消息: '{user_message[:30]}...' (会话: {session_id}, 历史长度: {len(history)})")
        
        # 调用真正的AI服务！
        ai_reply = get_ai_reply(user_message, history)
        
        # 持久化到数据库（保存用户消息和AI回复）
        save_message(session_id, 'user', user_message)
        save_message(session_id, 'assistant', ai_reply)
        # 裁剪历史，保留最近5轮（10条消息）
        trim_history(session_id, max_items=10)
        # 重新读取当前历史长度以返回给客户端
        history = get_session_history_db(session_id)
        
        return jsonify({
            'reply': ai_reply,
            'status': 'success',
            'session_id': session_id,
            'history_length': len(history)
        })
        
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

if __name__ == '__main__':
    print("=" * 60)
    print("MyEmotionCompanion 情感陪伴程序 (AI集成版)")
    print("服务器启动中...")
    print(f"API Key 已配置: {'是' if config.DEEPSEEK_API_KEY else '否（请检查）'}")
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
