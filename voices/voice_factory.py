# -*- coding: utf-8 -*-
"""
音色工厂 - 根据音色ID创建对应音色实例
支持自动路由和降级策略
"""

from typing import Dict, Type, Optional, List
from .base_voice import BaseVoice, VoiceConfig
from .edge_voice import EdgeVoice
from .volc_voice import VolcVoice


class VoiceFactory:
    """
    音色工厂类
    负责创建和管理音色实例，支持自动路由
    """
    
    # 音色注册表
    _voice_registry: Dict[str, Dict] = {
        # Edge TTS 音色
        "zh-CN-YunxiNeural": {"engine": "edge", "key": "yunxi", "class": EdgeVoice},
        "zh-CN-XiaoxiaoNeural": {"engine": "edge", "key": "xiaoxiao", "class": EdgeVoice},
        "zh-CN-YunyeNeural": {"engine": "edge", "key": "yunye", "class": EdgeVoice},
        "zh-CN-XiaoyiNeural": {"engine": "edge", "key": "xiaoyi", "class": EdgeVoice},
        
        # 火山引擎音色
        "volc_lingcheng_wanqu": {"engine": "volc", "key": "lingcheng", "class": VolcVoice},
        "volc_xinglin_chengshu": {"engine": "volc", "key": "xinglin", "class": VolcVoice},
        "volc_mingxuan_qingsu": {"engine": "volc", "key": "mingxuan", "class": VolcVoice},
        "volc_yanping_tianmei": {"engine": "volc", "key": "yanping", "class": VolcVoice},
        "volc_yuanfeng_huoli": {"engine": "volc", "key": "yuanfeng", "class": VolcVoice},
    }
    
    # 显示名称映射
    _display_names: Dict[str, str] = {
        "zh-CN-YunxiNeural": "🎙️ 云希 (抖音热门)",
        "zh-CN-XiaoxiaoNeural": "🎙️ 晓晓 (温柔女声)",
        "zh-CN-YunyeNeural": "🎙️ 云野 (磁性男声)",
        "zh-CN-XiaoyiNeural": "🎙️ 晓伊 (活泼女声)",
        "volc_lingcheng_wanqu": "🔥 火山-温柔女声",
        "volc_xinglin_chengshu": "🔥 火山-成熟男声",
        "volc_mingxuan_qingsu": "🔥 火山-暴躁老哥",
        "volc_yanping_tianmei": "🔥 火山-甜美女声",
        "volc_yuanfeng_huoli": "🔥 火山-活力少年",
    }
    
    @classmethod
    def create(cls, voice_id: str) -> Optional[BaseVoice]:
        """
        创建音色实例
        
        Args:
            voice_id: 音色ID
        
        Returns:
            音色实例，如果找不到则返回None
        """
        voice_info = cls._voice_registry.get(voice_id)
        if not voice_info:
            return None
        
        voice_class = voice_info["class"]
        voice_key = voice_info["key"]
        
        return voice_class(voice_key)
    
    @classmethod
    def create_with_fallback(cls, voice_id: str) -> BaseVoice:
        """
        创建音色实例，如果不可用则自动降级
        
        Args:
            voice_id: 首选音色ID
        
        Returns:
            可用的音色实例
        """
        # 尝试创建首选音色
        voice = cls.create(voice_id)
        if voice and voice.is_available():
            return voice
        
        # 如果是火山引擎失败，降级到 Edge TTS
        if voice_id.startswith("volc_"):
            print(f"⚠️ 火山引擎不可用，降级到 Edge TTS")
            fallback = cls.create("zh-CN-YunxiNeural")
            if fallback:
                return fallback
        
        # 默认返回云希
        default = cls.create("zh-CN-YunxiNeural")
        if default:
            return default
        
        # 最后的兜底
        return EdgeVoice("yunxi")
    
    @classmethod
    def get_display_name(cls, voice_id: str) -> str:
        """获取显示名称"""
        return cls._display_names.get(voice_id, voice_id)
    
    @classmethod
    def list_all_voices(cls) -> List[str]:
        """列出所有可用音色ID"""
        return list(cls._display_names.keys())
    
    @classmethod
    def list_edge_voices(cls) -> List[str]:
        """列出 Edge TTS 音色"""
        return [vid for vid in cls._display_names.keys() if not vid.startswith("volc_")]
    
    @classmethod
    def list_volc_voices(cls) -> List[str]:
        """列出火山引擎音色"""
        return [vid for vid in cls._display_names.keys() if vid.startswith("volc_")]
    
    @classmethod
    def get_voice_mapping(cls) -> Dict[str, str]:
        """
        获取音色映射（用于Streamlit下拉框）
        
        Returns:
            {显示名称: voice_id}
        """
        return {name: vid for vid, name in cls._display_names.items()}
    
    @classmethod
    def get_default_voice(cls) -> BaseVoice:
        """获取默认音色（云希）"""
        return cls.create("zh-CN-YunxiNeural") or EdgeVoice("yunxi")
    
    @classmethod
    def register_voice(cls, voice_id: str, voice_class: Type[BaseVoice], 
                       voice_key: str, display_name: str, engine: str = "custom"):
        """
        注册新音色
        
        Args:
            voice_id: 音色唯一标识
            voice_class: 音色类
            voice_key: 音色在类中的键名
            display_name: 显示名称
            engine: 引擎类型
        """
        cls._voice_registry[voice_id] = {
            "engine": engine,
            "key": voice_key,
            "class": voice_class
        }
        cls._display_names[voice_id] = display_name


class VoiceRouter:
    """
    音色路由器
    根据场景/情绪自动选择最佳音色
    """
    
    # 场景到音色的映射
    SCENE_VOICE_MAP = {
        "知识科普": "zh-CN-YunyeNeural",      # 云野 - 磁性权威
        "情感治愈": "zh-CN-XiaoxiaoNeural",   # 晓晓 - 温柔女声
        "搞笑娱乐": "zh-CN-XiaoyiNeural",     # 晓伊 - 活泼女声
        "热血励志": "volc_xinglin_chengshu",  # 火山成熟男声
        "温柔萌系": "volc_yanping_tianmei",   # 火山甜美女声
        "吐槽吐槽": "volc_mingxuan_qingsu",   # 火山暴躁老哥
        "默认": "zh-CN-YunxiNeural",          # 云希 - 通用
    }
    
    @classmethod
    def route_by_scene(cls, scene: str) -> str:
        """
        根据场景推荐音色
        
        Args:
            scene: 场景描述
        
        Returns:
            voice_id
        """
        for key, voice_id in cls.SCENE_VOICE_MAP.items():
            if key in scene:
                return voice_id
        return cls.SCENE_VOICE_MAP["默认"]
    
    @classmethod
    def route_by_emotion(cls, emotion: str) -> str:
        """
        根据情绪推荐音色
        
        Args:
            emotion: 情绪标签
        
        Returns:
            voice_id
        """
        emotion_map = {
            "angry": "volc_mingxuan_qingsu",      # 愤怒 -> 暴躁老哥
            "gentle": "zh-CN-XiaoxiaoNeural",     # 温柔 -> 晓晓
            "excited": "zh-CN-XiaoyiNeural",      # 兴奋 -> 晓伊
            "serious": "zh-CN-YunyeNeural",       # 严肃 -> 云野
            "cute": "volc_yanping_tianmei",       # 可爱 -> 甜美女声
        }
        return emotion_map.get(emotion, "zh-CN-YunxiNeural")
