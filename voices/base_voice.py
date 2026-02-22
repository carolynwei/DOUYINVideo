# -*- coding: utf-8 -*-
"""
音色基类 - 定义所有 TTS 引擎的通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os


@dataclass
class VoiceConfig:
    """音色配置数据类"""
    voice_id: str
    voice_name: str
    voice_emoji: str
    description: str
    gender: str  # male/female
    style: str   # 风格标签
    is_emotional: bool = False  # 是否支持情绪控制
    supports_ssml: bool = False  # 是否支持 SSML


class BaseVoice(ABC):
    """
    TTS 音色基类
    所有具体音色引擎必须继承此类并实现抽象方法
    """
    
    # 引擎标识（子类必须覆盖）
    engine_id: str = ""
    engine_name: str = ""
    
    def __init__(self, config: VoiceConfig):
        """
        初始化音色
        
        Args:
            config: 音色配置
        """
        self.config = config
    
    @abstractmethod
    async def synthesize(self, text: str, output_path: str, **kwargs) -> bool:
        """
        合成语音
        
        Args:
            text: 要合成的文本（可能包含 SSML）
            output_path: 输出文件路径
            **kwargs: 额外参数（语速、音调等）
        
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查引擎是否可用（API密钥等）"""
        pass
    
    def get_voice_id(self) -> str:
        """获取音色ID"""
        return self.config.voice_id
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return f"{self.config.voice_emoji} {self.config.voice_name}"
    
    def get_config(self) -> VoiceConfig:
        """获取配置"""
        return self.config
    
    def preprocess_text(self, text: str) -> str:
        """
        预处理文本（子类可覆盖）
        
        Args:
            text: 原始文本
        
        Returns:
            处理后的文本
        """
        # 默认：去除多余空白
        return ' '.join(text.split())
    
    def validate_output(self, output_path: str) -> bool:
        """
        验证输出文件是否有效
        
        Args:
            output_path: 文件路径
        
        Returns:
            是否有效
        """
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    
    def __str__(self) -> str:
        return self.get_display_name()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.config.voice_id}>"
