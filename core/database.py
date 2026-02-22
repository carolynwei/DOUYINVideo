# -*- coding: utf-8 -*-
"""
数据库模块 - 面向对象的数据访问层
"""

import sqlite3
from datetime import date, timedelta, datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class User:
    """用户数据类"""
    user_id: str
    credits: int = 0
    last_check_in_date: Optional[str] = None
    consecutive_days: int = 0
    total_check_ins: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'credits': self.credits,
            'last_check_in_date': self.last_check_in_date,
            'consecutive_days': self.consecutive_days,
            'total_check_ins': self.total_check_ins
        }


class Database:
    """
    数据库管理类
    使用单例模式管理数据库连接
    """
    
    _instance = None
    
    def __new__(cls, db_file: str = "app_data.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db_file = db_file
            cls._instance._initialized = False
        return cls._instance
    
    def init(self):
        """初始化数据库表"""
        if self._initialized:
            return
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    credits INTEGER DEFAULT 0,
                    last_check_in_date DATE,
                    consecutive_days INTEGER DEFAULT 0,
                    total_check_ins INTEGER DEFAULT 0
                )
            ''')
            
            # 剧本版本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS script_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    version_name TEXT,
                    scenes_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 聊天记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    request TEXT,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            self._initialized = True
    
    def _get_connection(self):
        """获取数据库连接（上下文管理器）"""
        return sqlite3.connect(self._db_file)
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行SQL语句"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """查询单条记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        """查询所有记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()


class UserRepository:
    """
    用户数据仓库
    封装所有用户相关的数据库操作
    """
    
    def __init__(self, database: Database = None):
        self._db = database or Database()
    
    def get_or_create(self, user_id: str) -> User:
        """获取或创建用户"""
        user_data = self._db.fetch_one(
            "SELECT * FROM users WHERE user_id=?", (user_id,)
        )
        
        if user_data:
            return User(
                user_id=user_data[0],
                credits=user_data[1],
                last_check_in_date=user_data[2],
                consecutive_days=user_data[3],
                total_check_ins=user_data[4]
            )
        else:
            # 创建新用户
            self._db.execute(
                "INSERT INTO users (user_id, credits) VALUES (?, 0)",
                (user_id,)
            )
            return User(user_id=user_id)
    
    def update_credits(self, user_id: str, credits: int):
        """更新用户积分"""
        self._db.execute(
            "UPDATE users SET credits=? WHERE user_id=?",
            (credits, user_id)
        )
    
    def check_in(self, user_id: str) -> tuple:
        """
        用户签到
        
        Returns:
            (success: bool, message: str, bonus: int)
        """
        user = self.get_or_create(user_id)
        today = date.today()
        
        # 检查今天是否已签到
        if user.last_check_in_date:
            last_date = datetime.strptime(user.last_check_in_date, "%Y-%m-%d").date()
            if last_date == today:
                return False, "今天已经签到过了", 0
            
            # 计算连续签到
            if last_date == today - timedelta(days=1):
                consecutive = user.consecutive_days + 1
            else:
                consecutive = 1
        else:
            consecutive = 1
        
        # 计算奖励
        base_reward = 5
        consecutive_bonus = min(consecutive - 1, 10)  # 连续签到额外奖励，封顶10
        milestone_bonus = 0
        
        # 里程碑奖励
        if consecutive in [3, 7, 15, 30]:
            milestone_bonus = consecutive
        
        # 首次签到额外奖励
        first_time_bonus = 10 if user.total_check_ins == 0 else 0
        
        total_bonus = base_reward + consecutive_bonus + milestone_bonus + first_time_bonus
        new_credits = user.credits + total_bonus
        
        # 更新数据库
        self._db.execute(
            """UPDATE users SET 
                credits=?, 
                last_check_in_date=?, 
                consecutive_days=?, 
                total_check_ins=total_check_ins+1 
                WHERE user_id=?""",
            (new_credits, today.isoformat(), consecutive, user_id)
        )
        
        message = f"签到成功！获得 {total_bonus} 积分"
        if consecutive > 1:
            message += f" (连续{consecutive}天 +{consecutive_bonus})"
        if milestone_bonus > 0:
            message += f" (里程碑奖励 +{milestone_bonus})"
        
        return True, message, total_bonus
    
    def deduct_credits(self, user_id: str, amount: int) -> bool:
        """扣除积分"""
        user = self.get_or_create(user_id)
        if user.credits < amount:
            return False
        
        new_credits = user.credits - amount
        self.update_credits(user_id, new_credits)
        return True
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取积分排行榜"""
        rows = self._db.fetch_all(
            "SELECT user_id, credits, total_check_ins FROM users ORDER BY credits DESC LIMIT ?",
            (limit,)
        )
        return [
            {
                'user_id': row[0],
                'credits': row[1],
                'total_check_ins': row[2]
            }
            for row in rows
        ]
