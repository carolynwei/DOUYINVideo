# -*- coding: utf-8 -*-
"""
Skill 文件加载器
用于从 .qoder/skills/ 目录加载 Prompt 模板
"""

import os
from typing import Optional


def load_skill(skill_name: str) -> str:
    """
    加载 Skill 文件内容
    
    Args:
        skill_name: Skill 文件名（不含 .md 后缀）
        
    Returns:
        Skill 文件内容
        
    Raises:
        FileNotFoundError: 如果文件不存在
    """
    # 可能的文件路径
    possible_paths = [
        # 项目根目录下的 .qoder/skills/
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.qoder', 'skills', f'{skill_name}.md'),
        # 当前目录下的 skills/
        os.path.join(os.path.dirname(__file__), 'skills', f'{skill_name}.md'),
        # 绝对路径（用于Streamlit Cloud）
        f'/mount/src/douyinvideo/.qoder/skills/{skill_name}.md',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    
    # 如果都找不到，返回默认提示词
    raise FileNotFoundError(f"Skill 文件未找到: {skill_name}.md，尝试路径: {possible_paths}")


def load_video_master_prompt() -> str:
    """
    加载视频生成总体 Prompt 模板
    
    Returns:
        video-master-prompt.md 的内容
    """
    return load_skill('video-master-prompt')


def get_skill_path(skill_name: str) -> Optional[str]:
    """
    获取 Skill 文件的完整路径
    
    Args:
        skill_name: Skill 文件名
        
    Returns:
        文件路径，如果找不到则返回 None
    """
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.qoder', 'skills', f'{skill_name}.md'),
        os.path.join(os.path.dirname(__file__), 'skills', f'{skill_name}.md'),
        f'/mount/src/douyinvideo/.qoder/skills/{skill_name}.md',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None
