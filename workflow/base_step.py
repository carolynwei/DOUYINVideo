# -*- coding: utf-8 -*-
"""
工作流步骤基类 - 定义所有步骤的通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """步骤执行结果"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    error: Optional[str] = None
    duration: float = 0.0  # 执行耗时（秒）
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class StepContext:
    """
    工作流上下文
    在步骤之间传递数据
    """
    # 输入数据
    topic: str = ""                    # 主题
    style_id: str = ""                 # 风格ID
    voice_id: str = ""                 # 音色ID
    user_id: str = ""                  # 用户ID
    
    # 步骤1输出：选题研究
    hot_topics: List[Dict] = field(default_factory=list)
    selected_topic: str = ""
    topic_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # 步骤2输出：脚本生成
    script_data: Dict[str, Any] = field(default_factory=dict)
    scenes: List[Dict] = field(default_factory=list)
    visual_anchor: str = ""
    
    # 步骤3输出：视觉资产
    image_assets: List[str] = field(default_factory=list)
    video_assets: List[str] = field(default_factory=list)
    
    # 步骤4输出：生产合成
    audio_files: List[str] = field(default_factory=list)
    final_video: str = ""
    
    # 步骤5输出：反馈数据
    publish_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # 全局配置
    config: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, **kwargs):
        """更新上下文数据"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get(self, key: str, default=None):
        """获取上下文数据"""
        return getattr(self, key, default)


class BaseStep(ABC):
    """
    工作流步骤基类
    所有具体步骤必须继承此类
    """
    
    # 步骤标识（子类必须覆盖）
    step_id: str = ""
    step_name: str = ""
    step_emoji: str = ""
    step_description: str = ""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化步骤
        
        Args:
            config: 步骤配置
        """
        self.config = config or {}
        self.status = StepStatus.PENDING
        self.result: Optional[StepResult] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    @abstractmethod
    async def execute(self, context: StepContext) -> StepResult:
        """
        执行步骤
        
        Args:
            context: 工作流上下文
        
        Returns:
            StepResult: 执行结果
        """
        pass
    
    async def run(self, context: StepContext) -> StepResult:
        """
        运行步骤（包装方法，包含状态管理）
        
        Args:
            context: 工作流上下文
        
        Returns:
            StepResult: 执行结果
        """
        import time
        
        self.status = StepStatus.RUNNING
        self.start_time = datetime.now()
        start_ts = time.time()
        
        try:
            # 执行具体逻辑
            result = await self.execute(context)
            
            # 更新状态
            self.status = StepStatus.SUCCESS if result.success else StepStatus.FAILED
            self.result = result
            
        except Exception as e:
            self.status = StepStatus.FAILED
            result = StepResult(
                success=False,
                error=str(e),
                message=f"步骤执行异常: {e}"
            )
            self.result = result
        
        finally:
            self.end_time = datetime.now()
            if self.result:
                self.result.duration = time.time() - start_ts
        
        return self.result
    
    def get_status(self) -> StepStatus:
        """获取步骤状态"""
        return self.status
    
    def get_result(self) -> Optional[StepResult]:
        """获取执行结果"""
        return self.result
    
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.status in [StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED]
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.status == StepStatus.SUCCESS
    
    def reset(self):
        """重置步骤状态"""
        self.status = StepStatus.PENDING
        self.result = None
        self.start_time = None
        self.end_time = None
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return f"{self.step_emoji} {self.step_name}"
    
    def get_progress_info(self) -> Dict[str, Any]:
        """获取进度信息"""
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "status": self.status.value,
            "description": self.step_description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.result.duration if self.result else 0
        }
    
    def __str__(self) -> str:
        return self.get_display_name()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.step_id} [{self.status.value}]>"
