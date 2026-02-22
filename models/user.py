# -*- coding: utf-8 -*-
"""
用户模块 - 面向对象架构
包含用户实体、签到记录、用户管理器
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import sqlite3


class UserLevel(Enum):
    """用户等级"""
    ROOKIE = "新手司机"
    DRIVER = "正式司机"
    PRO = "专业司机"
    MASTER = "老司机"


@dataclass
class CheckInRecord:
    """签到记录"""
    date: str
    consecutive_days: int
    bonus: int
    is_milestone: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date,
            'consecutive_days': self.consecutive_days,
            'bonus': self.bonus,
            'is_milestone': self.is_milestone
        }


@dataclass
class User:
    """
    用户实体类
    包含用户所有属性和行为
    """
    user_id: str
    credits: int = 0
    last_check_in_date: Optional[str] = None
    consecutive_days: int = 0
    total_check_ins: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 非持久化字段
    _check_in_history: List[CheckInRecord] = field(default_factory=list, repr=False)
    
    @property
    def level(self) -> UserLevel:
        """根据积分计算等级"""
        if self.credits >= 500:
            return UserLevel.MASTER
        elif self.credits >= 200:
            return UserLevel.PRO
        elif self.credits >= 50:
            return UserLevel.DRIVER
        return UserLevel.ROOKIE
    
    @property
    def can_check_in_today(self) -> bool:
        """检查今天是否可以签到"""
        if not self.last_check_in_date:
            return True
        last_date = datetime.strptime(self.last_check_in_date, "%Y-%m-%d").date()
        return last_date < date.today()
    
    def calculate_check_in_bonus(self) -> tuple:
        """
        计算签到奖励
        
        Returns:
            (base_reward, consecutive_bonus, milestone_bonus, first_time_bonus, total)
        """
        today = date.today()
        
        # 计算连续天数
        if self.last_check_in_date:
            last_date = datetime.strptime(self.last_check_in_date, "%Y-%m-%d").date()
            if last_date == today - timedelta(days=1):
                consecutive = self.consecutive_days + 1
            else:
                consecutive = 1
        else:
            consecutive = 1
        
        # 基础奖励
        base_reward = 5
        
        # 连续签到奖励（封顶10）
        consecutive_bonus = min(consecutive - 1, 10)
        
        # 里程碑奖励
        milestone_bonus = 0
        is_milestone = False
        if consecutive in [3, 7, 15, 30]:
            milestone_bonus = consecutive
            is_milestone = True
        
        # 首次签到奖励
        first_time_bonus = 10 if self.total_check_ins == 0 else 0
        
        total = base_reward + consecutive_bonus + milestone_bonus + first_time_bonus
        
        return base_reward, consecutive_bonus, milestone_bonus, first_time_bonus, total, consecutive, is_milestone
    
    def check_in(self) -> tuple:
        """
        执行签到
        
        Returns:
            (success: bool, message: str, bonus: int, record: CheckInRecord)
        """
        if not self.can_check_in_today:
            return False, "今天已经签到过了", 0, None
        
        base, consecutive_bonus, milestone_bonus, first_bonus, total, consecutive, is_milestone = self.calculate_check_in_bonus()
        
        # 更新用户数据
        today_str = date.today().isoformat()
        self.credits += total
        self.last_check_in_date = today_str
        self.consecutive_days = consecutive
        self.total_check_ins += 1
        
        # 创建记录
        record = CheckInRecord(
            date=today_str,
            consecutive_days=consecutive,
            bonus=total,
            is_milestone=is_milestone
        )
        self._check_in_history.append(record)
        
        # 构建消息
        message = f"签到成功！获得 {total} 积分"
        if consecutive > 1:
            message += f" (连续{consecutive}天 +{consecutive_bonus})"
        if milestone_bonus > 0:
            message += f" (里程碑奖励 +{milestone_bonus})"
        if first_bonus > 0:
            message += f" (新手礼包 +{first_bonus})"
        
        return True, message, total, record
    
    def deduct_credits(self, amount: int) -> bool:
        """扣除积分"""
        if self.credits < amount:
            return False
        self.credits -= amount
        return True
    
    def add_credits(self, amount: int):
        """增加积分"""
        self.credits += amount
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'credits': self.credits,
            'level': self.level.value,
            'consecutive_days': self.consecutive_days,
            'total_check_ins': self.total_check_ins,
            'last_check_in_date': self.last_check_in_date,
            'can_check_in': self.can_check_in_today
        }


class UserManager:
    """
    用户管理器
    负责用户的CRUD操作和数据库交互
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None, db_path: str = "app_data.db"):
        self._db_path = db_path
        self._connection = db_connection
        self._init_table()
    
    def _get_connection(self):
        """获取数据库连接"""
        if self._connection:
            return self._connection
        return sqlite3.connect(self._db_path)
    
    def _init_table(self):
        """初始化用户表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    credits INTEGER DEFAULT 0,
                    last_check_in_date DATE,
                    consecutive_days INTEGER DEFAULT 0,
                    total_check_ins INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def get_or_create(self, user_id: str) -> User:
        """获取或创建用户"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, credits, last_check_in_date, consecutive_days, total_check_ins FROM users WHERE user_id=?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return User(
                    user_id=row[0],
                    credits=row[1],
                    last_check_in_date=row[2],
                    consecutive_days=row[3],
                    total_check_ins=row[4]
                )
            else:
                # 创建新用户
                user = User(user_id=user_id)
                cursor.execute(
                    "INSERT INTO users (user_id, credits) VALUES (?, 0)",
                    (user_id,)
                )
                conn.commit()
                return user
    
    def save(self, user: User):
        """保存用户数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET
                    credits=?,
                    last_check_in_date=?,
                    consecutive_days=?,
                    total_check_ins=?
                WHERE user_id=?
            ''', (
                user.credits,
                user.last_check_in_date,
                user.consecutive_days,
                user.total_check_ins,
                user.user_id
            ))
            conn.commit()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取积分排行榜"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, credits, total_check_ins, consecutive_days
                FROM users
                ORDER BY credits DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            return [
                {
                    'rank': i + 1,
                    'user_id': row[0],
                    'credits': row[1],
                    'total_check_ins': row[2],
                    'consecutive_days': row[3]
                }
                for i, row in enumerate(rows)
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 总用户数
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # 总积分
            cursor.execute("SELECT SUM(credits) FROM users")
            total_credits = cursor.fetchone()[0] or 0
            
            # 今日签到人数
            today = date.today().isoformat()
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE last_check_in_date=?",
                (today,)
            )
            today_check_ins = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'total_credits': total_credits,
                'today_check_ins': today_check_ins
            }
