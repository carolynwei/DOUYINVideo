# -*- coding: utf-8 -*-
"""
用户积分与签到系统数据库管理模块
使用 SQLite 轻量级数据库实现用户资产管理
确保所有中文字符正确显示
"""

import sqlite3
from datetime import date, timedelta, datetime

DB_FILE = "app_data.db"

def init_db():
    """初始化数据库表（如果不存在则创建）"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 0,
            last_check_in_date DATE,
            consecutive_days INTEGER DEFAULT 0,
            total_check_ins INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_user(user_id):
    """获取用户信息，如果是新用户则创建（初始积分为0，需签到获得）"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    
    if not user:
        # 新用户注册，初始积分为0，必须通过签到获得积分
        # last_check_in_date 为 None 表示从未签到
        c.execute("INSERT INTO users (user_id, credits, last_check_in_date, consecutive_days, total_check_ins) VALUES (?, 0, NULL, 0, 0)", (user_id,))
        conn.commit()
        user = (user_id, 0, None, 0, 0)
        
    conn.close()
    # 返回格式: {'user_id': user[0], 'credits': user[1], ...}
    return {
        "user_id": user[0], 
        "credits": user[1], 
        "last_check_in_date": user[2], 
        "consecutive_days": user[3],
        "total_check_ins": user[4] if len(user) > 4 else 0
    }

def check_in(user_id):
    """处理每日打卡签到逻辑 - 增强版积分系统"""
    user = get_or_create_user(user_id)
    today = date.today()
    last_check_in = date.fromisoformat(user["last_check_in_date"]) if user["last_check_in_date"] else None
    
    if last_check_in == today:
        return False, "今日已签到！", 0, user["consecutive_days"], user["credits"]

    # 计算连续签到
    if last_check_in == today - timedelta(days=1):
        new_consecutive = user["consecutive_days"] + 1
    else:
        new_consecutive = 1  # 断签了，重新计算

    # ========== 增强版积分规则 ==========
    # 基础奖励：5分
    base_reward = 5
    
    # 连续签到加成：每连续1天额外+1分，封顶+10分（即连续11天达到最大加成）
    consecutive_bonus = min(new_consecutive - 1, 10)
    
    # 里程碑奖励：
    # - 第3天：额外+3分
    # - 第7天：额外+7分  
    # - 第15天：额外+15分
    # - 第30天：额外+30分
    milestone_bonus = 0
    milestone_msg = ""
    if new_consecutive == 3:
        milestone_bonus = 3
        milestone_msg = "🎯 达成3天里程碑！额外奖励3积分！"
    elif new_consecutive == 7:
        milestone_bonus = 7
        milestone_msg = "🎯 达成7天里程碑！额外奖励7积分！"
    elif new_consecutive == 15:
        milestone_bonus = 15
        milestone_msg = "🎯 达成15天里程碑！额外奖励15积分！"
    elif new_consecutive == 30:
        milestone_bonus = 30
        milestone_msg = "🏆 达成30天超级里程碑！额外奖励30积分！"
    
    # 首签奖励：首次签到额外+10分
    first_checkin_bonus = 0
    if user["total_check_ins"] == 0:
        first_checkin_bonus = 10
        milestone_msg = "🎉 首次签到奖励10积分！"
    
    # 计算总奖励
    total_reward = base_reward + consecutive_bonus + milestone_bonus + first_checkin_bonus
    new_credits = user["credits"] + total_reward
    new_total_check_ins = user["total_check_ins"] + 1

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 检查是否需要添加新列
    try:
        c.execute("SELECT total_check_ins FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN total_check_ins INTEGER DEFAULT 0")
    
    # 检查是否需要重命名列
    try:
        c.execute("SELECT last_check_in_date FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # 旧版本使用 last_login_date，需要迁移
        try:
            c.execute("ALTER TABLE users ADD COLUMN last_check_in_date DATE")
        except sqlite3.OperationalError:
            pass  # 列已存在
    
    c.execute("""
        UPDATE users 
        SET credits=?, last_check_in_date=?, consecutive_days=?, total_check_ins=? 
        WHERE user_id=?
    """, (new_credits, today.isoformat(), new_consecutive, new_total_check_ins, user_id))
    conn.commit()
    conn.close()
    
    # 构建返回消息
    msg_parts = [f"✅ 签到成功！"]
    if milestone_msg:
        msg_parts.append(milestone_msg)
    msg_parts.append(f"📊 连续 {new_consecutive} 天 | 本次获得 {total_reward} 积分")
    msg_parts.append(f"💰 基础{base_reward} + 连续加成{consecutive_bonus}",)
    if milestone_bonus > 0:
        msg_parts[-1] += f" + 里程碑{milestone_bonus}"
    if first_checkin_bonus > 0:
        msg_parts[-1] += f" + 首签{first_checkin_bonus}"
    msg_parts.append(f"💎 当前总积分: {new_credits}")
    
    full_msg = "\n".join(msg_parts)
    return True, full_msg, total_reward, new_consecutive, new_credits

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

# ==================== 聊天记录持久化功能 ====================

def init_chat_db():
    """初始化聊天记录表"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 建立 chat_history 表，记录是谁说的、角色是什么、内容是什么、什么时候说的
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    """保存单条聊天记录到数据库"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", 
              (user_id, role, content))
    conn.commit()
    conn.close()

def load_messages(user_id):
    """加载某个用户的所有历史聊天记录"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE user_id=? ORDER BY id ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    
    # 将查出来的数据转成 Streamlit 和大模型都能直接用的字典格式
    return [{"role": row[0], "content": row[1]} for row in rows]

def clear_messages(user_id):
    """清空某个用户的聊天记录"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# ==================== 剧本版本历史持久化功能 ====================

def init_script_versions_db():
    """初始化剧本版本历史表"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS script_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            version INTEGER,
            timestamp TEXT,
            scenes TEXT,  -- JSON格式存储
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_script_version(user_id, version, timestamp, scenes):
    """保存剧本版本到数据库"""
    import json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    scenes_json = json.dumps(scenes, ensure_ascii=False)
    c.execute(
        "INSERT INTO script_versions (user_id, version, timestamp, scenes) VALUES (?, ?, ?, ?)",
        (user_id, version, timestamp, scenes_json)
    )
    conn.commit()
    conn.close()

def load_script_versions(user_id):
    """加载用户的所有剧本版本历史"""
    import json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT version, timestamp, scenes FROM script_versions WHERE user_id=? ORDER BY version ASC",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    
    versions = []
    for row in rows:
        versions.append({
            'version': row[0],
            'timestamp': row[1],
            'scenes': json.loads(row[2])
        })
    return versions

def clear_script_versions(user_id):
    """清空用户的剧本版本历史"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM script_versions WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
