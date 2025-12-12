# websocket_handler.py - WebSocket 消息推送模块

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask import request
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('websocket')

# 创建 SocketIO 实例（将在 app.py 中初始化）
socketio = None

# 存储用户连接映射 {user_id: [sid1, sid2, ...]}
user_connections = {}


def init_socketio(app):
    """
    初始化 SocketIO
    
    参数:
        app: Flask 应用实例
    """
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # 允许跨域，生产环境应限制具体域名
        async_mode='threading',
        logger=True,
        engineio_logger=False
    )
    
    # 注册事件处理器
    register_handlers()
    
    logger.info("[WebSocket] SocketIO 已初始化")
    return socketio


def register_handlers():
    """注册 WebSocket 事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        logger.info(f'[WebSocket] 客户端已连接: {request.sid}')
        emit('connected', {'message': '连接成功', 'sid': request.sid})
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        logger.info(f'[WebSocket] 客户端已断开: {request.sid}')
        
        # 从用户连接映射中移除
        for user_id, sids in list(user_connections.items()):
            if request.sid in sids:
                sids.remove(request.sid)
                if not sids:
                    del user_connections[user_id]
                logger.info(f'[WebSocket] 用户 {user_id} 的连接已移除')
                break
    
    
    @socketio.on('register')
    def handle_register(data):
        """
        客户端注册用户ID事件
        
        前端需要在连接后发送: socket.emit('register', {user_id: 'xxx'})
        """
        user_id = data.get('user_id')
        if not user_id:
            emit('error', {'message': '缺少 user_id'})
            logger.warning(f'[WebSocket] 注册失败: 缺少 user_id (sid: {request.sid})')
            return
        
        # 将连接加入用户专属房间
        join_room(user_id)
        
        # 记录用户连接
        if user_id not in user_connections:
            user_connections[user_id] = []
        if request.sid not in user_connections[user_id]:
            user_connections[user_id].append(request.sid)
        
        logger.info(f'[WebSocket] 用户 {user_id} 已注册 (sid: {request.sid}, 总连接数: {len(user_connections[user_id])})')
        
        # 更新用户最后活跃时间
        try:
            from models import update_user_last_active
            update_user_last_active(user_id)
        except Exception as e:
            logger.error(f'[WebSocket] 更新用户活跃时间失败: {e}')
        
        emit('registered', {
            'message': f'用户 {user_id} 注册成功',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
    
    
    @socketio.on('unregister')
    def handle_unregister(data):
        """客户端取消注册事件"""
        user_id = data.get('user_id')
        if user_id:
            leave_room(user_id)
            
            # 从连接映射中移除
            if user_id in user_connections:
                if request.sid in user_connections[user_id]:
                    user_connections[user_id].remove(request.sid)
                if not user_connections[user_id]:
                    del user_connections[user_id]
            
            logger.info(f'[WebSocket] 用户 {user_id} 已取消注册 (sid: {request.sid})')
            emit('unregistered', {'message': f'用户 {user_id} 取消注册成功'})
    
    
    @socketio.on('ping')
    def handle_ping():
        """心跳检测"""
        emit('pong', {'timestamp': datetime.now().isoformat()})
    
    
    @socketio.on('user_typing')
    def handle_user_typing(data):
        """用户正在输入事件（可选功能）"""
        user_id = data.get('user_id')
        if user_id:
            # 可以在这里更新用户活跃时间或做其他处理
            logger.debug(f'[WebSocket] 用户 {user_id} 正在输入')


def push_to_user(user_id, data):
    """
    向特定用户推送消息
    
    参数:
        user_id (str): 用户ID
        data (dict): 要推送的数据
    """
    if not socketio:
        logger.error("[WebSocket] SocketIO 未初始化")
        return False
    
    try:
        # 向用户房间发送消息
        socketio.emit('care_message', data, room=user_id)
        logger.info(f'[WebSocket] 已向用户 {user_id} 推送消息: {data.get("message_type", "unknown")}')
        return True
    except Exception as e:
        logger.error(f'[WebSocket] 推送消息失败: {e}', exc_info=True)
        return False


def push_to_all(data, event='broadcast'):
    """
    向所有连接的客户端广播消息
    
    参数:
        data (dict): 要广播的数据
        event (str): 事件名称
    """
    if not socketio:
        logger.error("[WebSocket] SocketIO 未初始化")
        return False
    
    try:
        socketio.emit(event, data)
        logger.info(f'[WebSocket] 已广播消息到所有客户端')
        return True
    except Exception as e:
        logger.error(f'[WebSocket] 广播消息失败: {e}', exc_info=True)
        return False


def get_online_users():
    """
    获取当前在线用户列表
    
    返回:
        list: 在线用户ID列表
    """
    return list(user_connections.keys())


def get_user_connection_count(user_id):
    """
    获取用户的连接数（用户可能有多个标签页/设备）
    
    参数:
        user_id (str): 用户ID
    
    返回:
        int: 连接数
    """
    return len(user_connections.get(user_id, []))


def is_user_online(user_id):
    """
    检查用户是否在线
    
    参数:
        user_id (str): 用户ID
    
    返回:
        bool: 是否在线
    """
    return user_id in user_connections and len(user_connections[user_id]) > 0


def disconnect_user(user_id):
    """
    强制断开用户的所有连接（管理功能）
    
    参数:
        user_id (str): 用户ID
    """
    if not socketio or user_id not in user_connections:
        return False
    
    try:
        for sid in user_connections[user_id]:
            socketio.server.disconnect(sid)
        
        del user_connections[user_id]
        logger.info(f'[WebSocket] 已强制断开用户 {user_id} 的所有连接')
        return True
    except Exception as e:
        logger.error(f'[WebSocket] 断开用户连接失败: {e}', exc_info=True)
        return False


def get_connection_stats():
    """
    获取连接统计信息（用于监控）
    
    返回:
        dict: 统计信息
    """
    total_connections = sum(len(sids) for sids in user_connections.values())
    return {
        'online_users': len(user_connections),
        'total_connections': total_connections,
        'users': [
            {'user_id': uid, 'connections': len(sids)}
            for uid, sids in user_connections.items()
        ]
    }


if __name__ == '__main__':
    # 测试代码
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    # 初始化 WebSocket
    socketio = init_socketio(app)
    
    # 测试路由
    @app.route('/')
    def index():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebSocket Test</title>
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
        </head>
        <body>
            <h1>WebSocket 测试页面</h1>
            <div id="status">未连接</div>
            <button onclick="connect()">连接</button>
            <button onclick="register()">注册用户</button>
            <button onclick="disconnect()">断开</button>
            <div id="messages"></div>
            
            <script>
                let socket = null;
                const userId = 'test_user_' + Date.now();
                
                function connect() {
                    socket = io();
                    
                    socket.on('connect', () => {
                        document.getElementById('status').textContent = '已连接: ' + socket.id;
                        addMessage('系统', '已连接到服务器');
                    });
                    
                    socket.on('disconnect', () => {
                        document.getElementById('status').textContent = '已断开';
                        addMessage('系统', '已断开连接');
                    });
                    
                    socket.on('registered', (data) => {
                        addMessage('系统', '注册成功: ' + data.user_id);
                    });
                    
                    socket.on('care_message', (data) => {
                        addMessage('关怀消息', JSON.stringify(data));
                    });
                }
                
                function register() {
                    if (socket) {
                        socket.emit('register', {user_id: userId});
                    }
                }
                
                function disconnect() {
                    if (socket) {
                        socket.disconnect();
                    }
                }
                
                function addMessage(type, content) {
                    const div = document.createElement('div');
                    div.textContent = `[${new Date().toLocaleTimeString()}] ${type}: ${content}`;
                    document.getElementById('messages').appendChild(div);
                }
            </script>
        </body>
        </html>
        '''
    
    print("WebSocket 测试服务器启动在 http://localhost:5000")
    print("在浏览器中打开上述地址进行测试")
    socketio.run(app, debug=True, port=5000)
