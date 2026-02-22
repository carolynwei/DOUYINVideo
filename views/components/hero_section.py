# -*- coding: utf-8 -*-
"""
Hero Section 组件
VideoTaxi 品牌首屏视觉组件
"""

import streamlit as st


def hero_section():
    """
    渲染 VideoTaxi 首屏 Hero Section
    品牌视觉冲击力展示 - 赛博朋克科技风格
    """
    # 赛博风格标题区
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(255,49,49,0.15) 0%, rgba(0,0,0,0) 50%, rgba(255,107,53,0.1) 100%);
        border: 1px solid rgba(255,49,49,0.3);
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #FF3131, #FF6B35, #FF3131);
            background-size: 200% 100%;
            animation: pulse 2s ease infinite;
        "></div>
        <h1 style="
            margin: 0 0 10px 0;
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #FF3131 0%, #FF6B35 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        ">🚖 VideoTaxi</h1>
        <p style="
            margin: 15px 0 0 0;
            font-size: 20px;
            color: #ffffff;
            font-weight: 600;
            text-shadow: 0 0 20px rgba(255,49,49,0.5);
            letter-spacing: 2px;
        ">在抖音公路上自由驰骋</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心数据指标 - 科技感卡片
    st.markdown("""
    <div style="display: flex; justify-content: space-between; gap: 15px; margin: 25px 0;">
        <div style="
            flex: 1;
            background: rgba(255,49,49,0.08);
            border: 1px solid rgba(255,49,49,0.2);
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
        ">
            <div style="font-size: 32px; font-weight: 700; color: #FF3131;">5</div>
            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">爆款风格引擎</div>
        </div>
        <div style="
            flex: 1;
            background: rgba(255,49,49,0.08);
            border: 1px solid rgba(255,49,49,0.2);
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
        ">
            <div style="font-size: 32px; font-weight: 700; color: #FF3131;">GPT-4</div>
            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">深度编剧模型</div>
        </div>
        <div style="
            flex: 1;
            background: rgba(255,49,49,0.08);
            border: 1px solid rgba(255,49,49,0.2);
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
        ">
            <div style="font-size: 32px; font-weight: 700; color: #FF3131;">180s</div>
            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px;">全自动成片</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心 Slogan
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, rgba(255,49,49,0.15) 0%, rgba(255,107,53,0.1) 50%, rgba(255,49,49,0.15) 100%);
        border: 1px solid rgba(255,49,49,0.25);
        border-radius: 10px;
        padding: 18px 25px;
        text-align: center;
        margin: 20px 0;
        position: relative;
    ">
        <div style="
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #FF3131;
            font-size: 20px;
        ">⚡</div>
        <span style="color: #FF3131; font-weight: 700; font-size: 15px; letter-spacing: 1px;">
            7×24 小时自动跑单 · 流量永动机
        </span>
        <div style="
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #FF3131;
            font-size: 20px;
        ">⚡</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
