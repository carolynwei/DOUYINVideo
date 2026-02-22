# -*- coding: utf-8 -*-
"""
Hero Section 组件
VideoTaxi 品牌首屏视觉组件
"""

import streamlit as st


def hero_section():
    """
    渲染 VideoTaxi 首屏 Hero Section
    品牌视觉冲击力展示 - 使用原生 Streamlit 组件确保兼容性
    """
    # 使用原生 Streamlit 组件，避免 HTML 渲染问题
    
    # 主标题
    st.markdown("## 🚖 开你的 **VideoTaxi**")
    st.caption("在抖音公路上自由驰骋")
    
    # Slogan
    st.markdown("""
    <div style="
        background: rgba(255, 49, 49, 0.1);
        border: 1px solid rgba(255, 49, 49, 0.3);
        border-radius: 8px;
        padding: 15px 25px;
        text-align: center;
        margin: 20px 0;
    ">
        <span style="color: #FF3131; font-weight: 600;">🚖 让流量为你 7x24 小时跑单</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 统计数据 - 使用列布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="爆款风格", value="5")
    
    with col2:
        st.metric(label="智能编剧", value="AI")
    
    with col3:
        st.metric(label="一键成片", value="3min")
    
    st.divider()
