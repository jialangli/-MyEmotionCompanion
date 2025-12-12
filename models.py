# models.py - 数据库模型和初始化

import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'companion.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_user_schedule_db():
    """初始化用户推送偏好数据库表"""
    conn = get_db_connection()
    try:
        conn.execute('''
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
        ''')
        conn.commit()
        print("[数据库] user_schedule 表已初始化")
    except Exception as e:
        print(f"[数据库] 初始化失败: {e}")
    finally:
        conn.close()


def get_user_schedule(user_id):
    """获取用户的推送偏好设置"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            'SELECT * FROM user_schedule WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def create_or_update_user_schedule(user_id, **kwargs):
    """创建或更新用户的推送偏好"""
    conn = get_db_connection()
    try:
        existing = conn.execute(
            'SELECT user_id FROM user_schedule WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if existing:
            # 更新现有记录
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key} = ?")
                values.append(value)
            
            if fields:
                fields.append("updated_at = ?")
                values.append(datetime.now().isoformat())
                values.append(user_id)
                
                query = f"UPDATE user_schedule SET {', '.join(fields)} WHERE user_id = ?"
                conn.execute(query, values)
        else:
            # 创建新记录
            kwargs['user_id'] = user_id
            kwargs['created_at'] = datetime.now().isoformat()
            kwargs['updated_at'] = datetime.now().isoformat()
            
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?'] * len(kwargs))
            query = f"INSERT INTO user_schedule ({columns}) VALUES ({placeholders})"
            conn.execute(query, list(kwargs.values()))
        
        conn.commit()
        print(f"[数据库] 用户 {user_id} 的推送偏好已保存")
    except Exception as e:
        print(f"[数据库] 保存用户偏好失败: {e}")
    finally:
        conn.close()


def update_user_last_active(user_id):
    """更新用户最后活跃时间"""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE user_schedule SET last_active_time = ? WHERE user_id = ?',
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
    except Exception as e:
        print(f"[数据库] 更新用户活跃时间失败: {e}")
    finally:
        conn.close()


def get_all_active_users():
    """获取所有启用了推送的用户列表"""
    conn = get_db_connection()
    try:
        users = conn.execute('''
            SELECT user_id, timezone, 
                   enable_morning, morning_time,
                   enable_evening, evening_time,
                   enable_care, care_time
            FROM user_schedule
            WHERE enable_morning = 1 OR enable_evening = 1 OR enable_care = 1
        ''').fetchall()
        return [dict(user) for user in users]
    finally:
        conn.close()


def disable_user_push(user_id, push_type='all'):
    """禁用用户的推送功能"""
    conn = get_db_connection()
    try:
        if push_type == 'all':
            conn.execute('''
                UPDATE user_schedule 
                SET enable_morning = 0, enable_evening = 0, enable_care = 0
                WHERE user_id = ?
            ''', (user_id,))
        else:
            conn.execute(
                f'UPDATE user_schedule SET enable_{push_type} = 0 WHERE user_id = ?',
                (user_id,)
            )
        conn.commit()
        print(f"[数据库] 用户 {user_id} 的 {push_type} 推送已禁用")
    except Exception as e:
        print(f"[数据库] 禁用推送失败: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    # 初始化数据库（测试用）
    init_user_schedule_db()
    
    # 创建测试用户
    create_or_update_user_schedule(
        'user_test_123',
        timezone='Asia/Shanghai',
        enable_morning=1,
        morning_time='08:30',
        enable_care=1,
        care_time='18:00'
    )
    
    # 查询测试
    user = get_user_schedule('user_test_123')
    print(f"测试用户配置: {user}")
    
    # 获取所有活跃用户
    active_users = get_all_active_users()
    print(f"活跃用户数: {len(active_users)}")
