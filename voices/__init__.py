# -*- coding: utf-8 -*-
"""
VideoTaxi 音色系统 - 面向对象架构
支持多种 TTS 引擎（Edge TTS、火山引擎等）
"""

from .base_voice import BaseVoice, VoiceConfig
from .edge_voice import EdgeVoice
from .volc_voice import VolcVoice
from .voice_factory import VoiceFactory

__all__ = [
    'BaseVoice',
    'VoiceConfig',
    'EdgeVoice',
    'VolcVoice',
    'VoiceFactory'
]
