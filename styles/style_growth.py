# -*- coding: utf-8 -*-
"""
逆袭见证·养成系 风格
普通人的英雄之旅，让观众相信'努力真的有用'
"""

from .base_style import BaseStyle


class GrowthWitnessStyle(BaseStyle):
    """
    逆袭见证·养成系
    真诚、不完美但极其真诚。目标：普通人的英雄之旅，让观众相信'努力真的有用'。
    语言：口语化、求助式、充满感恩。
    """
    
    style_id = "growth_witness"
    style_name = "逆袭见证·养成系"
    style_emoji = "🚀"
    default_shot = "medium_shot"
    
    def get_tone(self) -> str:
        return """真诚、不完美但极其真诚。目标：普通人的英雄之旅，让观众相信'努力真的有用'。
语言：口语化、求助式、充满感恩。"""
    
    def get_hook_formula(self) -> str:
        return "以对比图开场，回应上期评论（家人们，上一期你们把我骂惨了...）"
    
    def get_visual_base(self) -> str:
        return "Casey Neistat Vlog风格，大量手持镜头，动作衔接处有特效转场"
    
    def get_visual_rules(self) -> str:
        return """视觉：Casey Neistat式Vlog风格，大量手持镜头，动作衔接处有特效转场。
镜头：Handheld camera, slightly shaky footage, over-the-shoulder shots。
光影：Natural lighting, golden hour warmth, 画面明亮。
色调：自然光，明亮通透，略带暖调。
参考：Casey Neistat Vlog + 真实生活记录。"""
    
    def get_shot_keywords(self) -> str:
        return "Casey Neistat style, vlog style, handheld, bright lighting, golden hour, authentic"
    
    def get_bgm_style(self) -> str:
        return "轻快、有节奏感的Lofi或Funk音乐，音量8%，营造轻松有趣的氛围"
