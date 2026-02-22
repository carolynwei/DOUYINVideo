"""
用户积分与签到系统数据库管理模块
使用 SQLite 轻量级数据库实现用户资产管理
"""

import sqlite3
from datetime import date, timedelta

DB_FILE = "app_data.db"

def init_db():
    """初始化数据库表（如果不存在则创建）"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 0,
            last_login_date DATE,
            consecutive_days INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_user(user_id):
    """获取用户信息，如果是新用户则送初始积分"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    
    if not user:
        # 新用户注册，赠送 20 初始积分
        today = date.today().isoformat()
        c.execute("INSERT INTO users (user_id, credits, last_login_date, consecutive_days) VALUES (?, 20, ?, 1)", (user_id, today))
        conn.commit()
        user = (user_id, 20, today, 1)
        
    conn.close()
    # 返回格式: {'user_id': user[0], 'credits': user[1], ...}
    return {
        "user_id": user[0], 
        "credits": user[1], 
        "last_login_date": user[2], 
        "consecutive_days": user[3]
    }

def check_in(user_id):
    """处理每日打卡签到逻辑"""
    user = get_or_create_user(user_id)
    today = date.today()
    last_login = date.fromisoformat(user["last_login_date"]) if user["last_login_date"] else None
    
    if last_login == today:
        return False, "今日已签到！"

    # 计算连续签到
    if last_login == today - timedelta(days=1):
        new_consecutive = user["consecutive_days"] + 1
    else:
        new_consecutive = 1  # 断签了，重新计算

    # 签到奖励逻辑：基础 5 分，连续签到天数每多1天多给1分，封顶 15 分
    reward = min(5 + new_consecutive, 15)
    new_credits = user["credits"] + reward

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET credits=?, last_login_date=?, consecutive_days=? 
        WHERE user_id=?
    """, (new_credits, today.isoformat(), new_consecutive, user_id))
    conn.commit()
    conn.close()
    
    return True, f"签到成功！连续 {new_consecutive} 天，获得 {reward} 积分。当前总积分: {new_credits}"

def deduct_credits(user_id, cost):
    """扣除积分，返回是否成功"""
    user = get_or_create_user(user_id)
    if user["credits"] < cost:
        return False  # 积分不足

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits - ? WHERE user_id = ?", (cost, user_id))
    conn.commit()
    conn.close()
    return True

def get_user_credits(user_id):
    """获取用户当前积分"""
    user = get_or_create_user(user_id)
    return user["credits"]
