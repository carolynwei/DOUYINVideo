# -*- coding: utf-8 -*-
"""
VideoTaxi Cockpit v2.0 - 驾驶舱控制台

设计理念：
- 渐进式暴露：根据任务态显示不同界面
- 单窗口操作：构思态/生产态/资产态 三态分离
- 赛博发光：统一的视觉规范
"""

import streamlit as st
from cyber_theme import (
    apply_cyber_theme,
    render_cockpit_header,
    render_status_panel,
    render_mode_selector,
    render_concept_state,
    render_producing_state
)

# 页面配置
st.set_page_config(
    page_title="🚖 VideoTaxi Cockpit",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 应用赛博主题
apply_cyber_theme()

# ==================== Session State 初始化 ====================
if 'cockpit_mode' not in st.session_state:
    st.session_state.cockpit_mode = "构思"  # 构思 / 生产 / 资产
if 'user_credits' not in st.session_state:
    st.session_state.user_credits = 20
if 'is_producing' not in st.session_state:
    st.session_state.is_producing = False
if 'production_progress' not in st.session_state:
    st.session_state.production_progress = 0.0

# ==================== 驾驶舱布局 ====================

# 顶部极简品牌栏
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    st.markdown("""
    <div style="padding: 15px;">
        <span style="font-size: 24px; font-weight: 800; color: #FF3131;">🚖 VideoTaxi</span>
        <span style="font-size: 10px; color: #8b949e; display: block;">FSD COCKPIT v2.0</span>
    </div>
    """, unsafe_allow_html=True)

with col_center:
    # 模式选择器
    new_mode = render_mode_selector(st.session_state.cockpit_mode)
    if new_mode != st.session_state.cockpit_mode:
        st.session_state.cockpit_mode = new_mode
        st.rerun()

with col_right:
    # 状态面板
    render_status_panel(
        credits=st.session_state.user_credits,
        next_run="04:00"
    )

st.markdown("<hr style='border: none; height: 1px; background: rgba(255,49,49,0.2); margin: 0;'>", unsafe_allow_html=True)

# ==================== 主内容区 - 根据模式切换 ====================

if st.session_state.cockpit_mode == "构思":
    # 构思态：极简输入界面
    render_concept_state(
        on_generate=lambda topic, style: start_production(topic, style)
    )

elif st.session_state.cockpit_mode == "生产":
    # 生产态：全屏渲染监控器
    if st.session_state.is_producing:
        render_producing_state(
            progress=st.session_state.production_progress,
            status_text="Generating video frames..."
        )
    else:
        # 等待开始生产
        st.markdown("""
        <div style="text-align: center; padding: 100px 20px;">
            <div style="font-size: 48px; margin-bottom: 20px;">🎬</div>
            <div style="font-size: 24px; color: #E6EDF3; margin-bottom: 10px;">Ready to Produce</div>
            <div style="color: #8b949e;">剧本已锁定，点击开始渲染</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ START RENDERING", type="primary", use_container_width=True):
            st.session_state.is_producing = True
            st.rerun()

elif st.session_state.cockpit_mode == "资产":
    # 资产态：侧滑抽屉风格
    st.markdown("""
    <div style="padding: 40px 20px;">
        <h2 style="color: #E6EDF3; margin-bottom: 30px;">📂 Asset Library</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 历史版本列表
    if st.session_state.get('script_versions'):
        for version in reversed(st.session_state.script_versions[-5:]):
            with st.expander(f"Version {version.get('version', '?')} - {version.get('timestamp', 'Unknown')}"):
                scenes = version.get('scenes', [])
                st.caption(f"{len(scenes)} scenes")
                if st.button("Restore", key=f"restore_{version.get('version')}"):
                    st.session_state.scenes_data = scenes
                    st.success("Restored!")
    else:
        st.info("No assets yet. Start creating!")

# ==================== 函数定义 ====================

def start_production(topic: str, style: str):
    """开始生产流程"""
    st.session_state.selected_topic = topic
    st.session_state.selected_style = style
    st.session_state.cockpit_mode = "生产"
    st.session_state.is_producing = True
    st.session_state.production_progress = 0.0
    st.rerun()

# ==================== 生产进度模拟 ====================
if st.session_state.is_producing:
    import time
    
    # 模拟进度增长
    if st.session_state.production_progress < 1.0:
        st.session_state.production_progress += 0.1
        time.sleep(0.5)
        st.rerun()
    else:
        # 生产完成
        st.session_state.is_producing = False
        st.session_state.cockpit_mode = "资产"
        st.balloons()
        st.success("✅ Video generated successfully!")
