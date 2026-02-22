# -*- coding: utf-8 -*-
"""
步骤3：视觉分镜与素材解耦
分镜脚本化 + 多模态并发 + 字幕排版
"""

import asyncio
from typing import Dict, Any, List
from .base_step import BaseStep, StepResult, StepContext


class VisualAssetStep(BaseStep):
    """
    视觉分镜与素材解耦
    
    功能：
    1. 分镜脚本化：脚本→画面描述词
    2. 多模态并发：素材库 vs AI生成
    3. 字幕排版：动态气泡字/强调色
    """
    
    step_id = "visual_asset"
    step_name = "视觉分镜与素材解耦"
    step_emoji = "🎨"
    step_description = "分镜脚本化 + 多模态并发 + 字幕排版"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.zhipu_api_key = config.get("zhipu_api_key", "")
        self.pexels_api_key = config.get("pexels_api_key", "")
    
    async def execute(self, context: StepContext) -> StepResult:
        """执行视觉资产生成"""
        try:
            scenes = context.scenes
            if not scenes:
                return StepResult(
                    success=False,
                    message="缺少脚本分镜",
                    error="请先完成脚本生成步骤"
                )
            
            # 1. 生成完整画面描述
            enhanced_scenes = await self._generate_visual_prompts(scenes, context)
            
            # 2. 并发获取视觉资产
            image_assets = await self._fetch_visual_assets(enhanced_scenes, context)
            
            # 3. 设计字幕样式
            subtitle_style = self._design_subtitle_style(context)
            
            # 更新上下文
            context.scenes = enhanced_scenes
            context.image_assets = image_assets
            
            return StepResult(
                success=True,
                data={
                    "scene_count": len(enhanced_scenes),
                    "image_count": len(image_assets),
                    "subtitle_style": subtitle_style
                },
                message=f"✅ 生成视觉资产: {len(image_assets)}张图片"
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message="视觉资产生成失败",
                error=str(e)
            )
    
    async def _generate_visual_prompts(self, scenes: List[Dict], context: StepContext) -> List[Dict]:
        """生成完整画面描述"""
        anchor = context.visual_anchor
        
        for scene in scenes:
            base_prompt = scene.get("image_prompt", "")
            # 组合视觉锚点 + 场景描述
            scene["full_prompt"] = f"{anchor}, {base_prompt}, cinematic lighting, 8k resolution"
            scene["prompt_enhanced"] = True
        
        return scenes
    
    async def _fetch_visual_assets(self, scenes: List[Dict], context: StepContext) -> List[str]:
        """并发获取视觉资产"""
        # 模拟图片路径
        return [f"scene_{i}.png" for i in range(len(scenes))]
    
    def _design_subtitle_style(self, context: StepContext) -> Dict:
        """设计字幕样式"""
        style_id = context.style_id
        
        styles = {
            "cognitive_reshaper": {
                "font": "bold",
                "color": "#FF3131",
                "highlight": "red_box",
                "animation": "typewriter"
            },
            "healing_observer": {
                "font": "elegant",
                "color": "#F5F5F5",
                "highlight": "soft_glow",
                "animation": "fade_in"
            },
            "default": {
                "font": "standard",
                "color": "#FFFFFF",
                "highlight": "underline",
                "animation": "pop"
            }
        }
        
        return styles.get(style_id, styles["default"])
