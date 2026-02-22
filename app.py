import streamlit as st
import os
from api_services import get_hot_topics, generate_script_json, generate_viral_script, refine_script_data
from video_engine import render_ai_video_pipeline
from db_manager import init_db, get_or_create_user, check_in, deduct_credits, get_user_credits
from chat_page import render_chat_page

# 启动时初始化数据库
init_db()

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
    3. **一键出片**：渲染过程约需2-3 分钟，请耐心等待。
    ---
    *注：建议分镜数量控制在4-6 个，以获得最佳画质。*
    """)

if 'hot_topics' not in st.session_state: st.session_state.hot_topics = []
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = []

with st.sidebar:
    st.header("👤 用户中心")
    
    # 1. 简易登录框
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    
    user_id = st.text_input("👤 请输入用户名登录：", value=st.session_state.user_id, placeholder="直接输入即可自动创建", key="user_login")
    
    if user_id:
        st.session_state.user_id = user_id
        # 获取用户信息
        user_info = get_or_create_user(user_id)
        st.success(f"👋 欢迎, {user_id}！")
        st.metric("📎 当前积分", user_info["credits"])
        
        # 2. 签到按钮
        if st.button("📅 每日签到领积分", use_container_width=True):
            success, msg = check_in(user_id)
            if success:
                st.success(msg)
                st.rerun()  # 刷新页面更新积分显示
            else:
                st.info(msg)
        
        st.divider()
    else:
        st.warning("👈 请先输入用户名登录")
        st.stop()
    
    st.header("⚙️ 核心引擎设置")
    
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
        
    st.divider()
        
    # 🧠 多模型选择器
    st.header("🧠 大语言模型")
        
    # 定义模型配置表：包含显示名称、真实调用ID、每次调用的基础积分消耗
    MODEL_CONFIG = {
        "🧠 DeepSeek (性价比/基础润色)": {"id": "deepseek-chat", "cost": 1},
        "🚀 GPT-4o (高智能/深度重写)": {"id": "gpt-4o", "cost": 5},
        "🎨 Claude 3.5 Sonnet (文笔极佳/创意发散)": {"id": "claude-3-5-sonnet-20240620", "cost": 4}
    }
        
    selected_model_label = st.selectbox(
        "请选择大语言模型：",
        list(MODEL_CONFIG.keys()),
        help="不同模型的智能程度和创作风格有所不同"
    )
        
    # 获取真实模型配置
    current_model_id = MODEL_CONFIG[selected_model_label]["id"]
    current_model_cost = MODEL_CONFIG[selected_model_label]["cost"]
        
    # 存储到 session_state 供后续使用
    st.session_state.model_id = current_model_id
    st.session_state.model_cost = current_model_cost
        
    st.info(f"💰 当前模型单次调用消耗: **{current_model_cost} 积分**")
        
    st.divider()
    
    # 🎯 页面模式切换
    st.header("🎯 创作模式")
    page_mode = st.radio(
        "选择你的创作方式：",
        ["📝 工作流模式", "💬 对话创作模式"],
        help="工作流：适合系统化创作 | 对话：自然聊天式创作",
        horizontal=True
    )
    
    # 存储选择到 session_state
    st.session_state.page_mode = page_mode
        
    st.divider()
        
    # 🎙️ 声音与情绪选择
    st.header("🎙️ 配音音色选择")
    
    # 将前端展示标签映射到后端具体的 Voice ID
    VOICE_MAPPING = {
        # Edge TTS (免费兜底)
        "标准男声 (免费/Edge)": "zh-CN-YunxiNeural",
        "标准女声 (免费/Edge)": "zh-CN-XiaoxiaoNeural",
        "温柔女声 (免费/Edge)": "zh-CN-XiaoyiNeural",
        
        # 火山引擎 (高阶情绪与特色音色 - 真实 ID)
        # 注意：volc_ 前缀用于后端路由识别，会自动脱去传递给火山 API
        "🍵 京腔侃爷 (火山)": "volc_zh_male_jingqiangkanye_moon_bigtts",
        "✨ 俊朗男友 (火山)": "volc_zh_male_junlangnanyou_emo_v2_mars_bigtts",
        "🎀 甜心小妹 (火山)": "volc_zh_female_tianxinxiaomei_emo_v2_mars_bigtts",
    }
    
    # 下拉框选择
    selected_voice_label = st.selectbox(
        "请选择配音音色与方言：", 
        list(VOICE_MAPPING.keys()),
        help="火山引擎音色支持方言和情绪表达，Edge TTS 免费但表现力有限"
    )
    
    # 获取对应的真实 ID 以便传递给引擎
    selected_voice_id = VOICE_MAPPING[selected_voice_label]
    
    # 存储到 session_state 供后续使用
    st.session_state.voice_id = selected_voice_id

# ==================== 页面模式判断 ====================
# 检查用户是否登录
if not st.session_state.get('user_id'):
    st.warning("⚠️ 请先在左侧侧边栏登录")
    st.stop()

# 根据用户选择渲染不同页面
if st.session_state.get('page_mode') == "💬 对话创作模式":
    # 对话创作页面
    render_chat_page(
        user_id=st.session_state.user_id,
        llm_api_key=st.secrets["DEEPSEEK_KEY"],
        model_id=st.session_state.model_id,
        model_cost=st.session_state.model_cost
    )
    st.stop()  # 停止后续的工作流逻辑

# ==================== 工作流模式 ====================

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
        
        # 👑 新增：画面提示词生成模式切换
        auto_image_mode = st.toggle("🤖 AI 自动生成画面分镜", value=True, help="关闭后，AI 将只写脚本文案，画面分镜由您手动输入")
        
        if script_mode == "🤖 标准 AI 导演":
            if st.button("🤖 呼叫 AI 导演写剧本", help="由 DeepSeek-V3 驱动，自动构思分镜与视觉指令"):
                if not llm_api_key: 
                    st.error("请配置 DeepSeek Key")
                else:
                    # 💰 积分扣除检查
                    model_cost = st.session_state.get('model_cost', 1)
                    if deduct_credits(user_id, model_cost):
                        with st.spinner(f"AI 导演构思中... (消耗 {model_cost} 积分)"):
                            st.session_state.scenes_data = generate_script_json(selected_topic, llm_api_key)
                        st.success(f"✅ 剧本生成成功！已扣除 {model_cost} 积分")
                        st.rerun()
                    else:
                        st.error(f"❌ 积分不足！当前操作需要 {model_cost} 积分。请明日签到或更换低消耗模型。")
        
        else:  # 爆款剧本大师模式
            if st.button("🔥 呼叫爆款剧本大师", help="顶尖爆款视频制作人 & 认知刺客，精通算法推流逻辑"):
                if not llm_api_key: st.error("请配置 DeepSeek Key")
                else:
                    with st.status("🎬 爆款剧本大师创作中...", expanded=True) as status:
                        st.write("📖 分析主题，选定心理学武器...")
                        st.write("🪝 构思黄金3秒Hook...")
                        st.write("✍️ 撰写高能量刺客文案...")
                        
                        if auto_image_mode:
                            st.write("🎥 自动生成导演级分镜提示词...")
                        else:
                            st.write("⏸️ 画面分镜留空，等待人类导演指示...")
                        
                        # 把前端的开关状态传给后台函数
                        viral_script = generate_viral_script(selected_topic, llm_api_key, auto_image_prompt=auto_image_mode)
                        
                        if viral_script:
                            st.session_state.scenes_data = viral_script
                            status.update(label="✅ 爆款剧本创作完成！", state="complete", expanded=False)
                        else:
                            status.update(label="❌ 创作失败", state="error")


with col2:
    st.subheader("✍️ 编导微调台")
    if st.session_state.scenes_data:
        st.caption("💡 提示：你可以双击单元格修改文案，或调整提示词以改变画风")
        
        # 必须将编辑后的数据存下来，这样精修时才能拿到用户手动改过的最新版本
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
        
        # 使用列布局，让"精修"和"渲染"按钮并排展示，提升UI体验
        col_refine, col_render = st.columns(2)
        
        with col_refine:
            if st.button("✨ 让大师精修剧本", use_container_width=True, help="清除废话，强化钩子，提升文案爆款率"):
                if not llm_api_key: 
                    st.error("请配置 DeepSeek Key")
                else:
                    with st.spinner("大师正在逐句毒舌批改中..."):
                        # 把用户目前编辑在表格里的最新数据传给精修函数
                        refined_data = refine_script_data(edited_scenes, llm_api_key)
                        if refined_data:
                            # 覆盖 session_state，并强制刷新页面重新渲染表格
                            st.session_state.scenes_data = refined_data
                            st.rerun() 
                            
        with col_render:
            if st.button("🚀 确认剧本，生成大片！", type="primary", use_container_width=True, help="渲染过程约需2-3 分钟"):
                if not zhipu_api_key: st.error("请配置智谱 Key！")
                else:
                    # 使用 st.status 展示实时进度
                    with st.status("🚀 视频引擎全力运转中...", expanded=True) as status:
                        st.write("🎨 智谱 AI 正在绘制高清分镜...")
                                
                        # 动态展示配音提示
                        selected_label = [k for k, v in VOICE_MAPPING.items() if v == st.session_state.voice_id][0]
                        if st.session_state.voice_id.startswith("volc_"):
                            st.write(f"🔥 火山引擎正在生成高表现力配音：{selected_label}")
                        else:
                            st.write(f"🎙️ Edge TTS 正在合成配音：{selected_label}")
                                
                        st.write("🎬 MoviePy 正在进行像素压制...")
                                
                        video_file = "ai_b_roll_output.mp4"
                        # 传递 voice_id 参数
                        success = render_ai_video_pipeline(
                            edited_scenes, 
                            zhipu_api_key, 
                            video_file, 
                            pexels_api_key,
                            voice_id=st.session_state.voice_id  # 关键：传递音色 ID
                        )
                                
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