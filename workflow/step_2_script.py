# -*- coding: utf-8 -*-
"""
步骤2：差异化脚本生成
三段式结构 + 风格迁移 + SSML情绪标注
"""

import asyncio
from typing import Dict, Any, List
from .base_step import BaseStep, StepResult, StepContext


class ScriptGenerationStep(BaseStep):
    """
    差异化脚本生成
    
    功能：
    1. 三段式结构：强钩子 + 反转/干货 + 引导互动
    2. 风格迁移：根据选定风格调整语感
    3. 视觉锚点生成：确保画面一致性
    4. SSML情绪标注：TTS情绪控制
    """
    
    step_id = "script_generation"
    step_name = "差异化脚本生成"
    step_emoji = "✍️"
    step_description = "三段式结构 + 风格迁移 + SSML情绪标注"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm_api_key = config.get("llm_api_key", "")
        self.style_id = config.get("style_id", "cognitive_reshaper")
    
    async def execute(self, context: StepContext) -> StepResult:
        """
        执行脚本生成
        
        流程：
        1. 生成视觉锚点
        2. 生成脚本结构
        3. 应用风格迁移
        4. 添加SSML标注
        """
        try:
            topic = context.selected_topic
            if not topic:
                return StepResult(
                    success=False,
                    message="缺少选题信息",
                    error="请先完成选题步骤"
                )
            
            # 1. 生成视觉锚点
            visual_anchor = await self._generate_visual_anchor(topic, context)
            
            # 2. 生成三段式脚本
            script_data = await self._generate_script_structure(topic, context)
            
            # 3. 应用风格迁移
            styled_script = await self._apply_style_migration(script_data, context)
            
            # 4. 添加SSML情绪标注
            final_scenes = await self._add_ssml_annotations(styled_script)
            
            # 更新上下文
            context.visual_anchor = visual_anchor
            context.script_data = {
                "topic": topic,
                "visual_anchor": visual_anchor,
                "hook": script_data.get("hook", ""),
                "body": script_data.get("body", ""),
                "cta": script_data.get("cta", ""),
                "style": self.style_id
            }
            context.scenes = final_scenes
            
            return StepResult(
                success=True,
                data={
                    "visual_anchor": visual_anchor,
                    "scene_count": len(final_scenes),
                    "scenes": final_scenes,
                    "estimated_duration": self._estimate_duration(final_scenes)
                },
                message=f"✅ 生成脚本: {len(final_scenes)}个分镜"
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message="脚本生成失败",
                error=str(e)
            )
    
    async def _generate_visual_anchor(self, topic: str, context: StepContext) -> str:
        """生成视觉锚点（确保画面一致性）"""
        # 根据话题类型推断主角
        if "职场" in topic:
            return "A 35-year-old Asian professional, wearing smart casual, confident expression"
        elif "AI" in topic:
            return "A young tech enthusiast, modern minimalist style, curious expression"
        else:
            return "A relatable young protagonist, contemporary urban style"
    
    async def _generate_script_structure(self, topic: str, context: StepContext) -> Dict:
        """生成三段式脚本结构"""
        # 获取爆款基因
        viral_genes = context.topic_analysis.get("viral_genes", {})
        hook_pattern = viral_genes.get("hook_pattern", "悬念式")
        
        # 根据Hook模式生成开场
        hooks = {
            "反常识开场": f"所有人都说{topic}，但真相恰恰相反...",
            "数据冲击": f"95%的人都不知道，{topic}背后的数字让人震惊",
            "悬念式": f"关于{topic}，我有一个秘密要告诉你",
            "预言式": f"三年后，{topic}将彻底改变你的生活"
        }
        
        hook = hooks.get(hook_pattern, hooks["悬念式"])
        
        # 主体内容（模拟）
        body = f"""
        第一点：打破常规认知
        第二点：提供新视角/解决方案
        第三点：强化核心观点
        """
        
        # 引导互动
        cta = "你觉得呢？评论区告诉我你的看法"
        
        return {
            "hook": hook,
            "body": body,
            "cta": cta,
            "hook_pattern": hook_pattern
        }
    
    async def _apply_style_migration(self, script: Dict, context: StepContext) -> Dict:
        """应用风格迁移"""
        # 根据风格调整语感
        style_tones = {
            "cognitive_reshaper": "冷静笃定，逻辑清晰",
            "healing_observer": "温柔诗意，神性视角",
            "growth_witness": "真诚口语，求助感恩",
            "emotional_rollercoaster": "极端戏剧，情绪波动",
            "meme_philosopher": "幽默智慧，流行梗"
        }
        
        tone = style_tones.get(self.style_id, "自然流畅")
        
        return {
            **script,
            "tone": tone,
            "style_applied": True
        }
    
    async def _add_ssml_annotations(self, script: Dict) -> List[Dict]:
        """添加SSML情绪标注"""
        scenes = []
        
        # Hook分镜 - 冷启动
        scenes.append({
            "narration": f'<prosody rate="slow" pitch="-5%">{script["hook"]}</prosody><break time="500ms"/>',
            "image_prompt": "Hook scene visual",
            "emotion": "cold_question",
            "sfx_label": "[Suspense]",
            "duration": 3
        })
        
        # 内容分镜 - 深入
        body_points = script["body"].strip().split('\n')
        for i, point in enumerate(body_points[:3], 1):
            if point.strip():
                scenes.append({
                    "narration": f'<prosody rate="medium">{point.strip()}</prosody>',
                    "image_prompt": f"Content scene {i}",
                    "emotion": "neutral_narrate" if i < 3 else "deep_mystery",
                    "sfx_label": "[Transition]",
                    "duration": 5
                })
        
        # 高潮分镜 - 爆发
        scenes.append({
            "narration": f'<prosody rate="fast" pitch="+10%">这就是真相！</prosody>',
            "image_prompt": "Climax scene",
            "emotion": "excited_announce",
            "sfx_label": "[Impact]",
            "duration": 3
        })
        
        # CTA分镜 - 余韵
        scenes.append({
            "narration": f'<prosody rate="slow">{script["cta"]}</prosody>',
            "image_prompt": "CTA scene",
            "emotion": "neutral_narrate",
            "sfx_label": "[Silence]",
            "duration": 3
        })
        
        return scenes
    
    def _estimate_duration(self, scenes: List[Dict]) -> int:
        """估算视频时长"""
        return sum(scene.get("duration", 5) for scene in scenes)
