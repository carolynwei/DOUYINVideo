# -*- coding: utf-8 -*-
"""
治愈系·观察者 风格
诗意、温暖、神性视角观察人间冷暖
"""

from .base_style import BaseStyle


class HealingObserverStyle(BaseStyle):
    """
    治愈系·观察者
    诗意、温暖、神性视角。目标：赋予观众'上帝/猫咪/路灯'的视角观察人间冷暖，
    发现平凡生活中的微光。语言：内心独白式，温柔而细腻。
    """
    
    style_id = "healing_observer"
    style_name = "治愈系·观察者"
    style_emoji = "🎬"
    default_shot = "low_angle"
    
    def get_tone(self) -> str:
        return """诗意、温暖、神性视角。目标：赋予观众'上帝/猫咪/路灯'的视角观察人间冷暖，
发现平凡生活中的微光。语言：内心独白式，温柔而细腻。"""
    
    def get_hook_formula(self) -> str:
        return "以非人类视角开场，建立独特观察角度（我是便利店的那盏灯，今晚我看到...）"
    
    def get_visual_base(self) -> str:
        return "是枝裕和 + 《三分野》风格，青橙色调降低饱和度，增加颗粒感"
    
    def get_visual_rules(self) -> str:
        return """视觉：低角度拍摄（模拟动物/物体视角），或隔着玻璃、水渍拍摄，营造电影质感。
镜头：固定镜头为主，低机位，偶尔透过雨滴/玻璃拍摄增加朦胧感。
光影：柔和自然光，城市夜景灯光，营造温暖孤独感。
色调：青橙色调但降低饱和度，增加颗粒感，电影质感。
参考：是枝裕和 + 《三分野》+ 治愈系摄影。"""
    
    def get_shot_keywords(self) -> str:
        return "Low angle shot, Through glass, Rain drops, Teal and orange muted, Film grain, Cinematic, Warm lighting"
    
    def get_bgm_style(self) -> str:
        return "舒缓钢琴曲+雨声白噪音，音量12%，人声清晰"
