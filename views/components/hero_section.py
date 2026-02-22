# -*- coding: utf-8 -*-
"""
Hero Section 组件
VideoTaxi 品牌首屏视觉组件
"""

import streamlit as st


def hero_section():
    """
    渲染 VideoTaxi 首屏 Hero Section
    品牌视觉冲击力展示
    """
    st.markdown("""
    <style>
    .hero-container {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 40px 30px;
        margin: 20px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF3131, #FF6B35, #FF3131);
        background-size: 200% 100%;
        animation: gradient-flow 3s ease infinite;
    }
    
    @keyframes gradient-flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 10px 0;
        letter-spacing: -1px;
    }
    
    .main-title .highlight {
        background: linear-gradient(135deg, #FF3131 0%, #FF6B35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        font-size: 18px;
        color: #8b949e;
        margin: 0 0 30px 0;
        font-weight: 400;
    }
    
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-top: 30px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        color: #FF3131;
        display: block;
    }
    
    .stat-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .slogan {
        margin-top: 25px;
        padding: 15px 25px;
        background: rgba(255, 49, 49, 0.1);
        border: 1px solid rgba(255, 49, 49, 0.3);
        border-radius: 8px;
        display: inline-block;
    }
    
    .slogan-text {
        font-size: 16px;
        color: #FF3131;
        font-weight: 600;
        margin: 0;
    }
    </style>
    
    <div class="hero-container">
        <h1 class="main-title">开你的 <span class="highlight">VideoTaxi</span></h1>
        <p class="subtitle">在抖音公路上自由驰骋</p>
        
        <div class="slogan">
            <p class="slogan-text">🚖 让流量为你 7x24 小时跑单</p>
        </div>
        
        <div class="stats-row">
            <div class="stat-item">
                <span class="stat-number">5</span>
                <span class="stat-label">爆款风格</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">AI</span>
                <span class="stat-label">智能编剧</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">3min</span>
                <span class="stat-label">一键成片</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
