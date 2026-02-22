# -*- coding: utf-8 -*-
"""
VideoTaxi (VibeDrive) v2.0 - AI短视频创作平台
完全面向对象架构 - 新版主入口

架构层级:
- Entry: app_v2.py
- Services: UserService, ScriptService, VideoService
- Models: User, ScriptVersion, Scene
- Core: ConfigManager, AppState, API Clients
- OO Systems: styles/, voices/, workflow/
"""

import streamlit as st
import os

# ========== 新版面向对象架构导入 ==========
from core import ConfigManager, AppState, WorkflowState
from models import User, ScriptVersion, Scene
from services import UserService, ScriptService, VideoService
from styles import StyleFactory
from voices import VoiceFactory

# 页面配置
st.set_page_config(
    page_title="🚖 VideoTaxi v2.0 - AI短视频创作平台",
    page_icon="🚖",
    layout="wide"
)


# ==================== 全局配置与初始化 ====================

@st.cache_resource
def get_services():
    """获取服务实例（缓存）"""
    return {
        'user': UserService(),
        'script': ScriptService(),
        'video': VideoService()
    }

@st.cache_resource  
def get_config_manager():
    """获取配置管理器（缓存）"""
    return ConfigManager()

def init_app():
    """初始化应用"""
    # 初始化配置
    config_mgr = get_config_manager()
    config_mgr.load_from_secrets().load_from_env()
    
    # 初始化状态
    app_state = AppState()
    app_state.load_from_session()
    
    # 初始化Session State
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = WorkflowState.DRAFT.value
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'hot_topics' not in st.session_state:
        st.session_state.hot_topics = []
    if 'current_version' not in st.session_state:
        st.session_state.current_version = None
    if 'voice_id' not in st.session_state:
        st.session_state.voice_id = "zh-CN-YunxiNeural"
    if 'style_id' not in st.session_state:
        st.session_state.style_id = "cognitive_reshaper"


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

STYLE_MAPPING = {
    "🎭 认知重塑·破壁人": "cognitive_reshaper",
    "👁️ 观察者·上帝视角": "observer",
    "🌱 成长叙事·逆袭流": "growth",
    "💢 情绪共鸣·替你说": "emotion",
    "😂 梗图解构·玩梗王": "meme"
}


# ==================== 登录与侧边栏 ====================

def render_login_page():
    """渲染登录页面 - 居中显示"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 30px; margin: 20px 0; 
                    border: 2px solid #FF3131; border-radius: 20px;
                    background: linear-gradient(135deg, rgba(255,49,49,0.1) 0%, rgba(13,17,23,0.95) 100%);">
            <div style="font-size: 80px; margin-bottom: 15px;">🚖</div>
            <div style="font-size: 48px; font-weight: 900; color: #FF3131; 
                        text-shadow: 0 0 30px rgba(255,49,49,0.5); 
                        margin-bottom: 15px; letter-spacing: 2px;">VIDEOTAXI v2.0</div>
            <div style="font-size: 20px; color: #fff; margin-bottom: 25px; 
                        letter-spacing: 3px; font-weight: 500;">完全面向对象架构</div>
            <div style="background: linear-gradient(90deg, #FF3131 0%, #8b0000 100%); 
                        padding: 12px 25px; border-radius: 8px; display: inline-block;">
                <span style="color: white; font-size: 16px; font-weight: 700;">⚡ OO Architecture</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        user_id = st.text_input(
            "👤 输入用户名开始创作",
            value=st.session_state.user_id,
            placeholder="请输入用户名",
            key="user_login_center"
        )
        
        if user_id:
            st.session_state.user_id = user_id
            # 获取或创建用户
            services = get_services()
            user = services['user'].get_or_create_user(user_id)
            st.session_state.current_user = user
            st.rerun()
    
    return None


def render_sidebar():
    """渲染侧边栏"""
    services = get_services()
    
    with st.sidebar:
        # 品牌区
        st.markdown("""
        <div style="text-align: center; padding: 15px; margin-bottom: 15px; 
                    border: 1px solid #FF3131; border-radius: 10px;">
            <div style="font-size: 42px; margin-bottom: 5px;">🚖</div>
            <div style="font-size: 24px; font-weight: bold; color: #FF3131; 
                        margin-bottom: 5px;">VIDEOTAXI v2.0</div>
            <div style="font-size: 11px; color: #888;">完全面向对象架构</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # 用户信息
        user_id = st.session_state.user_id
        st.caption(f"👤 当前用户: {user_id}")
        
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.user_id = ""
            st.session_state.current_user = None
            st.rerun()
        
        st.divider()
        
        # 获取用户数据
        user = services['user'].get_or_create_user(user_id)
        st.session_state.current_user = user
        
        # 积分与签到
        col_cred, col_btn = st.columns([1, 1])
        with col_cred:
            st.metric(
                label="💎 积分", 
                value=user.credits,
                help="📋 积分规则：基础签到+5/天，连续加成，里程碑奖励"
            )
        with col_btn:
            if st.button("📅 签到", use_container_width=True):
                result = services['user'].check_in(user_id)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.info(result['message'])
        
        # 用户等级
        st.caption(f"🏆 等级: {user.level.value}")
        st.caption(f"📊 连续签到: {user.consecutive_days}天")
        
        st.divider()
        
        # 音色选择
        st.subheader("🎹️ 音色选择")
        current_voice = st.session_state.voice_id
        current_label = [k for k, v in VOICE_MAPPING.items() if v == current_voice][0] if current_voice in VOICE_MAPPING.values() else list(VOICE_MAPPING.keys())[0]
        
        selected_voice = st.selectbox(
            "选择配音音色：",
            list(VOICE_MAPPING.keys()),
            index=list(VOICE_MAPPING.keys()).index(current_label) if current_label in VOICE_MAPPING else 0
        )
        st.session_state.voice_id = VOICE_MAPPING[selected_voice]
        
        # 风格选择
        st.subheader("🎨 风格选择")
        current_style = st.session_state.style_id
        current_style_label = [k for k, v in STYLE_MAPPING.items() if v == current_style][0] if current_style in STYLE_MAPPING.values() else list(STYLE_MAPPING.keys())[0]
        
        selected_style = st.selectbox(
            "选择创作风格：",
            list(STYLE_MAPPING.keys()),
            index=list(STYLE_MAPPING.keys()).index(current_style_label) if current_style_label in STYLE_MAPPING else 0
        )
        st.session_state.style_id = STYLE_MAPPING[selected_style]
        
        return user


# ==================== 主内容区 ====================

def render_topic_section(script_service: ScriptService):
    """渲染选题区域"""
    st.subheader("🔥 热点选题")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 获取热点
        if st.button("🔄 获取抖音热点"):
            with st.spinner("获取热点中..."):
                topics = script_service.get_hot_topics()
                st.session_state.hot_topics = topics
        
        # 显示热点
        if st.session_state.hot_topics:
            selected_topic = st.selectbox(
                "选择热点话题：",
                st.session_state.hot_topics
            )
        else:
            selected_topic = ""
    
    with col2:
        # 自定义主题
        custom_topic = st.text_input("或输入自定义主题：")
    
    topic = custom_topic if custom_topic else selected_topic
    return topic


def render_script_section(script_service: ScriptService, user: User, topic: str):
    """渲染剧本生成区域"""
    st.subheader("📝 剧本生成")
    
    if not topic:
        st.info("👆 请先选择或输入主题")
        return
    
    # 检查积分
    services = get_services()
    cost = services['user'].get_operation_cost('script_generation')
    
    if user.credits < cost:
        st.error(f"❌ 积分不足，需要 {cost} 积分，当前 {user.credits} 积分")
        return
    
    if st.button(f"🚀 生成剧本 (消耗{cost}积分)", type="primary"):
        # 扣除积分
        deduct_result = services['user'].deduct_credits(user.user_id, cost, 'script_generation')
        if not deduct_result['success']:
            st.error(deduct_result['message'])
            return
        
        with st.spinner("AI正在创作剧本..."):
            result = script_service.generate_script(topic, st.session_state.style_id)
            
            if result['success']:
                # 创建剧本版本
                version = script_service.save_version(
                    user_id=user.user_id,
                    version_name=f"{topic[:20]}_{st.session_state.style_id}",
                    scenes=result['scenes'],
                    topic=topic,
                    style_id=st.session_state.style_id,
                    voice_id=st.session_state.voice_id
                )
                st.session_state.current_version = version
                st.success(f"✅ 剧本生成成功！版本ID: {version.id}")
                st.rerun()
            else:
                st.error(f"❌ 生成失败: {result['error']}")


def render_version_list(script_service: ScriptService, user: User):
    """渲染版本列表"""
    st.subheader("📚 我的剧本版本")
    
    versions = script_service.get_user_versions(user.user_id)
    
    if not versions:
        st.info("暂无保存的剧本版本")
        return
    
    for version in versions:
        with st.expander(f"{version.version_name} ({version.created_at[:10]})"):
            st.write(f"**主题**: {version.topic}")
            st.write(f"**风格**: {version.style_id}")
            st.write(f"**场景数**: {len(version.scenes)}")
            st.write(f"**总时长**: {version.get_total_duration():.1f}秒")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📖 查看", key=f"view_{version.id}"):
                    st.session_state.current_version = version
                    st.rerun()
            with col2:
                if st.button("🔒 锁定", key=f"lock_{version.id}"):
                    script_service.lock_version(version.id)
                    st.success("已锁定")
                    st.rerun()
            with col3:
                if st.button("🗑️ 删除", key=f"del_{version.id}"):
                    script_service.delete_version(version.id)
                    st.success("已删除")
                    st.rerun()


def render_current_version():
    """渲染当前版本详情"""
    version = st.session_state.get('current_version')
    if not version:
        return
    
    st.subheader(f"📖 当前剧本: {version.version_name}")
    
    for scene in version.scenes:
        with st.container():
            st.markdown(f"**场景 {scene.scene_number}** ({scene.duration:.1f}秒)")
            st.write(scene.content)
            if scene.image_prompt:
                st.caption(f"🎨 {scene.image_prompt[:100]}...")
            st.divider()


# ==================== 主应用 ====================

def main():
    """主应用入口"""
    # 初始化
    init_app()
    
    # 获取服务
    services = get_services()
    
    # 检查登录状态
    if not st.session_state.user_id:
        render_login_page()
        return
    
    # 渲染侧边栏
    user = render_sidebar()
    
    # 主内容区
    st.markdown("""
    <div style="border: 1px solid #FF3131; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
        <div style="font-size: 16px; font-weight: bold; color: #333;">
            VideoTaxi v2.0 - 完全面向对象架构
        </div>
        <div style="font-size: 12px; color: #666;">
            Models → Services → Views
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab 导航
    tab_script, tab_video, tab_assets = st.tabs([
        "🔥 构思 · 写剧本", 
        "🎬 生产 · 渲染", 
        "📂 资产 · 管理"
    ])
    
    with tab_script:
        # 选题区域
        topic = render_topic_section(services['script'])
        
        # 剧本生成
        render_script_section(services['script'], user, topic)
        
        # 当前版本
        render_current_version()
    
    with tab_video:
        st.subheader("🎬 视频渲染")
        version = st.session_state.get('current_version')
        
        if not version:
            st.info("👆 请先在'构思'Tab生成剧本")
        elif version.is_locked:
            st.info("🔒 剧本已锁定，可以渲染")
            
            # 检查积分
            cost = services['user'].get_operation_cost('video_generation')
            if user.credits < cost:
                st.error(f"❌ 积分不足，需要 {cost} 积分")
            else:
                if st.button(f"🎬 开始渲染 (消耗{cost}积分)", type="primary"):
                    # 扣除积分
                    deduct_result = services['user'].deduct_credits(user.user_id, cost, 'video_generation')
                    if deduct_result['success']:
                        # 渲染视频
                        with st.spinner("正在渲染视频..."):
                            result = services['video'].generate_complete_video(
                                version,
                                progress_callback=lambda step, prog, msg: st.write(f"{step}: {msg}")
                            )
                            
                            if result['success']:
                                st.success(f"✅ 视频渲染成功！")
                                st.video(result['video_path'])
                            else:
                                st.error(f"❌ 渲染失败: {result['error']}")
                    else:
                        st.error(deduct_result['message'])
        else:
            st.warning("⚠️ 请先锁定剧本版本后再渲染")
            if st.button("🔒 锁定当前版本"):
                services['script'].lock_version(version.id)
                version.is_locked = True
                st.success("版本已锁定")
                st.rerun()
    
    with tab_assets:
        # 版本列表
        render_version_list(services['script'], user)
        
        # 积分交易记录
        st.subheader("💎 积分明细")
        transactions = services['user'].get_credit_transactions(user.user_id, limit=10)
        if transactions:
            for t in transactions:
                emoji = "🟢" if t.amount > 0 else "🔴"
                st.caption(f"{emoji} {t.transaction_type.value}: {t.amount:+d} (余额: {t.balance_after})")
        else:
            st.info("暂无交易记录")


if __name__ == "__main__":
    main()
