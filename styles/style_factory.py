# -*- coding: utf-8 -*-
"""
风格工厂 - 根据风格名称创建对应风格实例
"""

from typing import Dict, Type, Optional
from .base_style import BaseStyle
from .style_cognitive import CognitiveReshaperStyle
from .style_observer import HealingObserverStyle
from .style_growth import GrowthWitnessStyle
from .style_emotion import EmotionalRollercoasterStyle
from .style_meme import MemePhilosopherStyle


class StyleFactory:
    """
    风格工厂类
    负责根据风格ID或名称创建对应风格实例
    """
    
    # 风格注册表
    _styles: Dict[str, Type[BaseStyle]] = {
        # 按ID注册
        "cognitive_reshaper": CognitiveReshaperStyle,
        "healing_observer": HealingObserverStyle,
        "growth_witness": GrowthWitnessStyle,
        "emotional_rollercoaster": EmotionalRollercoasterStyle,
        "meme_philosopher": MemePhilosopherStyle,
    }
    
    # 风格名称映射（支持emoji前缀的名称）
    _name_mapping: Dict[str, str] = {
        # 标准名称
        "认知重塑·破壁人": "cognitive_reshaper",
        "治愈系·观察者": "healing_observer",
        "逆袭见证·养成系": "growth_witness",
        "情绪过山车·发疯艺术家": "emotional_rollercoaster",
        "萌即正义·哲学大师": "meme_philosopher",
        # 带emoji的名称
        "🎭 认知重塑·破壁人": "cognitive_reshaper",
        "🎬 治愈系·观察者": "healing_observer",
        "🚀 逆袭见证·养成系": "growth_witness",
        "🤯 情绪过山车·发疯艺术家": "emotional_rollercoaster",
        "🐕 萌即正义·哲学大师": "meme_philosopher",
    }
    
    @classmethod
    def create(cls, style_id_or_name: str) -> Optional[BaseStyle]:
        """
        创建风格实例
        
        Args:
            style_id_or_name: 风格ID或名称（支持带emoji的完整名称）
        
        Returns:
            风格实例，如果找不到则返回None
        """
        # 先尝试直接作为ID查找
        if style_id_or_name in cls._styles:
            return cls._styles[style_id_or_name]()
        
        # 再尝试作为名称查找
        style_id = cls._name_mapping.get(style_id_or_name)
        if style_id and style_id in cls._styles:
            return cls._styles[style_id]()
        
        # 尝试模糊匹配（去除emoji和空格）
        clean_name = style_id_or_name.strip()
        for name, sid in cls._name_mapping.items():
            if clean_name in name or name in clean_name:
                return cls._styles[sid]()
        
        return None
    
    @classmethod
    def get_default_style(cls) -> BaseStyle:
        """获取默认风格（认知重塑·破壁人）"""
        return CognitiveReshaperStyle()
    
    @classmethod
    def list_all_styles(cls) -> Dict[str, str]:
        """
        列出所有可用风格
        
        Returns:
            {风格显示名称: 风格ID}
        """
        return {
            "🎭 认知重塑·破壁人": "cognitive_reshaper",
            "🎬 治愈系·观察者": "healing_observer",
            "🚀 逆袭见证·养成系": "growth_witness",
            "🤯 情绪过山车·发疯艺术家": "emotional_rollercoaster",
            "🐕 萌即正义·哲学大师": "meme_philosopher",
        }
    
    @classmethod
    def get_style_names(cls) -> list:
        """获取所有风格显示名称列表（用于Streamlit下拉框）"""
        return list(cls.list_all_styles().keys())
    
    @classmethod
    def register_style(cls, style_id: str, style_class: Type[BaseStyle], names: list = None):
        """
        注册新风格
        
        Args:
            style_id: 风格唯一标识
            style_class: 风格类
            names: 风格的显示名称列表
        """
        cls._styles[style_id] = style_class
        if names:
            for name in names:
                cls._name_mapping[name] = style_id
    
    @classmethod
    def create_with_skill(cls, style_id_or_name: str, skill_content: str) -> tuple:
        """
        创建风格实例并生成完整的system prompt
        
        Args:
            style_id_or_name: 风格ID或名称
            skill_content: Skill文件中的总体Prompt模板
        
        Returns:
            (风格实例, 完整的system prompt)
        """
        style = cls.create(style_id_or_name) or cls.get_default_style()
        system_prompt = style.get_system_prompt(skill_content)
        return style, system_prompt
