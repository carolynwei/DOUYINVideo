import streamlit as st
import os
from api_services import get_hot_topics, generate_script_json
from video_engine import render_ai_video_pipeline

st.set_page_config(page_title="AI 视觉视频引擎", page_icon="🎬", layout="wide")
st.title("🎬 爆款视频全自动流水线")

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
    if st.button("刷新抖音热点 🔄"):
        with st.spinner("扫描中..."):
            st.session_state.hot_topics = get_hot_topics(tianapi_key)
            
    if st.session_state.hot_topics:
        selected_topic = st.selectbox("📌 选择目标：", st.session_state.hot_topics)
        if st.button("🤖 呼叫 AI 导演写剧本"):
            if not llm_api_key: st.error("请配置 DeepSeek Key")
            else:
                with st.spinner("AI 导演构思中..."):
                    st.session_state.scenes_data = generate_script_json(selected_topic, llm_api_key)

with col2:
    st.subheader("✍️ 编导微调台")
    if st.session_state.scenes_data:
        edited_scenes = st.data_editor(
            st.session_state.scenes_data,
            column_config={
                "narration": st.column_config.TextColumn("🎙️ 口播文案", width="medium"),
                "image_prompt": st.column_config.TextColumn("🎨 画面提示词", width="large"),
            },
            hide_index=True, num_rows="dynamic"
        )
        
        st.markdown("---")
        if st.button("🚀 确认剧本，生成大片！", use_container_width=True):
            if not zhipu_api_key: st.error("请配置智谱 Key！")
            else:
                with st.spinner("流水线全面启动，预计2-3分钟..."):
                    video_file = "ai_b_roll_output.mp4"
                    success = render_ai_video_pipeline(edited_scenes, zhipu_api_key, video_file, pexels_api_key)
                    
                    if success:
                        st.balloons()
                        st.success("🎉 大片生成完毕！")
                        # 核心修复：正确读取本地文件
                        with open(video_file, "rb") as file:
                            video_bytes = file.read()
                            st.video(video_bytes)
                            st.download_button("⬇️ 下载成片", data=video_bytes, file_name=f"{selected_topic}.mp4", mime="video/mp4")