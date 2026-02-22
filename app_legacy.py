# -*- coding: utf-8 -*-
"""
VideoTaxi (VibeDrive) - AI短视频创作平台
开你的 VideoTaxi，在抖音公路上自由驰骋
VideoTaxi：让流量为你 7x24 小时跑单

重构后的主入口 - 采用视图层分离架构
"""

import streamlit as st
import os

# 导入服务层
from api_services import (
    get_hot_topics, 
    generate_script_by_style,
    refine_script_data,
    refine_script_by_chat
)
from video_engine import render_ai_video_pipeline
from db_manager import (
    init_db, get_or_create_user, check_in, deduct_credits,
    init_chat_db, init_script_versions_db, save_script_version, load_script_versions
)

# 导入视图层
from views import render_script_view, render_video_view, render_assets_view

# 页面配置
st.set_page_config(
    page_title="🚖 VideoTaxi - AI短视频创作平台",
    page_icon="🚖",
    layout="wide"
)


# ==================== 全局配置与初始化 ====================

def init_session_state():
    """初始化 Streamlit Session State"""
    # 工作流状态: draft -> locked -> producing -> completed
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = 'draft'
    
    # 用户数据
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'hot_topics' not in st.session_state:
        st.session_state.hot_topics = []
    if 'scenes_data' not in st.session_state:
        st.session_state.scenes_data = []
    if 'script_versions' not in st.session_state:
        st.session_state.script_versions = []
    if 'current_version_index' not in st.session_state:
        st.session_state.current_version_index = -1
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 创作配置
    if 'voice_id' not in st.session_state:
        st.session_state.voice_id = "zh-CN-YunxiNeural"
    if 'script_mode' not in st.session_state:
        st.session_state.script_mode = "🎭 认知重塑·破壁人"
    if 'model_id' not in st.session_state:
        st.session_state.model_id = "deepseek-chat"
    if 'model_cost' not in st.session_state:
        st.session_state.model_cost = 1


def load_api_keys():
    """从环境或 secrets 加载 API Keys
    
    支持两种格式：
    1. 扁平格式: TIANAPI_KEY, DEEPSEEK_KEY, ZHIPU_KEY, PEXELS_KEY
    2. 嵌套格式: tianapi.key, deepseek.key, zhipu.key, pexels.key
    """
    # 优先尝试扁平格式（Streamlit Cloud 常用）
    tianapi = st.secrets.get("TIANAPI_KEY", "")
    deepseek = st.secrets.get("DEEPSEEK_KEY", "")
    zhipu = st.secrets.get("ZHIPU_KEY", "")
    pexels = st.secrets.get("PEXELS_KEY", "")
    
    # 如果扁平格式为空，尝试嵌套格式
    if not tianapi and "tianapi" in st.secrets:
        tianapi = st.secrets.get("tianapi", {}).get("key", "")
    if not deepseek and "deepseek" in st.secrets:
        deepseek = st.secrets.get("deepseek", {}).get("key", "")
    if not zhipu and "zhipu" in st.secrets:
        zhipu = st.secrets.get("zhipu", {}).get("key", "")
    if not pexels and "pexels" in st.secrets:
        pexels = st.secrets.get("pexels", {}).get("key", "")
    
    return {
        'tianapi': tianapi,
        'deepseek': deepseek,
        'zhipu': zhipu,
        'pexels': pexels
    }


# ==================== 音色配置 ====================

VOICE_MAPPING = {
    "🎙️ 云希 (抖音热门)": "zh-CN-YunxiNeural",
    "🎙️ 晓晓 (温柔女声)": "zh-CN-XiaoxiaoNeural",
    "🎙️ 云野 (磁性男声)": "zh-CN-YunyeNeural",
    "🎙️ 晓伊 (活泼女声)": "zh-CN-XiaoyiNeural",
    "🔥 火山-温柔女声": "volc_lingcheng_wanqu",
    "🔥 火山-成熟男声": "volc_xinglin_chengshu",
    "🔥 火山-暴躁老哥": "volc_mingxuan_qingsu",
    "🔥 火山-甜美女声": "volc_yanping_tianmei",
    "🔥 火山-活力少年": "volc_yuanfeng_huoli"
}


# ==================== 侧边栏 ====================

def render_login_page():
    """渲染登录页面 - 居中显示醒目的 Logo 和标语"""
    # 使用空白占位让内容居中
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 大号 Logo 和标语
        st.markdown("""
        <div style="text-align: center; padding: 40px 30px; margin: 20px 0; 
                    border: 2px solid #FF3131; border-radius: 20px;
                    background: linear-gradient(135deg, rgba(255,49,49,0.1) 0%, rgba(13,17,23,0.95) 100%);">
            <div style="font-size: 80px; margin-bottom: 15px;">🚖</div>
            <div style="font-size: 48px; font-weight: 900; color: #FF3131; 
                        text-shadow: 0 0 30px rgba(255,49,49,0.5); 
                        margin-bottom: 15px; letter-spacing: 2px;">VIDEOTAXI</div>
            <div style="font-size: 20px; color: #fff; margin-bottom: 25px; 
                        letter-spacing: 3px; font-weight: 500;">在抖音公路上自由驰骋</div>
            <div style="background: linear-gradient(90deg, #FF3131 0%, #8b0000 100%); 
                        padding: 12px 25px; border-radius: 8px; display: inline-block;">
                <span style="color: white; font-size: 16px; font-weight: 700;">⚡ 7×24H 流量跑单中</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 登录输入框
        user_id = st.text_input(
            "👤 输入用户名开始创作",
            value=st.session_state.user_id,
            placeholder="请输入用户名",
            key="user_login_center"
        )
        
        if user_id:
            st.session_state.user_id = user_id
            st.rerun()
    
    return None


def render_sidebar(api_keys):
    """渲染侧边栏 - 品牌监控座舱（登录后显示）"""
    with st.sidebar:
        # ===== 品牌监控区：小型 Logo（登录后） =====
        st.markdown("""
        <div style="text-align: center; padding: 15px; margin-bottom: 15px; border: 1px solid #FF3131; border-radius: 10px;">
            <div style="font-size: 42px; margin-bottom: 5px;">🚖</div>
            <div style="font-size: 24px; font-weight: bold; color: #FF3131; margin-bottom: 5px;">VIDEOTAXI</div>
            <div style="font-size: 11px; color: #888; margin-bottom: 10px;">在抖音公路上自由驰骋</div>
            <div style="background: #FF3131; padding: 6px 10px; border-radius: 5px; display: inline-block;">
                <span style="color: white; font-size: 12px; font-weight: bold;">● 7×24H 流量跑单中</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # 显示当前用户
        user_id = st.session_state.user_id
        st.caption(f"👤 当前用户: {user_id}")
        
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.user_id = ""
            st.rerun()
        
        st.divider()
        
        if user_id:
            st.session_state.user_id = user_id
            user_info = get_or_create_user(user_id)
            
            # 加载历史版本
            if 'script_versions_loaded' not in st.session_state:
                st.session_state.script_versions = load_script_versions(user_id)
                st.session_state.current_version_index = len(st.session_state.script_versions) - 1 if st.session_state.script_versions else -1
                st.session_state.script_versions_loaded = True
            
            # 用户信息与签到
            col_cred, col_btn = st.columns([1, 1])
            with col_cred:
                # 积分显示带规则提示
                st.metric(
                    label="💎 积分", 
                    value=user_info["credits"], 
                    label_visibility="collapsed",
                    help="📋 积分规则：\n"
                         "• 基础签到：+5分/天\n"
                         "• 连续加成：每天额外+1分（封顶+10）\n"
                         "• 里程碑奖励：3天+3、7天+7、15天+15、30天+30\n"
                         "• 首次签到：额外+10分"
                )
            with col_btn:
                if st.button("📅 签到", use_container_width=True):
                    result = check_in(user_id)
                    success = result[0]
                    msg = result[1]
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.info(msg)
            
            # 显示历史版本数
            if st.session_state.script_versions:
                st.caption(f"📚 已保存 {len(st.session_state.script_versions)} 个剧本版本")
        else:
            st.warning("👈 请先登录")
            st.stop()
        
        st.divider()
        
        # 音色选择
        st.subheader("🎹️ 音色选择")
        current_voice_label = [k for k, v in VOICE_MAPPING.items() if v == st.session_state.voice_id][0]
        selected_voice = st.selectbox(
            "选择配音音色：",
            list(VOICE_MAPPING.keys()),
            index=list(VOICE_MAPPING.keys()).index(current_voice_label)
        )
        st.session_state.voice_id = VOICE_MAPPING[selected_voice]
        
        return user_id


# ==================== 主应用 ====================

def main():
    """主应用入口"""
    # 初始化
    init_session_state()
    init_db()
    init_chat_db()
    init_script_versions_db()
    
    # 加载 API Keys
    api_keys = load_api_keys()
        
    # 检查登录状态
    if not st.session_state.user_id:
        # 未登录 - 显示居中登录页面
        render_login_page()
        return
        
    # 已登录 - 渲染侧边栏和主内容
    user_id = render_sidebar(api_keys)
        
    # 主内容区 - 三态分离工作流（美化版）
    st.markdown("""
    <div style="border: 1px solid #FF3131; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
        <div style="font-size: 16px; font-weight: bold; color: #333; margin-bottom: 5px;">
            VideoTaxi 三态工作流
        </div>
        <div style="font-size: 12px; color: #666;">
            构思 → 生产 → 资产
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab 样式美化 - 使用更现代的标签设计
    tab_script, tab_video, tab_assets = st.tabs([
        "🔥 构思 · 写剧本", 
        "🎬 生产 · 渲染", 
        "📂 资产 · 管理"
    ])
    
    with tab_script:
        render_script_view(
            user_id=user_id,
            tianapi_key=api_keys['tianapi'],
            llm_api_key=api_keys['deepseek'],
            zhipu_api_key=api_keys['zhipu'],
            pexels_api_key=api_keys['pexels'],
            voice_mapping=VOICE_MAPPING,
            check_ssml_quality_func=check_ssml_quality,
            get_hot_topics_func=get_hot_topics,
            deduct_credits_func=deduct_credits,
            save_script_version_func=save_script_version,
            generate_script_by_style_func=generate_script_by_style,
            refine_script_data_func=refine_script_data,
            refine_script_by_chat_func=refine_script_by_chat,
            render_ai_video_pipeline_func=render_ai_video_pipeline
        )
    
    with tab_video:
        render_video_view()
    
    with tab_assets:
        render_assets_view()


def check_ssml_quality(scenes_data):
    """
    检查 SSML 情绪标注质量
    返回: (总分镜数, SSML标注数, Hook是否有SSML, 警告列表)
    """
    total = len(scenes_data)
    ssml_count = 0
    hook_has_ssml = False
    warnings = []
    
    for i, scene in enumerate(scenes_data):
        narration = scene.get('narration', '')
        has_ssml = '<prosody' in narration or '<emotion' in narration or '<break' in narration
        
        if has_ssml:
            ssml_count += 1
            if i == 0:
                hook_has_ssml = True
        else:
            if i == 0:
                warnings.append(f"❌ Hook（第1个分镜）缺少 SSML 情绪标注")
            else:
                warnings.append(f"⚠️ 分镜 {i+1} 缺少 SSML 情绪标注")
    
    return total, ssml_count, hook_has_ssml, warnings


if __name__ == "__main__":
    main()
