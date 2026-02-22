# -*- coding: utf-8 -*-
"""
Cyber Theme Module - VideoTaxi 赛博驾驶舱UI系统
模块化隔离UI逻辑，实现一键换肤
确保所有中文字符正确显示
"""

import streamlit as st

def apply_cyber_theme():
    """
    VideoTaxi FSD (Full Self-Driving) 赛博驾驶舱主题 v2.0
    驾驶舱控制台风格 - 渐进式暴露设计
    碳素黑 + 刺客红的工业美学
    """
    st.markdown("""
    <style>
    /* ============================================
       0. 隐藏所有原生 Streamlit 组件
       ============================================ */
    header {visibility: hidden;}
    .main .block-container {padding: 0 !important; max-width: 100% !important;}
    .stDeployButton, .stStatus, [data-testid="stToolbar"] {display: none !important;}
    
    /* ============================================
       1. 全局背景：深邃渐变 + 扫描线效果
       ============================================ */
    .stApp {
        background: 
            linear-gradient(rgba(5, 5, 5, 0.97), rgba(5, 5, 5, 0.97)),
            radial-gradient(circle at 20% 50%, rgba(255, 49, 49, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 50%, rgba(255, 49, 49, 0.03) 0%, transparent 50%);
        color: #E6EDF3;
        font-family: 'SF Mono', 'Courier New', monospace;
    }
    
    /* 扫描线动画 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(255, 49, 49, 0.01) 2px,
            rgba(255, 49, 49, 0.01) 4px
        );
        pointer-events: none;
        z-index: 9999;
        animation: scanline 8s linear infinite;
    }
    
    @keyframes scanline {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
    }
    
    /* ============================================
       2. 拟物化卡片：毛玻璃+边缘微光
       ============================================ */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(22, 27, 34, 0.7) !important;
        border: 1px solid rgba(255, 49, 49, 0.15);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        transition: all 0.4s ease;
    }
    
    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: rgba(255, 49, 49, 0.35);
        box-shadow: 0 0 25px rgba(255, 49, 49, 0.15);
    }
    
    /* ============================================
       3. 按钮：引擎启动键风格
       ============================================ */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #FF3131;
        background-color: transparent;
        color: #FF3131;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'SF Mono', 'Courier New', monospace;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 49, 49, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        background-color: #FF3131;
        color: white;
        box-shadow: 0 0 25px rgba(255, 49, 49, 0.5), 0 0 50px rgba(255, 49, 49, 0.3);
        transform: translateY(-2px);
        border-color: #FF6161;
    }
    
    /* ============================================
       4. 输入框：命令行极客风
       ============================================ */
    .stTextInput input, 
    .stTextArea textarea,
    .stChatInput textarea {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #FF3131 !important;
        font-family: 'Courier New', monospace;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stChatInput textarea:focus {
        border-color: #FF3131 !important;
        box-shadow: 0 0 15px rgba(255, 49, 49, 0.3) !important;
        background: linear-gradient(90deg, #0d1117 0%, rgba(255, 49, 49, 0.05) 100%) !important;
    }
    
    /* ============================================
       5. 进度条：能量波纹效果
       ============================================ */
    .stProgress > div > div > div {
        background-image: linear-gradient(
            45deg, 
            #FF3131 25%, 
            #8b0000 25%, 
            #8b0000 50%, 
            #FF3131 50%, 
            #FF3131 75%, 
            #8b0000 75%, 
            #8b0000 100%
        );
        background-size: 40px 40px;
        animation: progress-move 1s linear infinite;
    }
    
    @keyframes progress-move {
        0% { background-position: 0 0; }
        100% { background-position: 40px 40px; }
    }
    
    /* ============================================
       6. Metric卡片：呼吸灯效果
       ============================================ */
    .stMetric {
        border-left: 3px solid #FF3131;
        padding-left: 15px;
        background: linear-gradient(90deg, rgba(255, 49, 49, 0.08) 0%, transparent 100%);
        border-radius: 8px;
        animation: metric-pulse 3s ease-in-out infinite;
    }
    
    @keyframes metric-pulse {
        0%, 100% { border-left-color: #FF3131; }
        50% { border-left-color: #FF6161; }
    }
    
    /* ============================================
       7. Tab切换：车载屏幕效果
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(13, 17, 23, 0.8);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #8b949e;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(255, 49, 49, 0.2) 0%, rgba(139, 0, 0, 0.1) 100%);
        border-color: #FF3131;
        color: #FF3131;
        box-shadow: 0 0 20px rgba(255, 49, 49, 0.3);
    }
    
    /* ============================================
       8. 侧边栏：驾驶员监控面板
       ============================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid rgba(255, 49, 49, 0.2);
    }
    
    [data-testid="stSidebar"] > div {
        background: transparent;
    }
    
    /* ============================================
       9. 数据卡片：3D效果
       ============================================ */
    .stImage, .stVideo {
        border-radius: 10px;
        border: 1px solid #30363d;
        overflow: hidden;
        transition: all 0.4s ease;
    }
    
    .stImage:hover, .stVideo:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 10px 40px rgba(255, 49, 49, 0.2);
        border-color: #FF3131;
    }
    
    /* ============================================
       10. 警告框：系统故障风格
       ============================================ */
    .stAlert {
        background: rgba(22, 27, 34, 0.9);
        border-left: 4px solid #FF3131;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
    }
    
    /* ============================================
       11. Expander：折叠面板
       ============================================ */
    .streamlit-expanderHeader {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #E6EDF3;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #FF3131;
        background: rgba(255, 49, 49, 0.05);
    }
    
    /* ============================================
       12. 滚动条：赛道风格
       ============================================ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0d1117;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #FF3131 0%, #8b0000 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FF3131;
    }
    
    /* ============================================
       13. 选择框：电子面板
       ============================================ */
    .stSelectbox > div > div {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #E6EDF3;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #FF3131;
    }
    
    /* ============================================
       14. Code块：硬核代码感
       ============================================ */
    code {
        color: #FF3131 !important;
        background: rgba(255, 49, 49, 0.1) !important;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'SF Mono', 'Courier New', monospace;
    }
    
    /* ============================================
       15. Status组件：任务执行状态
       ============================================ */
    [data-testid="stStatus"] {
        background: rgba(22, 27, 34, 0.9);
        border: 1px solid rgba(255, 49, 49, 0.2);
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_dashboard():
    """
    侧边栏：驾驶员实时监控面板
    """
    with st.sidebar:
        st.markdown("### 🚖 VideoTaxi FSD")
        st.caption("**System Status:** `ACTIVE (7x24h)`")
        st.divider()
        
        # 系统状态指示器
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔋 算力", "98%", delta="充足")
        with col2:
            st.metric("🌐 网络", "正常", delta="稳定")
        
        st.divider()
        
        # 快捷操作
        st.caption("**快捷操作**")
        if st.button("🔄 刷新任务", use_container_width=True, key="refresh_tasks"):
            st.rerun()
        
        if st.button("📊 查看日志", use_container_width=True, key="view_logs"):
            st.info("日志查看功能开发中...")
        
        st.divider()
        st.caption("💡 Powered by VideoTaxi Engine v2.0")


# ============================================
# 驾驶舱控制台组件 v2.0
# ============================================

def render_cockpit_header(title: str, subtitle: str = ""):
    """
    驾驶舱头部 - 极简品牌展示
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, rgba(255,49,49,0.1) 0%, transparent 100%);
        border-left: 3px solid #FF3131;
        padding: 15px 20px;
        margin: 0 0 20px 0;
    ">
        <h1 style="
            margin: 0;
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -1px;
        ">{title}</h1>
        {f'<p style="margin: 5px 0 0 0; color: #8b949e; font-size: 14px;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_status_panel(credits: int, next_run: str = "--:--"):
    """
    左侧状态监控面板 - 极简数字显示
    """
    st.markdown("""
    <div style="
        background: rgba(13, 17, 23, 0.8);
        border: 1px solid rgba(255, 49, 49, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
            <span style="color: #FF3131; font-size: 20px;">●</span>
            <span style="color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 2px;">System Online</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 积分显示 - 大数字风格
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div style="color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Credits</div>
            <div style="font-size: 48px; font-weight: 700; color: #FF3131; font-family: 'SF Mono', monospace;">{credits:03d}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 下次发车时间
    st.markdown(f"""
        <div>
            <div style="color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Next Run</div>
            <div style="font-size: 24px; font-weight: 600; color: #E6EDF3; font-family: 'SF Mono', monospace;">{next_run}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_mode_selector(current_mode: str, on_change=None):
    """
    模式选择器 - 大卡片式
    """
    modes = [
        ("构思", "CONCEPT", "创建新剧本"),
        ("生产", "PRODUCE", "渲染视频"),
        ("资产", "ASSETS", "历史记录")
    ]
    
    cols = st.columns(3)
    selected = current_mode
    
    for i, (label, code, desc) in enumerate(modes):
        is_active = current_mode == label
        with cols[i]:
            if st.button(
                f"**{label}**\n\n`{code}`\n\n{desc}",
                key=f"mode_{label}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                selected = label
                if on_change:
                    on_change(label)
    
    return selected


def render_concept_state(topic: str = "", on_generate=None):
    """
    构思态 - 极简输入界面
    """
    st.markdown("""
    <div style="
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 20px;
    ">
    """, unsafe_allow_html=True)
    
    # 巨大的输入框
    topic_input = st.text_input(
        "",
        value=topic,
        placeholder="输入你的创作主题...",
        key="concept_topic",
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # 5种风格大卡片
    styles = [
        ("🗡️", "认知刺客", "冲击+扎心"),
        ("👍", "听劝养成", "互动+蜕变"),
        ("🎬", "POV沉浸", "代入+共情"),
        ("🔥", "情绪宣泄", "爽感+反转"),
        ("🐱", "Meme抗象", "幽默+病毒")
    ]
    
    st.markdown("<div style='color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px;'>Select Style</div>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    selected_style = None
    
    for i, (emoji, name, tag) in enumerate(styles):
        with cols[i]:
            if st.button(
                f"{emoji}\n\n**{name}**\n\n<span style='font-size: 10px; color: #8b949e;'>{tag}</span>",
                key=f"style_{i}",
                use_container_width=True
            ):
                selected_style = name
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # 生成按钮
    if topic_input and st.button(
        "🚀 INITIATE CREATION",
        type="primary",
        use_container_width=True
    ):
        if on_generate:
            on_generate(topic_input, selected_style or "认知刺客")
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_producing_state(progress: float = 0, status_text: str = "Initializing..."):
    """
    生产态 - 全屏渲染监控器
    """
    st.markdown(f"""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(5, 5, 5, 0.98);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    ">
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #8b949e; letter-spacing: 4px; margin-bottom: 30px;">RENDERING</div>
            
            <!-- 进度环 -->
            <div style="
                width: 200px;
                height: 200px;
                border: 3px solid rgba(255, 49, 49, 0.2);
                border-radius: 50%;
                position: relative;
                margin: 0 auto 40px;
            ">
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 48px;
                    font-weight: 700;
                    color: #FF3131;
                    font-family: 'SF Mono', monospace;
                ">{int(progress * 100)}%</div>
            </div>
            
            <div style="color: #FF3131; font-size: 16px; letter-spacing: 2px;">{status_text}</div>
            
            <!-- 扫描线效果 -->
            <div style="
                width: 300px;
                height: 2px;
                background: linear-gradient(90deg, transparent, #FF3131, transparent);
                margin: 40px auto;
                animation: scan 2s linear infinite;
            "></div>
        </div>
    </div>
    
    <style>
    @keyframes scan {{
        0% {{ opacity: 0; transform: translateX(-100%); }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0; transform: translateX(100%); }}
    }}
    </style>
    """, unsafe_allow_html=True)


# 测试接口
if __name__ == "__main__":
    st.set_page_config(page_title="Cyber Theme Test", page_icon="🚖", layout="wide")
    
    # 应用主题
    apply_cyber_theme()
    render_sidebar_dashboard()
    
    # 测试内容
    st.title("🚖 VideoTaxi Cyber Theme")
    st.caption("赛博驾驶舱UI测试页面")
    
    tab1, tab2, tab3 = st.tabs(["🔥 任务简报", "🎥 生产流水线", "📂 我的车库"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("🎬 今日任务", "3", delta="+1")
        col2.metric("👁️ 总播放", "128K", delta="+23K")
        col3.metric("💰 预估收益", "¥856", delta="+152")
        
        st.subheader("当前任务")
        with st.status("正在生成视频...", expanded=True) as status:
            st.write("📝 生成剧本...")
            st.write("🎨 绘制分镜...")
            st.write("🎙️ 合成配音...")
            status.update(label="✅ 任务完成！", state="complete")
    
    with tab2:
        st.write("生产流水线内容")
    
    with tab3:
        st.write("我的车库内容")
