# -*- coding: utf-8 -*-
"""
VideoTaxi 工作流系统 - 面向对象架构
抖音爆款全自动工作流：5步闭环
"""

from .base_step import BaseStep, StepResult, StepContext
from .step_1_topic import TopicResearchStep
from .step_2_script import ScriptGenerationStep
from .step_3_visual import VisualAssetStep
from .step_4_production import ProductionStep
from .step_5_feedback import FeedbackLoopStep
from .workflow_engine import WorkflowEngine

__all__ = [
    'BaseStep',
    'StepResult', 
    'StepContext',
    'TopicResearchStep',
    'ScriptGenerationStep',
    'VisualAssetStep',
    'ProductionStep',
    'FeedbackLoopStep',
    'WorkflowEngine'
]
