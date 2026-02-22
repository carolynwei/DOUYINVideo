# -*- coding: utf-8 -*-
"""
应用状态管理模块 - 面向对象的状态管理
替代分散的 session_state 操作
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


class WorkflowState(Enum):
    """工作流状态枚举"""
    DRAFT = "draft"           # 草稿/编辑中
    LOCKED = "locked"         # 已锁定，准备生产
    PRODUCING = "producing"   # 生产中
    COMPLETED = "completed"   # 已完成


@dataclass
class UserSession:
    """用户会话数据"""
    user_id: str = ""
    credits: int = 0
    is_logged_in: bool = False


@dataclass
class ProjectData:
    """项目数据"""
    topic: str = ""
    style_id: str = "cognitive_reshaper"
    voice_id: str = "zh-CN-YunxiNeural"
    scenes: List[Dict] = field(default_factory=list)
    script_versions: List[Dict] = field(default_factory=list)
    current_version_index: int = -1


class AppState:
    """
    应用状态管理器
    集中管理所有应用状态，替代分散的 session_state 操作
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_defaults()
        return cls._instance
    
    def _init_defaults(self):
        """初始化默认值"""
        self._workflow_state = WorkflowState.DRAFT
        self._user_session = UserSession()
        self._project = ProjectData()
        self._chat_history: List[Dict] = []
        self._hot_topics: List[str] = []
        self._config: Dict[str, Any] = {}
    
    # ========== 工作流状态管理 ==========
    
    @property
    def workflow_state(self) -> WorkflowState:
        return self._workflow_state
    
    def set_workflow_state(self, state: WorkflowState):
        """设置工作流状态"""
        self._workflow_state = state
        self._sync_to_session("workflow_state", state.value)
    
    def is_draft(self) -> bool:
        return self._workflow_state == WorkflowState.DRAFT
    
    def is_locked(self) -> bool:
        return self._workflow_state == WorkflowState.LOCKED
    
    def is_producing(self) -> bool:
        return self._workflow_state == WorkflowState.PRODUCING
    
    def is_completed(self) -> bool:
        return self._workflow_state == WorkflowState.COMPLETED
    
    # ========== 用户会话管理 ==========
    
    @property
    def user_session(self) -> UserSession:
        return self._user_session
    
    def login(self, user_id: str, credits: int = 0):
        """用户登录"""
        self._user_session.user_id = user_id
        self._user_session.credits = credits
        self._user_session.is_logged_in = True
        self._sync_to_session("user_id", user_id)
    
    def logout(self):
        """用户登出"""
        self._user_session = UserSession()
        self._sync_to_session("user_id", "")
    
    def update_credits(self, credits: int):
        """更新积分"""
        self._user_session.credits = credits
        self._sync_to_session("credits", credits)
    
    # ========== 项目管理 ==========
    
    @property
    def project(self) -> ProjectData:
        return self._project
    
    def set_topic(self, topic: str):
        """设置主题"""
        self._project.topic = topic
        self._sync_to_session("topic", topic)
    
    def set_style(self, style_id: str):
        """设置风格"""
        self._project.style_id = style_id
        self._sync_to_session("style_id", style_id)
    
    def set_voice(self, voice_id: str):
        """设置音色"""
        self._project.voice_id = voice_id
        self._sync_to_session("voice_id", voice_id)
    
    def set_scenes(self, scenes: List[Dict]):
        """设置分镜"""
        self._project.scenes = scenes
        self._sync_to_session("scenes_data", scenes)
    
    def save_script_version(self, version_name: str, scenes: List[Dict]):
        """保存剧本版本"""
        version = {
            "name": version_name,
            "scenes": scenes,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        self._project.script_versions.append(version)
        self._project.current_version_index = len(self._project.script_versions) - 1
        self._sync_to_session("script_versions", self._project.script_versions)
    
    # ========== 聊天记录 ==========
    
    @property
    def chat_history(self) -> List[Dict]:
        return self._chat_history
    
    def add_chat_message(self, role: str, content: str):
        """添加聊天消息"""
        message = {
            "role": role,
            "content": content,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        self._chat_history.append(message)
        self._sync_to_session("chat_history", self._chat_history)
    
    def clear_chat_history(self):
        """清空聊天记录"""
        self._chat_history = []
        self._sync_to_session("chat_history", [])
    
    # ========== 热点数据 ==========
    
    @property
    def hot_topics(self) -> List[str]:
        return self._hot_topics
    
    def set_hot_topics(self, topics: List[str]):
        """设置热点列表"""
        self._hot_topics = topics
        self._sync_to_session("hot_topics", topics)
    
    # ========== 配置管理 ==========
    
    def set_config(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value
        self._sync_to_session(key, value)
    
    def get_config(self, key: str, default=None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    # ========== Streamlit 同步 ==========
    
    def _sync_to_session(self, key: str, value: Any):
        """同步到 Streamlit session_state"""
        try:
            import streamlit as st
            st.session_state[key] = value
        except ImportError:
            pass
    
    def load_from_session(self):
        """从 Streamlit session_state 加载状态"""
        try:
            import streamlit as st
            
            # 加载工作流状态
            if 'workflow_state' in st.session_state:
                state_value = st.session_state['workflow_state']
                self._workflow_state = WorkflowState(state_value)
            
            # 加载用户会话
            if 'user_id' in st.session_state:
                self._user_session.user_id = st.session_state['user_id']
                self._user_session.is_logged_in = bool(st.session_state['user_id'])
            
            # 加载项目数据
            if 'topic' in st.session_state:
                self._project.topic = st.session_state['topic']
            if 'style_id' in st.session_state:
                self._project.style_id = st.session_state['style_id']
            if 'voice_id' in st.session_state:
                self._project.voice_id = st.session_state['voice_id']
            if 'scenes_data' in st.session_state:
                self._project.scenes = st.session_state['scenes_data']
            if 'script_versions' in st.session_state:
                self._project.script_versions = st.session_state['script_versions']
            
            # 加载其他数据
            if 'chat_history' in st.session_state:
                self._chat_history = st.session_state['chat_history']
            if 'hot_topics' in st.session_state:
                self._hot_topics = st.session_state['hot_topics']
                
        except ImportError:
            pass
    
    def reset_project(self):
        """重置项目数据（保留用户会话）"""
        self._project = ProjectData()
        self._workflow_state = WorkflowState.DRAFT
        self._chat_history = []
        
        # 同步到 session
        self._sync_to_session("scenes_data", [])
        self._sync_to_session("chat_history", [])
        self._sync_to_session("workflow_state", WorkflowState.DRAFT.value)
