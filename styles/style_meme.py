# -*- coding: utf-8 -*-
"""
萌即正义·哲学大师 风格
用最软的脸说最硬的道理，用幽默消解焦虑
"""

from .base_style import BaseStyle


class MemePhilosopherStyle(BaseStyle):
    """
    萌即正义·哲学大师
    幽默、智慧、举重若轻。目标：用最软的脸说最硬的道理，用幽默消解焦虑。
    语言：一本正经的胡说八道，充满流行梗。
    """
    
    style_id = "meme_philosopher"
    style_name = "萌即正义·哲学大师"
    style_emoji = "🐕"
    default_shot = "close_up"
    
    def get_tone(self) -> str:
        return """幽默、智慧、举重若轻。目标：用最软的脸说最硬的道理，用幽默消解焦虑。
语言：一本正经的胡说八道，充满流行梗。"""
    
    def get_hook_formula(self) -> str:
        return "以萌宠动作引出人生大问题（当笛卡尔说'我思故我在'的时候，他一定没经历过周一早会）"
    
    def get_visual_base(self) -> str:
        return "萌宠高清素材 + 巨大彩色花字，重点词汇用emoji代替"
    
    def get_visual_rules(self) -> str:
        return """视觉：素材本身要萌、要高清。字幕使用巨大彩色花字，重点词汇用emoji代替，制造反差感。
镜头：Static camera, centered subject, 聚焦萌宠表情动作。
光影：Bright even lighting, minimal shadows, vibrant saturation。
色调：明亮通透，多巴胺配色，高饱和，色彩丰富。
参考：萌宠配音 + TikTok viral style + 表情包美学。"""
    
    def get_shot_keywords(self) -> str:
        return "Cute pet, Close-up, Colorful text, Emoji overlay, Bright lighting, High saturation, Viral style, TikTok aesthetic"
    
    def get_bgm_style(self) -> str:
        return "节奏感强的洗脑神曲或Phonk，音量20%，卡点剪辑"
