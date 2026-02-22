# -*- coding: utf-8 -*-
"""
VideoTaxi 服务层 - 面向对象架构
整合所有业务逻辑，为UI层提供统一接口
"""

from .user_service import UserService
from .script_service import ScriptService
from .video_service import VideoService

__all__ = [
    'UserService',
    'ScriptService', 
    'VideoService'
]
