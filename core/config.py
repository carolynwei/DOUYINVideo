# -*- coding: utf-8 -*-
"""
配置管理模块 - 集中管理所有API密钥和配置
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class Config:
    """应用配置数据类"""
    # API Keys
    tianapi_key: str = ""
    deepseek_key: str = ""
    zhipu_key: str = ""
    pexels_key: str = ""
    volc_appid: str = ""
    volc_access_token: str = ""
    
    # 应用设置
    default_voice: str = "zh-CN-YunxiNeural"
    default_style: str = "cognitive_reshaper"
    output_dir: str = "./output"
    db_file: str = "app_data.db"
    
    # 功能开关
    use_video_model: bool = False
    enable_proxy: bool = False
    proxy_url: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tianapi_key': self.tianapi_key,
            'deepseek_key': self.deepseek_key,
            'zhipu_key': self.zhipu_key,
            'pexels_key': self.pexels_key,
            'volc_appid': self.volc_appid,
            'volc_access_token': self.volc_access_token,
            'default_voice': self.default_voice,
            'default_style': self.default_style,
            'output_dir': self.output_dir,
            'use_video_model': self.use_video_model
        }


class ConfigManager:
    """
    配置管理器
    负责从各种来源加载配置（环境变量、Streamlit secrets、文件）
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = Config()
        return cls._instance
    
    def __init__(self):
        self._initialized = False
    
    def load_from_secrets(self) -> 'ConfigManager':
        """从 Streamlit secrets 加载配置"""
        try:
            import streamlit as st
            
            # 扁平格式
            self._config.tianapi_key = st.secrets.get("TIANAPI_KEY", "")
            self._config.deepseek_key = st.secrets.get("DEEPSEEK_KEY", "")
            self._config.zhipu_key = st.secrets.get("ZHIPU_KEY", "")
            self._config.pexels_key = st.secrets.get("PEXELS_KEY", "")
            self._config.volc_appid = st.secrets.get("VOLC_APPID", "")
            self._config.volc_access_token = st.secrets.get("VOLC_ACCESS_TOKEN", "")
            
            # 嵌套格式
            if not self._config.tianapi_key and "tianapi" in st.secrets:
                self._config.tianapi_key = st.secrets.get("tianapi", {}).get("key", "")
            if not self._config.deepseek_key and "deepseek" in st.secrets:
                self._config.deepseek_key = st.secrets.get("deepseek", {}).get("key", "")
            if not self._config.zhipu_key and "zhipu" in st.secrets:
                self._config.zhipu_key = st.secrets.get("zhipu", {}).get("key", "")
            if not self._config.pexels_key and "pexels" in st.secrets:
                self._config.pexels_key = st.secrets.get("pexels", {}).get("key", "")
                
        except ImportError:
            pass
        
        return self
    
    def load_from_env(self) -> 'ConfigManager':
        """从环境变量加载配置"""
        self._config.tianapi_key = os.environ.get("TIANAPI_KEY", self._config.tianapi_key)
        self._config.deepseek_key = os.environ.get("DEEPSEEK_KEY", self._config.deepseek_key)
        self._config.zhipu_key = os.environ.get("ZHIPU_KEY", self._config.zhipu_key)
        self._config.pexels_key = os.environ.get("PEXELS_KEY", self._config.pexels_key)
        self._config.volc_appid = os.environ.get("VOLC_APPID", self._config.volc_appid)
        self._config.volc_access_token = os.environ.get("VOLC_ACCESS_TOKEN", self._config.volc_access_token)
        return self
    
    def get_config(self) -> Config:
        """获取当前配置"""
        return self._config
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def is_ready(self) -> bool:
        """检查核心配置是否就绪"""
        return bool(
            self._config.deepseek_key and 
            self._config.zhipu_key
        )
    
    def get_missing_keys(self) -> list:
        """获取缺失的必需密钥"""
        missing = []
        if not self._config.deepseek_key:
            missing.append("DEEPSEEK_KEY")
        if not self._config.zhipu_key:
            missing.append("ZHIPU_KEY")
        return missing
