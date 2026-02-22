# -*- coding: utf-8 -*-
"""
风格基类 - 定义所有风格的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None


class BaseStyle(ABC):
    """
    视频风格基类
    所有具体风格必须继承此类并实现抽象方法
    """
    
    # 风格标识（子类必须覆盖）
    style_id: str = ""
    style_name: str = ""
    style_emoji: str = ""
    
    # 视觉配置
    default_shot: str = "close_up"
    bgm_style: str = ""
    
    def __init__(self):
        """初始化风格配置"""
        self.config = self._build_config()
    
    @abstractmethod
    def get_tone(self) -> str:
        """获取风格语调描述"""
        pass
    
    @abstractmethod
    def get_hook_formula(self) -> str:
        """获取Hook公式"""
        pass
    
    @abstractmethod
    def get_visual_base(self) -> str:
        """获取视觉基调"""
        pass
    
    @abstractmethod
    def get_visual_rules(self) -> str:
        """获取视觉规则（详细）"""
        pass
    
    @abstractmethod
    def get_shot_keywords(self) -> str:
        """获取镜头关键词（英文，用于image_prompt）"""
        pass
    
    def get_bgm_style(self) -> str:
        """获取BGM风格描述"""
        return self.bgm_style
    
    def get_default_shot(self) -> str:
        """获取默认镜头类型"""
        return self.default_shot
    
    def _build_config(self) -> Dict[str, Any]:
        """构建风格配置字典"""
        return {
            "tone": self.get_tone(),
            "hook": self.get_hook_formula(),
            "visual_base": self.get_visual_base(),
            "visual_rules": self.get_visual_rules(),
            "shot_keywords": self.get_shot_keywords(),
            "default_shot": self.get_default_shot(),
            "bgm_style": self.get_bgm_style()
        }
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config
    
    def get_system_prompt(self, skill_content: str) -> str:
        """
        生成系统Prompt
        
        Args:
            skill_content: 从Skill文件加载的总体Prompt模板
        
        Returns:
            完整的system prompt
        """
        config = self.config
        
        prompt = f"""{skill_content}

【当前风格】：{self.style_name}

【核心风格约束】：
{config['tone']}

【Hook 公式】：
{config['hook']}

【视觉基调】：
{config['visual_base']}

【强制视觉分镜约束】：
{config['visual_rules']}

【镜头关键词】：
{config['shot_keywords']}

【BGM风格】：
{config['bgm_style']}
"""
        return prompt
    
    def render_preview(self):
        """在Streamlit中渲染风格预览卡片"""
        if not HAS_STREAMLIT or st is None:
            print(f"风格预览: {self.style_emoji} {self.style_name}")
            return
            
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #FF3131;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background: linear-gradient(135deg, rgba(255,49,49,0.05) 0%, rgba(0,0,0,0) 100%);
            ">
                <h4>{self.style_emoji} {self.style_name}</h4>
                <p style="color: #888; font-size: 12px;">{self.get_tone()[:50]}...</p>
            </div>
            """, unsafe_allow_html=True)
    
    def __str__(self) -> str:
        return f"{self.style_emoji} {self.style_name}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.style_id}>"
