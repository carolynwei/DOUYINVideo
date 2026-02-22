# -*- coding: utf-8 -*-
"""
用户服务 - 面向对象架构
整合用户、积分、签到等业务逻辑
"""

from typing import Optional, Dict, Any, List
from models import User, UserManager, CreditsManager, CreditTransaction, TransactionType
from core import ConfigManager


class UserService:
    """
    用户服务
    整合用户管理、积分管理、签到等业务
    """
    
    def __init__(self, db_path: str = "app_data.db"):
        self._user_manager = UserManager(db_path=db_path)
        self._credits_manager = CreditsManager(db_path=db_path)
        self._config = ConfigManager().get_config()
    
    # ========== 用户管理 ==========
    
    def get_or_create_user(self, user_id: str) -> User:
        """获取或创建用户"""
        return self._user_manager.get_or_create(user_id)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        try:
            return self._user_manager.get_or_create(user_id)
        except Exception:
            return None
    
    def save_user(self, user: User):
        """保存用户数据"""
        self._user_manager.save(user)
    
    # ========== 签到功能 ==========
    
    def check_in(self, user_id: str) -> Dict[str, Any]:
        """
        用户签到
        
        Returns:
            {
                'success': bool,
                'message': str,
                'bonus': int,
                'user': User,
                'record': CheckInRecord
            }
        """
        user = self.get_or_create_user(user_id)
        
        success, message, bonus, record = user.check_in()
        
        if success:
            # 保存用户数据
            self.save_user(user)
            
            # 记录积分交易
            transaction = CreditTransaction(
                user_id=user_id,
                amount=bonus,
                transaction_type=TransactionType.CHECK_IN,
                description=message,
                balance_after=user.credits
            )
            self._credits_manager.record_transaction(transaction)
            
            # 里程碑奖励额外记录
            if record and record.is_milestone:
                milestone_transaction = CreditTransaction(
                    user_id=user_id,
                    amount=0,  # 已包含在总奖励中
                    transaction_type=TransactionType.MILESTONE_BONUS,
                    description=f"连续签到{record.consecutive_days}天里程碑",
                    balance_after=user.credits
                )
                self._credits_manager.record_transaction(milestone_transaction)
        
        return {
            'success': success,
            'message': message,
            'bonus': bonus,
            'user': user,
            'record': record
        }
    
    def can_check_in(self, user_id: str) -> bool:
        """检查是否可以签到"""
        user = self.get_or_create_user(user_id)
        return user.can_check_in_today
    
    # ========== 积分管理 ==========
    
    def deduct_credits(self, user_id: str, amount: int, operation: str) -> Dict[str, Any]:
        """
        扣除积分
        
        Returns:
            {
                'success': bool,
                'message': str,
                'user': User
            }
        """
        user = self.get_or_create_user(user_id)
        
        if user.credits < amount:
            return {
                'success': False,
                'message': f"积分不足，需要 {amount} 积分，当前 {user.credits} 积分",
                'user': user
            }
        
        # 扣除积分
        user.deduct_credits(amount)
        self.save_user(user)
        
        # 记录交易
        transaction_type = self._get_transaction_type(operation)
        transaction = CreditTransaction(
            user_id=user_id,
            amount=-amount,
            transaction_type=transaction_type,
            description=f"{operation} 消耗",
            balance_after=user.credits
        )
        self._credits_manager.record_transaction(transaction)
        
        return {
            'success': True,
            'message': f"成功扣除 {amount} 积分",
            'user': user
        }
    
    def add_credits(self, user_id: str, amount: int, reason: str = "管理员添加") -> User:
        """增加积分（管理员用）"""
        user = self.get_or_create_user(user_id)
        user.add_credits(amount)
        self.save_user(user)
        
        # 记录交易
        transaction = CreditTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=TransactionType.ADMIN_ADD,
            description=reason,
            balance_after=user.credits
        )
        self._credits_manager.record_transaction(transaction)
        
        return user
    
    def get_credit_transactions(self, user_id: str, limit: int = 50) -> List[CreditTransaction]:
        """获取积分交易记录"""
        return self._credits_manager.get_user_transactions(user_id, limit)
    
    def get_credit_stats(self, user_id: str) -> Dict[str, Any]:
        """获取积分统计"""
        return self._credits_manager.get_transaction_stats(user_id)
    
    def get_operation_cost(self, operation: str) -> int:
        """获取操作成本"""
        return self._credits_manager.get_cost_for_operation(operation)
    
    # ========== 排行榜 ==========
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取积分排行榜"""
        return self._user_manager.get_leaderboard(limit)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        return self._user_manager.get_stats()
    
    # ========== 辅助方法 ==========
    
    def _get_transaction_type(self, operation: str) -> TransactionType:
        """根据操作类型获取交易类型"""
        mapping = {
            'video_generation': TransactionType.VIDEO_GENERATION,
            'script_generation': TransactionType.SCRIPT_GENERATION,
            'image_generation': TransactionType.VIDEO_GENERATION,
            'voice_generation': TransactionType.VIDEO_GENERATION
        }
        return mapping.get(operation, TransactionType.VIDEO_GENERATION)
