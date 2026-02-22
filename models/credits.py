# -*- coding: utf-8 -*-
"""
积分模块 - 面向对象架构
包含积分交易记录、积分管理器
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import sqlite3


class TransactionType(Enum):
    """交易类型"""
    CHECK_IN = "签到奖励"
    VIDEO_GENERATION = "视频生成消耗"
    SCRIPT_GENERATION = "剧本生成消耗"
    REFUND = "退款"
    ADMIN_ADD = "管理员添加"
    MILESTONE_BONUS = "里程碑奖励"
    FIRST_TIME_BONUS = "新手礼包"


@dataclass
class CreditTransaction:
    """积分交易记录"""
    user_id: str
    amount: int  # 正数为增加，负数为扣除
    transaction_type: TransactionType
    description: str
    balance_after: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'type': self.transaction_type.value,
            'description': self.description,
            'balance_after': self.balance_after,
            'created_at': self.created_at
        }


class CreditsManager:
    """
    积分管理器
    负责积分的交易记录和查询
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
        """初始化积分交易表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    balance_after INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def record_transaction(self, transaction: CreditTransaction) -> CreditTransaction:
        """记录交易"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO credit_transactions
                (user_id, amount, transaction_type, description, balance_after)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                transaction.user_id,
                transaction.amount,
                transaction.transaction_type.value,
                transaction.description,
                transaction.balance_after
            ))
            conn.commit()
            transaction.id = cursor.lastrowid
            return transaction
    
    def get_user_transactions(self, user_id: str, limit: int = 50) -> List[CreditTransaction]:
        """获取用户的交易记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, amount, transaction_type, description, balance_after, created_at
                FROM credit_transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append(CreditTransaction(
                    id=row[0],
                    user_id=row[1],
                    amount=row[2],
                    transaction_type=TransactionType(row[3]),
                    description=row[4],
                    balance_after=row[5],
                    created_at=row[6]
                ))
            return transactions
    
    def get_transaction_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户交易统计"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 总收入
            cursor.execute('''
                SELECT SUM(amount) FROM credit_transactions
                WHERE user_id = ? AND amount > 0
            ''', (user_id,))
            total_income = cursor.fetchone()[0] or 0
            
            # 总支出
            cursor.execute('''
                SELECT SUM(ABS(amount)) FROM credit_transactions
                WHERE user_id = ? AND amount < 0
            ''', (user_id,))
            total_expense = cursor.fetchone()[0] or 0
            
            # 交易次数
            cursor.execute('''
                SELECT COUNT(*) FROM credit_transactions
                WHERE user_id = ?
            ''', (user_id,))
            transaction_count = cursor.fetchone()[0]
            
            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': total_income - total_expense,
                'transaction_count': transaction_count
            }
    
    def get_cost_for_operation(self, operation: str) -> int:
        """
        获取操作所需的积分成本
        
        Args:
            operation: 操作类型 (video_generation, script_generation, etc.)
        """
        costs = {
            'video_generation': 10,
            'script_generation': 5,
            'image_generation': 3,
            'voice_generation': 2
        }
        return costs.get(operation, 0)
