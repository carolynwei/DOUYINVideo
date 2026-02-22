# -*- coding: utf-8 -*-
"""
情绪过山车·发疯艺术家 风格
替观众发疯，提供心理代偿
"""

from .base_style import BaseStyle


class EmotionalRollercoasterStyle(BaseStyle):
    """
    情绪过山车·发疯艺术家
    极端、艺术感、戏剧化。目标：替观众发疯，提供心理代偿。
    语言：情绪波动剧烈，用极度夸张的方式演出内心戏。
    """
    
    style_id = "emotional_rollercoaster"
    style_name = "情绪过山车·发疯艺术家"
    style_emoji = "🤯"
    default_shot = "extreme_close_up"
    
    def get_tone(self) -> str:
        return """极端、艺术感、戏剧化。目标：替观众发疯，提供心理代偿。
语言：情绪波动剧烈，用极度夸张的方式演出内心戏。"""
    
    def get_hook_formula(self) -> str:
        return "以面无表情但内心怒吼开场（那一刻，在我的BGM里，他已经死了100次）"
    
    def get_visual_base(self) -> str:
        return "《王牌特工》教堂戏 + 《妈的多重宇宙》，红黑撞色，极快剪辑节奏"
    
    def get_visual_rules(self) -> str:
        return """视觉：红黑撞色，极快的剪辑节奏，使用升格和快放结合。幻想世界与现实形成强烈对比。
镜头：Extreme close-up, rapid zoom, shaky cam, quick cuts, Dutch angles。
光影：High contrast, dramatic shadows, saturated colors, red and black palette。
色调：高饱和度，幻想部分鲜艳，现实部分 desaturated。
参考：《王牌特工》教堂戏 + 《妈的多重宇宙》+ Edgar Wright快速剪辑。"""
    
    def get_shot_keywords(self) -> str:
        return "Kingsman church scene style, Everything Everywhere All At Once, red and black, high contrast, fantasy vs reality, rapid cuts"
    
    def get_bgm_style(self) -> str:
        return "前半段压抑无声，进入幻想后爆发出史诗级交响乐或重低音电子乐，音量30%"
