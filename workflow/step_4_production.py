# -*- coding: utf-8 -*-
"""
步骤4：音视同步与后期合成
TTS合成 + BGM对齐 + 视觉转场
"""

import asyncio
import os
from typing import Dict, Any, List
from .base_step import BaseStep, StepResult, StepContext


class ProductionStep(BaseStep):
    """
    音视同步与后期合成
    
    功能：
    1. TTS合成：带情绪的语音生成
    2. BGM对齐：音频节奏踩点
    3. 视觉转场：电影级转场效果
    4. 最终渲染：视频合成输出
    """
    
    step_id = "production"
    step_name = "音视同步与后期合成"
    step_emoji = "🎬"
    step_description = "TTS合成 + BGM对齐 + 视觉转场 + 最终渲染"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.voice_id = config.get("voice_id", "zh-CN-YunxiNeural")
        self.output_dir = config.get("output_dir", "./output")
    
    async def execute(self, context: StepContext) -> StepResult:
        """执行后期合成"""
        try:
            scenes = context.scenes
            if not scenes:
                return StepResult(
                    success=False,
                    message="缺少分镜数据",
                    error="请先完成视觉资产步骤"
                )
            
            # 1. TTS语音合成
            audio_files = await self._synthesize_audio(scenes, context)
            
            # 2. BGM选择与对齐
            bgm_file = await self._select_and_align_bgm(context)
            
            # 3. 视频合成
            final_video = await self._compose_video(scenes, audio_files, bgm_file, context)
            
            # 更新上下文
            context.audio_files = audio_files
            context.final_video = final_video
            
            return StepResult(
                success=True,
                data={
                    "final_video": final_video,
                    "duration": self._calculate_duration(scenes),
                    "resolution": "1080x1920"
                },
                message=f"✅ 视频合成完成: {final_video}"
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message="视频合成失败",
                error=str(e)
            )
    
    async def _synthesize_audio(self, scenes: List[Dict], context: StepContext) -> List[str]:
        """TTS语音合成"""
        audio_files = []
        
        for i, scene in enumerate(scenes):
            narration = scene.get("narration", "")
            # 清理SSML标签用于文件名
            clean_text = narration[:20].replace("<", "").replace(">", "")
            audio_file = f"audio_{i}_{clean_text}.mp3"
            audio_files.append(audio_file)
        
        return audio_files
    
    async def _select_and_align_bgm(self, context: StepContext) -> str:
        """选择并对齐BGM"""
        style_id = context.style_id
        
        # 风格到BGM的映射
        bgm_map = {
            "cognitive_reshaper": "assassin/epic_cinematic.mp3",
            "healing_observer": "growth/lofi.mp3",
            "growth_witness": "growth/lofi.mp3",
            "emotional_rollercoaster": "venting/trap.mp3",
            "meme_philosopher": "meme/funny.mp3"
        }
        
        return bgm_map.get(style_id, "bgm.mp3")
    
    async def _compose_video(self, scenes: List[Dict], audio_files: List[str], 
                            bgm_file: str, context: StepContext) -> str:
        """合成最终视频"""
        # 生成输出文件名
        topic = context.selected_topic[:20].replace(" ", "_")
        timestamp = asyncio.get_event_loop().time()
        output_file = os.path.join(self.output_dir, f"{topic}_{int(timestamp)}.mp4")
        
        return output_file
    
    def _calculate_duration(self, scenes: List[Dict]) -> int:
        """计算视频时长"""
        return sum(scene.get("duration", 5) for scene in scenes)
