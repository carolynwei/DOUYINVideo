# -*- coding: utf-8 -*-
"""
视频服务 - 面向对象架构
整合视频生成、TTS、图片生成等业务逻辑
"""

from typing import Optional, Dict, Any, List
from models import ScriptVersion, Scene
from core import ConfigManager, ZhipuClient
from voices import VoiceFactory
from workflow import WorkflowEngine
import os


class VideoService:
    """
    视频服务
    整合视频生成全流程：图片生成、TTS合成、视频渲染
    """
    
    def __init__(self, db_path: str = "app_data.db"):
        self._config = ConfigManager().get_config()
        self._zhipu = None
        self._workflow = None
        
        # 初始化API客户端
        if self._config.zhipu_key:
            self._zhipu = ZhipuClient(self._config.zhipu_key)
        
        # 初始化工作流引擎
        config_dict = self._config.to_dict() if hasattr(self._config, 'to_dict') else {}
        self._workflow = WorkflowEngine(config_dict)
    
    # ========== 图片生成 ==========
    
    def generate_images(self, scenes: List[Scene], use_video_model: bool = False) -> Dict[str, Any]:
        """
        为场景生成图片
        
        Returns:
            {
                'success': bool,
                'image_paths': List[str],
                'error': str
            }
        """
        if not self._zhipu:
            return {
                'success': False,
                'error': '智谱API未配置',
                'image_paths': []
            }
        
        image_paths = []
        
        for i, scene in enumerate(scenes):
            if not scene.image_prompt:
                continue
            
            if use_video_model:
                response = self._zhipu.generate_video(scene.image_prompt)
            else:
                response = self._zhipu.generate_image(scene.image_prompt)
            
            if response.success:
                # 下载图片/视频
                media_url = self._extract_media_url(response.data)
                if media_url:
                    ext = 'mp4' if use_video_model else 'jpg'
                    save_path = f"output/scene_{i+1}.{ext}"
                    os.makedirs("output", exist_ok=True)
                    
                    import urllib.request
                    try:
                        urllib.request.urlretrieve(media_url, save_path)
                        image_paths.append(save_path)
                        scene.image_path = save_path
                    except Exception as e:
                        print(f"下载媒体失败: {e}")
            else:
                print(f"生成场景{i+1}失败: {response.error}")
        
        return {
            'success': len(image_paths) > 0,
            'image_paths': image_paths,
            'error': None if image_paths else '所有图片生成失败'
        }
    
    # ========== TTS合成 ==========
    
    def generate_audio(self, scenes: List[Scene], voice_id: str = None) -> Dict[str, Any]:
        """
        为场景生成音频
        
        Returns:
            {
                'success': bool,
                'audio_paths': List[str],
                'error': str
            }
        """
        voice_id = voice_id or self._config.default_voice
        
        try:
            voice = VoiceFactory.create(voice_id)
        except Exception as e:
            return {
                'success': False,
                'error': f'音色创建失败: {e}',
                'audio_paths': []
            }
        
        audio_paths = []
        
        for i, scene in enumerate(scenes):
            if not scene.content:
                continue
            
            save_path = f"output/scene_{i+1}.mp3"
            os.makedirs("output", exist_ok=True)
            
            try:
                result = voice.synthesize(scene.content, save_path)
                if result.get('success'):
                    audio_paths.append(save_path)
                    scene.audio_path = save_path
                    # 更新场景时长
                    scene.duration = result.get('duration', 5.0)
                else:
                    print(f"合成场景{i+1}音频失败: {result.get('error')}")
            except Exception as e:
                print(f"合成场景{i+1}音频异常: {e}")
        
        return {
            'success': len(audio_paths) > 0,
            'audio_paths': audio_paths,
            'error': None if audio_paths else '所有音频合成失败'
        }
    
    # ========== 视频渲染 ==========
    
    def render_video(self, version: ScriptVersion, output_path: str = None) -> Dict[str, Any]:
        """
        渲染完整视频
        
        Returns:
            {
                'success': bool,
                'video_path': str,
                'error': str
            }
        """
        if not output_path:
            output_path = f"output/video_{version.user_id}_{int(os.time())}.mp4"
        
        # 检查所有场景是否都有图片和音频
        for scene in version.scenes:
            if not scene.image_path or not os.path.exists(scene.image_path):
                return {
                    'success': False,
                    'error': f'场景{scene.scene_number}缺少图片',
                    'video_path': None
                }
            if not scene.audio_path or not os.path.exists(scene.audio_path):
                return {
                    'success': False,
                    'error': f'场景{scene.scene_number}缺少音频',
                    'video_path': None
                }
        
        # 使用video_engine渲染视频
        try:
            from video_engine import render_ai_video_pipeline
            
            # 转换Scene为video_engine需要的格式
            scenes_data = []
            for scene in version.scenes:
                scenes_data.append({
                    'scene_number': scene.scene_number,
                    'content': scene.content,
                    'image_path': scene.image_path,
                    'audio_path': scene.audio_path,
                    'duration': scene.duration
                })
            
            # 调用渲染
            video_path = render_ai_video_pipeline(
                scenes_data=scenes_data,
                output_path=output_path,
                voice_id=version.voice_id
            )
            
            if video_path and os.path.exists(video_path):
                return {
                    'success': True,
                    'video_path': video_path,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'error': '视频渲染失败',
                    'video_path': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'渲染异常: {e}',
                'video_path': None
            }
    
    # ========== 完整工作流 ==========
    
    def generate_complete_video(self, version: ScriptVersion, 
                                progress_callback=None) -> Dict[str, Any]:
        """
        执行完整的视频生成工作流
        
        Args:
            version: 剧本版本
            progress_callback: 进度回调函数 (step, progress, message)
        
        Returns:
            {
                'success': bool,
                'video_path': str,
                'scenes': List[Scene],
                'error': str
            }
        """
        # Step 1: 生成图片
        if progress_callback:
            progress_callback('images', 0, '开始生成图片...')
        
        image_result = self.generate_images(version.scenes)
        if not image_result['success']:
            return {
                'success': False,
                'error': f"图片生成失败: {image_result['error']}",
                'video_path': None,
                'scenes': version.scenes
            }
        
        if progress_callback:
            progress_callback('images', 100, '图片生成完成')
        
        # Step 2: 生成音频
        if progress_callback:
            progress_callback('audio', 0, '开始合成音频...')
        
        audio_result = self.generate_audio(version.scenes, version.voice_id)
        if not audio_result['success']:
            return {
                'success': False,
                'error': f"音频合成失败: {audio_result['error']}",
                'video_path': None,
                'scenes': version.scenes
            }
        
        if progress_callback:
            progress_callback('audio', 100, '音频合成完成')
        
        # Step 3: 渲染视频
        if progress_callback:
            progress_callback('video', 0, '开始渲染视频...')
        
        video_result = self.render_video(version)
        
        if progress_callback:
            progress_callback('video', 100, '视频渲染完成' if video_result['success'] else '渲染失败')
        
        return {
            'success': video_result['success'],
            'video_path': video_result.get('video_path'),
            'scenes': version.scenes,
            'error': video_result.get('error')
        }
    
    # ========== 辅助方法 ==========
    
    def _extract_media_url(self, data: Dict) -> Optional[str]:
        """从API响应中提取媒体URL"""
        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                return data['data'][0].get('url')
            if 'url' in data:
                return data['url']
        return None
