# -*- coding: utf-8 -*-
"""
Cyber Theme Module - VideoTaxi 赛博驾驶舱UI系统
模块化隔离UI逻辑，实现一键换肤
确保所有中文字符正确显示
"""

import streamlit as st

def apply_cyber_theme():
    """
    VideoTaxi FSD (Full Self-Driving) 赛博驾驶舱主题
    拟物化 (Skeuomorphism) + 未来主义 (Futurism)
    碳素黑 + 刺客红的工业美学
    """
    st.markdown("""
    <style>
    /* ============================================
       1. 全局背景：深邃渐变
       ============================================ */
    .stApp {
        background: radial-gradient(circle at center, #1a1b25 0%, #050505 100%);
        color: #E6EDF3;
    }
    
    .main {
        background: transparent;
    }
    
    /* 移除顶部装饰线与边距优化 */
    header {visibility: hidden;}
    .main .block-container {padding-top: 1.5rem;}
    
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
