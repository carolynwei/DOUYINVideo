import streamlit as st
import os
from api_services import get_hot_topics, generate_script_json, generate_viral_script
from video_engine import render_ai_video_pipeline

st.set_page_config(page_title="AI 视觉视频引擎", page_icon="🎬", layout="wide")

# 🎨 CSS 样式注入 - 提升高级感
st.markdown("""
    <style>
    /* 让侧边栏更有层次感 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    /* 美化主标题 */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #FF0050; /* 抖音红 */
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    <h1 class="main-title">🎬 AI Video Engine</h1>
""", unsafe_allow_html=True)

# 💡 快速上手指南（折叠式）
with st.expander("💡 快速上手指南 (点此展开)"):
    st.markdown("""
    1. **选热点**：从左侧获取最新的抖音趋势。
    2. **AI 编剧**：点击生成脚本，你可以手动微调文案。
    3. **一键出片**：渲染过程约需 2-3 分钟，请耐心等待。
    ---
    *注：建议分镜数量控制在 4-6 个，以获得最佳画质。*
    """)

if 'hot_topics' not in st.session_state: st.session_state.hot_topics = []
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = []

with st.sidebar:
    st.header("⚙️ 引擎运行状态")
    
    # 🔑 自动从 secrets 读取，不再使用 st.text_input
    try:
        tianapi_key = st.secrets["TIANAPI_KEY"]
        llm_api_key = st.secrets["DEEPSEEK_KEY"]
        zhipu_api_key = st.secrets["ZHIPU_KEY"]
        pexels_api_key = st.secrets.get("PEXELS_KEY", "")
        
        st.success("✅ 密钥加载成功（已安全隐藏）")
    except Exception as e:
        st.error("❌ 密钥缺失：请在 Streamlit Cloud 后台配置 Secrets")
        st.stop()  # 如果没有密钥，停止后续运行

    st.info("💡 你的个人 API 密钥已通过 Streamlit Cloud 加密保护。")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📡 热点挖掘机")
    if st.button("刷新抖音热点 🔄", help="实时获取抖音最新热搜榜单"):
        with st.spinner("扫描中..."):
            st.session_state.hot_topics = get_hot_topics(tianapi_key)
            
    if st.session_state.hot_topics:
        selected_topic = st.selectbox("📌 选择目标：", st.session_state.hot_topics, help="从热搜榜单中选择一个话题")
        
        # 🎬 剧本生成模式选择
        script_mode = st.radio(
            "🎭 选择剧本风格：",
            ["🤖 标准 AI 导演", "🔥 爆款剧本大师"],
            help="标准模式：快速生成基础脚本 | 爆款模式：运用心理学+导演美学+高能量文案"
        )
        
        if script_mode == "🤖 标准 AI 导演":
            if st.button("🤖 呼叫 AI 导演写剧本", help="由 DeepSeek-V3 驱动，自动构思分镜与视觉指令"):
                if not llm_api_key: st.error("请配置 DeepSeek Key")
                else:
                    with st.spinner("AI 导演构思中..."):
                        st.session_state.scenes_data = generate_script_json(selected_topic, llm_api_key)
        
        else:  # 爆款剧本大师模式
            if st.button("🔥 呼叫爆款剧本大师", help="顶尖爆款视频制作人 & 认知刺客，精通算法推流逻辑"):
                if not llm_api_key: st.error("请配置 DeepSeek Key")
                else:
                    with st.status("🎬 爆款剧本大师创作中...", expanded=True) as status:
                        st.write("📖 分析主题，选定心理学武器...")
                        st.write("🪝 构思黄金3秒Hook...")
                        st.write("✍️ 撰写高能量刺客文案...")
                        st.write("🎥 生成导演级分镜提示词...")
                        
                        # 调用爆款剧本生成函数
                        viral_script = generate_viral_script(selected_topic, llm_api_key)
                        
                        if viral_script:
                            st.session_state.scenes_data = viral_script
                            status.update(label="✅ 爆款剧本创作完成！", state="complete", expanded=False)
                        else:
                            status.update(label="❌ 创作失败", state="error")

with col2:
    st.subheader("✍️ 编导微调台")
    if st.session_state.scenes_data:
        st.caption("💡 提示：你可以双击单元格修改文案，或调整提示词以改变画风")
        edited_scenes = st.data_editor(
            st.session_state.scenes_data,
            column_config={
                "narration": st.column_config.TextColumn("🎙️ 口播文案", width="medium"),
                "image_prompt": st.column_config.TextColumn("🎨 画面提示词", width="large"),
            },
            hide_index=True, 
            num_rows="dynamic"
        )
        
        st.markdown("---")
        if st.button("🚀 确认剧本，生成大片！", use_container_width=True, help="渲染过程约需 2-3 分钟"):
            if not zhipu_api_key: st.error("请配置智谱 Key！")
            else:
                # 使用 st.status 展示实时进度
                with st.status("🚀 视频引擎全力运转中...", expanded=True) as status:
                    st.write("🎨 智谱 AI 正在绘制高清分镜...")
                    st.write("🎙️ 微软神经网络正在合成配音...")
                    st.write("🎬 MoviePy 正在进行像素压制...")
                    
                    video_file = "ai_b_roll_output.mp4"
                    success = render_ai_video_pipeline(edited_scenes, zhipu_api_key, video_file, pexels_api_key)
                    
                    if success:
                        status.update(label="🎉 视频生成成功！", state="complete", expanded=False)
                        st.balloons()
                        # 核心修复：正确读取本地文件
                        with open(video_file, "rb") as file:
                            video_bytes = file.read()
                            st.video(video_bytes)
                            st.download_button("⬇️ 下载成片", data=video_bytes, file_name=f"{selected_topic}.mp4", mime="video/mp4", help="下载生成的视频文件")
                    else:
                        status.update(label="❌ 生成失败", state="error")