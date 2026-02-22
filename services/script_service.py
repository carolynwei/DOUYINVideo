# -*- coding: utf-8 -*-
"""
剧本服务 - 面向对象架构
整合剧本生成、版本管理等业务逻辑
"""

from typing import Optional, Dict, Any, List
from models import ScriptVersion, ScriptManager, Scene
from core import ConfigManager, DeepSeekClient, TianapiClient
from styles import StyleFactory


class ScriptService:
    """
    剧本服务
    整合剧本生成、版本管理、风格应用等业务
    """
    
    def __init__(self, db_path: str = "app_data.db"):
        self._script_manager = ScriptManager(db_path=db_path)
        self._config = ConfigManager().get_config()
        self._deepseek = None
        self._tianapi = None
        
        # 初始化API客户端
        if self._config.deepseek_key:
            self._deepseek = DeepSeekClient(self._config.deepseek_key)
        if self._config.tianapi_key:
            self._tianapi = TianapiClient(self._config.tianapi_key)
    
    # ========== 热点获取 ==========
    
    def get_hot_topics(self) -> List[str]:
        """获取抖音热点话题"""
        if not self._tianapi:
            return []
        
        response = self._tianapi.get_douyin_hot()
        if response.success:
            return response.data
        return []
    
    # ========== 剧本生成 ==========
    
    def generate_script(self, topic: str, style_id: str = None) -> Dict[str, Any]:
        """
        生成剧本
        
        Returns:
            {
                'success': bool,
                'scenes': List[Scene],
                'topic': str,
                'style_id': str,
                'error': str
            }
        """
        if not self._deepseek:
            return {
                'success': False,
                'error': 'DeepSeek API 未配置',
                'scenes': [],
                'topic': topic,
                'style_id': style_id or self._config.default_style
            }
        
        style_id = style_id or self._config.default_style
        
        # 获取风格配置
        try:
            style = StyleFactory.create(style_id)
            system_prompt = style.get_system_prompt()
        except Exception as e:
            return {
                'success': False,
                'error': f'风格加载失败: {e}',
                'scenes': [],
                'topic': topic,
                'style_id': style_id
            }
        
        # 调用DeepSeek生成剧本
        response = self._deepseek.generate_script(topic, system_prompt)
        
        if not response.success:
            return {
                'success': False,
                'error': response.error,
                'scenes': [],
                'topic': topic,
                'style_id': style_id
            }
        
        # 解析返回的剧本数据
        try:
            data = response.data
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                import json
                script_data = json.loads(content)
                
                # 转换为Scene对象
                scenes = []
                for i, scene_data in enumerate(script_data.get('scenes', [])):
                    scene = Scene(
                        scene_number=i + 1,
                        content=scene_data.get('content', ''),
                        image_prompt=scene_data.get('image_prompt', ''),
                        duration=scene_data.get('duration', 5.0)
                    )
                    scenes.append(scene)
                
                return {
                    'success': True,
                    'scenes': scenes,
                    'topic': topic,
                    'style_id': style_id,
                    'error': None
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析剧本失败: {e}',
                'scenes': [],
                'topic': topic,
                'style_id': style_id
            }
        
        return {
            'success': False,
            'error': '未知错误',
            'scenes': [],
            'topic': topic,
            'style_id': style_id
        }
    
    # ========== 版本管理 ==========
    
    def save_version(self, user_id: str, version_name: str, 
                     scenes: List[Scene], topic: str = "",
                     style_id: str = "", voice_id: str = "") -> ScriptVersion:
        """保存剧本版本"""
        version = ScriptVersion(
            user_id=user_id,
            version_name=version_name,
            topic=topic,
            style_id=style_id,
            voice_id=voice_id,
            scenes=scenes
        )
        return self._script_manager.save_version(version)
    
    def get_user_versions(self, user_id: str) -> List[ScriptVersion]:
        """获取用户的所有版本"""
        return self._script_manager.get_user_versions(user_id)
    
    def get_version(self, version_id: int) -> Optional[ScriptVersion]:
        """获取指定版本"""
        return self._script_manager.get_version(version_id)
    
    def delete_version(self, version_id: int) -> bool:
        """删除版本"""
        return self._script_manager.delete_version(version_id)
    
    def lock_version(self, version_id: int) -> bool:
        """锁定版本"""
        return self._script_manager.lock_version(version_id)
    
    # ========== 场景编辑 ==========
    
    def update_scene_content(self, version: ScriptVersion, scene_number: int, 
                            new_content: str) -> bool:
        """更新场景内容"""
        for scene in version.scenes:
            if scene.scene_number == scene_number:
                scene.content = new_content
                return True
        return False
    
    def update_scene_image_prompt(self, version: ScriptVersion, scene_number: int,
                                  new_prompt: str) -> bool:
        """更新场景图片提示词"""
        for scene in version.scenes:
            if scene.scene_number == scene_number:
                scene.image_prompt = new_prompt
                return True
        return False
