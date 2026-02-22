# -*- coding: utf-8 -*-
"""
工作流引擎 - 协调执行所有步骤
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from .base_step import BaseStep, StepResult, StepContext, StepStatus
from .step_1_topic import TopicResearchStep
from .step_2_script import ScriptGenerationStep
from .step_3_visual import VisualAssetStep
from .step_4_production import ProductionStep
from .step_5_feedback import FeedbackLoopStep


class WorkflowEngine:
    """
    工作流引擎
    负责协调执行所有工作流步骤
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化工作流引擎
        
        Args:
            config: 全局配置
        """
        self.config = config or {}
        self.steps: List[BaseStep] = []
        self.context = StepContext(config=self.config)
        self.on_step_complete: Optional[Callable] = None
        self.on_step_error: Optional[Callable] = None
        
        # 注册默认步骤
        self._register_default_steps()
    
    def _register_default_steps(self):
        """注册默认的5个工作流步骤"""
        self.steps = [
            TopicResearchStep(self.config),
            ScriptGenerationStep(self.config),
            VisualAssetStep(self.config),
            ProductionStep(self.config),
            FeedbackLoopStep(self.config)
        ]
    
    def register_step(self, step: BaseStep, position: int = None):
        """
        注册自定义步骤
        
        Args:
            step: 步骤实例
            position: 插入位置，None表示追加到末尾
        """
        if position is None:
            self.steps.append(step)
        else:
            self.steps.insert(position, step)
    
    def set_callbacks(self, 
                      on_step_complete: Callable = None,
                      on_step_error: Callable = None):
        """
        设置回调函数
        
        Args:
            on_step_complete: 步骤完成回调 (step, result) -> None
            on_step_error: 步骤错误回调 (step, error) -> None
        """
        self.on_step_complete = on_step_complete
        self.on_step_error = on_step_error
    
    async def run(self, 
                  topic: str = None,
                  style_id: str = "cognitive_reshaper",
                  voice_id: str = "zh-CN-YunxiNeural",
                  user_id: str = "") -> StepContext:
        """
        运行完整工作流
        
        Args:
            topic: 主题（可选，如不提供则自动选题）
            style_id: 风格ID
            voice_id: 音色ID
            user_id: 用户ID
        
        Returns:
            StepContext: 包含所有执行结果的上下文
        """
        # 初始化上下文
        self.context.topic = topic or ""
        self.context.style_id = style_id
        self.context.voice_id = voice_id
        self.context.user_id = user_id
        
        print(f"🚀 启动工作流: {style_id}")
        print(f"📋 步骤数: {len(self.steps)}")
        
        # 顺序执行每个步骤
        for i, step in enumerate(self.steps, 1):
            print(f"\n{'='*50}")
            print(f"步骤 {i}/{len(self.steps)}: {step}")
            print(f"{'='*50}")
            
            # 执行步骤
            result = await step.run(self.context)
            
            # 回调通知
            if result.success and self.on_step_complete:
                self.on_step_complete(step, result)
            elif not result.success and self.on_step_error:
                self.on_step_error(step, result)
            
            # 如果步骤失败，决定是否继续
            if not result.success:
                print(f"❌ 步骤失败: {result.message}")
                if result.error:
                    print(f"错误: {result.error}")
                
                # 可以选择中断或继续
                # 这里选择中断
                break
            else:
                print(f"✅ {result.message}")
                if result.data:
                    print(f"数据: {result.data}")
        
        return self.context
    
    async def run_step(self, step_id: str) -> Optional[StepResult]:
        """
        运行指定步骤
        
        Args:
            step_id: 步骤ID
        
        Returns:
            StepResult: 执行结果
        """
        for step in self.steps:
            if step.step_id == step_id:
                return await step.run(self.context)
        
        print(f"❌ 未找到步骤: {step_id}")
        return None
    
    def get_step_status(self) -> List[Dict]:
        """获取所有步骤状态"""
        return [step.get_progress_info() for step in self.steps]
    
    def get_overall_progress(self) -> float:
        """获取整体进度（0-100）"""
        if not self.steps:
            return 0.0
        
        completed = sum(1 for step in self.steps if step.is_completed())
        return (completed / len(self.steps)) * 100
    
    def reset(self):
        """重置工作流"""
        self.context = StepContext(config=self.config)
        for step in self.steps:
            step.reset()
    
    def get_workflow_report(self) -> Dict[str, Any]:
        """生成工作流执行报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(self.steps),
            "completed_steps": sum(1 for s in self.steps if s.is_success()),
            "failed_steps": sum(1 for s in self.steps if s.get_status() == StepStatus.FAILED),
            "overall_progress": self.get_overall_progress(),
            "steps": self.get_step_status(),
            "final_context": {
                "topic": self.context.selected_topic,
                "video": self.context.final_video,
                "scenes_count": len(self.context.scenes)
            }
        }


class WorkflowBuilder:
    """
    工作流构建器
    用于链式构建自定义工作流
    """
    
    def __init__(self):
        self.steps: List[BaseStep] = []
        self.config: Dict[str, Any] = {}
    
    def with_config(self, config: Dict[str, Any]) -> 'WorkflowBuilder':
        """设置配置"""
        self.config = config
        return self
    
    def add_step(self, step: BaseStep) -> 'WorkflowBuilder':
        """添加步骤"""
        self.steps.append(step)
        return self
    
    def add_topic_research(self) -> 'WorkflowBuilder':
        """添加选题步骤"""
        self.steps.append(TopicResearchStep(self.config))
        return self
    
    def add_script_generation(self) -> 'WorkflowBuilder':
        """添加脚本步骤"""
        self.steps.append(ScriptGenerationStep(self.config))
        return self
    
    def add_visual_asset(self) -> 'WorkflowBuilder':
        """添加视觉步骤"""
        self.steps.append(VisualAssetStep(self.config))
        return self
    
    def add_production(self) -> 'WorkflowBuilder':
        """添加合成步骤"""
        self.steps.append(ProductionStep(self.config))
        return self
    
    def add_feedback(self) -> 'WorkflowBuilder':
        """添加反馈步骤"""
        self.steps.append(FeedbackLoopStep(self.config))
        return self
    
    def build(self) -> WorkflowEngine:
        """构建工作流引擎"""
        engine = WorkflowEngine(self.config)
        engine.steps = self.steps
        return engine
