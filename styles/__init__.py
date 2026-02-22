# -*- coding: utf-8 -*-
"""
VideoTaxi 风格系统 - 面向对象架构
支持5大爆款风格，每个风格独立为类
"""

from .base_style import BaseStyle
from .style_cognitive import CognitiveReshaperStyle
from .style_observer import HealingObserverStyle
from .style_growth import GrowthWitnessStyle
from .style_emotion import EmotionalRollercoasterStyle
from .style_meme import MemePhilosopherStyle
from .style_factory import StyleFactory
from .skill_loader import load_skill, load_video_master_prompt, get_skill_path

__all__ = [
    'BaseStyle',
    'CognitiveReshaperStyle',
    'HealingObserverStyle', 
    'GrowthWitnessStyle',
    'EmotionalRollercoasterStyle',
    'MemePhilosopherStyle',
    'StyleFactory',
    'load_skill',
    'load_video_master_prompt',
    'get_skill_path'
]
