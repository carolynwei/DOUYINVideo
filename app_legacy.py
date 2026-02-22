# -*- coding: utf-8 -*-
"""
VideoTaxi (VibeDrive) - AI短视频创作平台
开你的 VideoTaxi，在抖音公路上自由驰骋
VideoTaxi：让流量为你 7x24 小时跑单

【路由中心化架构】
- app.py: 仅负责页面配置、主题初始化、Tab路由
- views/: 各Tab的UI渲染逻辑
- core/: 状态管理和工作流引擎
"""

import streamlit as st
from cyber_theme import apply_cyber_theme
from db_manager import init_db, init_chat_db, init_script_versions_db
from chat_page import render_chat_page

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🚖 VideoTaxi - AI短视频创作平台",
    page_icon="🚖",
    layout="wide"
)

# ==================== 主题初始化 ====================
apply_cyber_theme()

# ==================== 数据库初始化 ====================
init_db()
init_chat_db()
init_script_versions_db()

# ==================== Session State 初始化 ====================
def init_session_state():
    """初始化所有 Session State 变量"""
    # 工作流状态: draft → locked → producing → completed
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = 'draft'
    
    # 用户数据
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'page_mode' not in st.session_state:
        st.session_state.page_mode = "📝 工作流模式"
    
    # 创作数据
    if 'scenes_data' not in st.session_state:
        st.session_state.scenes_data = []
    if 'script_versions' not in st.session_state:
        st.session_state.script_versions = []
    if 'current_version_index' not in st.session_state:
        st.session_state.current_version_index = -1
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 配置数据
    if 'voice_id' not in st.session_state:
        st.session_state.voice_id = "zh-CN-YunxiNeural"
    if 'model_id' not in st.session_state:
        st.session_state.model_id = "deepseek-chat"
    if 'model_cost' not in st.session_state:
        st.session_state.model_cost = 1
    if 'script_mode' not in st.session_state:
        st.session_state.script_mode = "🗡️ 认知刺客流（冲击力+优越感）"
    
    # 热点数据
    if 'hot_topics' not in st.session_state:
        st.session_state.hot_topics = []
    if 'navigator' not in st.session_state:
        st.session_state.navigator = None
    if 'missions' not in st.session_state:
        st.session_state.missions = []
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = ""
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = ""

init_session_state()

# ==================== 侧边栏渲染 ====================
from views.sidebar_view import render_sidebar

user_authenticated = render_sidebar()

# ==================== 页面路由 ====================

# 1. 检查用户登录
if not user_authenticated:
    st.warning("⚠️ 请先在左侧侧边栏登录")
    st.stop()

# 2. 对话创作模式路由
if st.session_state.get('page_mode') == "💬 对话创作模式":
    render_chat_page(
        user_id=st.session_state.user_id,
        llm_api_key=st.secrets["DEEPSEEK_KEY"],
        model_id=st.session_state.model_id,
        model_cost=st.session_state.model_cost
    )
    st.stop()

# 3. 工作流模式 - Tab 路由
from views.script_view import render_script_tab
from views.factory_view import render_factory_tab
from views.assets_view import render_assets_tab

tab_script, tab_video, tab_assets = st.tabs(["🔥 剧本构思", "🎬 影像工坊", "📂 历史资产"])

with tab_script:
    render_script_tab()

with tab_video:
    render_factory_tab()

with tab_assets:
    render_assets_tab()
