# -*- coding: utf-8 -*-
"""
ASSASSIN AI - 认知刺客创作平台
确保所有中文字符正确显示
"""

import streamlit as st
import os
from api_services import get_hot_topics, generate_script_json, generate_viral_script, refine_script_data
from video_engine import render_ai_video_pipeline
from db_manager import init_db, get_or_create_user, check_in, deduct_credits, get_user_credits, init_chat_db
from chat_page import render_chat_page

# 启动时初始化数据库
init_db()
init_chat_db()  # 初始化聊天记录表

st.set_page_config(page_title="🥷 ASSASSIN AI - 认知刺客创作平台", page_icon="🥷", layout="wide")

# 🎨 CSS 样式注入 - 工业电影感 + SaaS 级交互 + 主题切换
def inject_custom_css(theme='dark'):
    """
    根据主题动态注入 CSS 样式
    
    Args:
        theme: 'dark' 或 'light'
    """
    # 主题配色方案
    if theme == 'dark':
        # 深色模式：碳素黑 + 刺客红
        colors = {
            'bg_main': '#0A0A0B',
            'bg_secondary': '#161B22',
            'bg_sidebar': '#0d1117',
            'border': '#30363d',
            'text': '#E6EDF3',
            'text_secondary': '#8b949e',
            'accent': '#FF3131',
            'input_bg': '#0d1117',
            'chat_bg': '#0d1117'
        }
    else:
        # 浅色模式：白色 + 刺客红
        colors = {
            'bg_main': '#FFFFFF',
            'bg_secondary': '#F6F8FA',
            'bg_sidebar': '#F6F8FA',
            'border': '#D0D7DE',
            'text': '#24292F',
            'text_secondary': '#57606A',
            'accent': '#FF3131',
            'input_bg': '#FFFFFF',
            'chat_bg': '#F6F8FA'
        }
    
    st.markdown(f"""
    <style>
    /* 0. 全局背景和文字颜色 */
    .stApp {{
        background-color: {colors['bg_main']};
        color: {colors['text']};
    }}
    
    /* 主内容区域 */
    .main {{
        background-color: {colors['bg_main']};
        color: {colors['text']};
    }}
    
    /* 所有标题和段落 */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {colors['text']} !important;
    }}
    
    /* 1. 隐藏默认的顶部红线和多余边距 */
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 2rem;}}

    /* 2. 按钮悬浮发光效果 */
    .stButton>button {{
        width: 100%;
        border-radius: 5px;
        border: 1px solid {colors['accent']};
        background: transparent;
        color: {colors['accent']};
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background: {colors['accent']};
        color: white;
        box-shadow: 0 0 20px rgba(255, 49, 49, 0.4);
        transform: translateY(-2px);
    }}

    /* 3. 侧边栏卡片化 */
    [data-testid="stSidebar"] {{
        border-right: 1px solid {colors['border']};
        background-color: {colors['bg_sidebar']};
    }}
    
    /* 侧边栏内的文字 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{
        color: {colors['text']} !important;
    }}

    /* 4. 聊天气泡专业化 */
    [data-testid="stChatMessage"] {{
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 1rem;
        background-color: {colors['chat_bg']};
        margin-bottom: 0.5rem;
    }}
    
    /* 5. 表格专业化 */
    .stDataFrame {{
        border: 1px solid {colors['border']};
        border-radius: 8px;
    }}
    
    /* 表格内容颜色 */
    .stDataFrame table {{
        background-color: {colors['bg_secondary']};
        color: {colors['text']};
    }}
    
    /* 6. 输入框工业感 */
    .stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>div {{
        background-color: {colors['input_bg']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 5px;
        color: {colors['text']} !important;
    }}
    
    /* 输入框标签 */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label {{
        color: {colors['text']} !important;
    }}
    
    /* 7. Metric 卡片强化 */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: bold;
        color: {colors['accent']};
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {colors['text']} !important;
    }}
    
    /* 8. Tab 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 5px;
        padding: 10px 20px;
        background-color: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
        color: {colors['text']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {colors['accent']} !important;
        color: white !important;
    }}
    
    /* 9. 信息框样式 */
    .stAlert {{
        border-radius: 8px;
        border: 1px solid {colors['border']};
        background-color: {colors['bg_secondary']};
    }}
    
    /* 10. Expander 样式 */
    .streamlit-expanderHeader {{
        background-color: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
        color: {colors['text']} !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
    }}
    
    /* 11. Caption 文字 */
    .stCaption {{
        color: {colors['text_secondary']} !important;
    }}
    
    /* 12. Radio 按钮 */
    .stRadio>div {{
        background-color: {colors['bg_secondary']};
        border-radius: 5px;
        padding: 0.5rem;
    }}
    
    /* 13. Checkbox */
    .stCheckbox label {{
        color: {colors['text']} !important;
    }}
    
    /* 14. Toggle 开关 */
    .stToggle label {{
        color: {colors['text']} !important;
    }}
    
    /* 15. Divider 分割线 */
    hr {{
        border-color: {colors['border']};
    }}
    
    /* 16. 下拉框选项 */
    [data-baseweb="popover"] {{
        background-color: {colors['bg_secondary']} !important;
    }}
    
    [data-baseweb="select"] > div {{
        background-color: {colors['input_bg']} !important;
        border-color: {colors['border']} !important;
        color: {colors['text']} !important;
    }}
    
    /* 17. 数据编辑器 */
    .stDataEditor {{
        background-color: {colors['bg_secondary']};
    }}
    
    /* 18. 按钮primary类型 */
    .stButton>button[kind="primary"] {{
        background-color: {colors['accent']} !important;
        color: white !important;
        border: none !important;
    }}
    
    .stButton>button[kind="primary"]:hover {{
        background-color: #CC2828 !important;
        box-shadow: 0 0 25px rgba(255, 49, 49, 0.6);
    }}
    
    /* 19. Success/Error/Warning/Info 消息框 */
    .stSuccess, .stError, .stWarning, .stInfo {{
        border-radius: 8px;
        border: 1px solid {colors['border']};
    }}
    
    /* 20. Spinner 加载动画 */
    .stSpinner > div {{
        border-top-color: {colors['accent']} !important;
    }}
    
    /* 21. Progress Bar 进度条 */
    .stProgress > div > div {{
        background-color: {colors['accent']} !important;
    }}
    
    /* 22. Toast 消息 */
    [data-testid="stToast"] {{
        background-color: {colors['bg_secondary']} !important;
        border: 1px solid {colors['border']} !important;
        color: {colors['text']} !important;
    }}
    
    /* 23. Status 状态容器 */
    [data-testid="stStatus"] {{
        background-color: {colors['bg_secondary']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* 24. Code 代码块 */
    code {{
        background-color: {colors['bg_secondary']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']};
    }}
    
    /* 25. 数字输入框 */
    .stNumberInput input {{
        background-color: {colors['input_bg']} !important;
        border: 1px solid {colors['border']} !important;
        color: {colors['text']} !important;
    }}
    
    /* 26. Slider 滑块 */
    .stSlider {{
        color: {colors['text']} !important;
    }}
    
    /* 27. File Uploader 文件上传 */
    [data-testid="stFileUploader"] {{
        background-color: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
    }}
    
    /* 28. Download Button 下载按钮 */
    .stDownloadButton > button {{
        background-color: {colors['bg_secondary']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* 29. 侧边栏分割线 */
    [data-testid="stSidebar"] hr {{
        border-color: {colors['border']};
    }}
    
    /* 30. 侧边栏标题 */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {{
        color: {colors['text']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 初始化主题状态（在侧边栏之前）
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'dark'  # 默认深色模式

# 执行 CSS 注入（使用当前主题）
inject_custom_css(st.session_state.theme_mode)

# 💡 快速上手指南（折叠式）
with st.expander("💡 快速上手指南 (点此展开)"):
    st.markdown("""
    ### 🔥 爆款创作流程
    1. **选热点**：从左侧获取最新的抖音趋势
    2. **AI 编剧**：
       - 标准模式：快速生成，注入爆款基因
       - 爆款大师：深度运用心理学武器+认知刺客文案
    3. **精修剧本**：毒舌总监批改，提升文案能量密度
    4. **一键出片**：渲染过程约需2-3 分钟
    
    ### 🎯 爆款核心法则
    - ✅ 黄金前3秒：第一句必须强冲击（悬念/冲突/反常识）
    - ✅ 删除废话：不用“那么、其实”等连接词
    - ✅ 具体化表达：用动词/名词替换模糊形容词
    - ✅ 高密度钩子：每15秒一个记忆点
    ---
    *注：建议分镜数量控制在4-6 个，以获得最佳画质。*
    """)

if 'hot_topics' not in st.session_state: st.session_state.hot_topics = []
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = []

# 🎯 渐进式工作流状态管理
if 'script_versions' not in st.session_state: st.session_state.script_versions = []  # 版本历史
if 'current_version_index' not in st.session_state: st.session_state.current_version_index = -1  # -1表示无版本
if 'workflow_state' not in st.session_state: st.session_state.workflow_state = 'draft'  # draft → locked → producing → completed
if 'chat_history' not in st.session_state: st.session_state.chat_history = []  # 对话微调历史
if 'voice_id' not in st.session_state: st.session_state.voice_id = "zh-CN-YunxiNeural"

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
    
    # 🎨 主题切换
    st.header("🎨 界面主题")
    
    # 初始化主题状态
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'  # 默认深色模式
    
    # 主题切换按钮
    theme_options = {
        'dark': '🌙 深色模式',
        'light': '☀️ 浅色模式'
    }
    
    current_theme = st.session_state.theme_mode
    next_theme = 'light' if current_theme == 'dark' else 'dark'
    
    if st.button(f"切换至 {theme_options[next_theme]}", use_container_width=True, key="theme_toggle"):
        st.session_state.theme_mode = next_theme
        st.rerun()
    
    st.caption(f"当前：{theme_options[current_theme]}")
    st.divider()
    
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

# ==================== 🎭 Tab 工作台布局 ====================

tab_script, tab_video, tab_assets = st.tabs(["🔥 剧本构思", "🎬 影像工坊", "📂 历史资产"])

# ==================== Tab 1: 剧本构思 ====================
with tab_script:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📡 热点挖掘机")
        if st.button("刷新抖音热点 🔄", help="实时获取抖音最新热搜榜单"):
            with st.spinner("扫描中..."):
                st.session_state.hot_topics = get_hot_topics(tianapi_key)
                
        if st.session_state.hot_topics:
            selected_topic = st.selectbox("📌 选择目标：", st.session_state.hot_topics, help="从热搜榜单中选择一个话题")
        else:
            st.info("👉 点击上方按钮获取热点")
            selected_topic = st.text_input("或直接输入主题：", placeholder="例：内耗、裸辞、理财")
        
        # 🎭 剧本生成风格选择（全新升级）
        script_mode = st.radio(
            "🎭 选择剧本风格：",
            [
                "🗡️ 认知刺客流（冲击力+优越感）",
                "👍 听勝/养成系（互动率04+评论爆炸）",
                "🎬 POV沉浸流（第一人称+代入感）",
                "🔥 情绪宣泄流（极致反转+发疯文学）",
                "🐱 Meme抗象流（低成本+病毒传播）"
            ],
            help="选择不同的爆款风格，AI将自动适配创作策略"
        )
        
        # 💡 保存风格到 session_state，供视频渲染时使用
        st.session_state.script_mode = script_mode
                
        # 💡 风格详细说明 + 视觉预览
        style_descriptions = {
            "🗡️ 认知刺客流（冲击力+优越感）": {
                "icon": "🗡️",
                "desc": "摧毁旧认知，建立新真相。**核心：冲击+扎心+人间清醒**，让观众觉得自己变聪明了",
                "formula": "反常识结论 + 高频论点重击 + 不容置疑的口吞",
                "适配度": "极高（AI最擅长）",
                "visual": "🎬 镜头：中远景→特写 | 🎨 色调：冷色调+强对比 | 🎵 BGM：深沉鼓点",
                "reference": "Sam Kolder + Blade Runner 2049"
            },
            "👍 听勝/养成系（互动率04+评论爆炸）": {
                "icon": "👍",
                "desc": "把创作权交给评论区。**核心：真诚+反差+低姿态+蜕变**，满足观众养成欲",
                "formula": "“大家说我XX，我改了，你们看现在呢？”或“接受全网建议改稿的第X天”",
                "适配度": "中（需要多轮对话调整）",
                "visual": "🎬 镜头：手持摇晃Vlog | 🎨 色调：自然光+生活场景 | 🎵 BGM：温暖原声吉他",
                "reference": "Brandon Li + Casey Neistat"
            },
            "🎬 POV沉浸流（第一人称+代入感）": {
                "icon": "🎬",
                "desc": "让观众从旁观者变成当事人。**核心：代入感+压迫感+共情**",
                "formula": "“如果你是那个被老板骂了10分钟还不准下班的人……”",
                "适配度": "高（大量使用“你”，详细分镜）",
                "visual": "🎬 镜头：第一人称+超广角 | 🎨 色调：焦虑感氛围 | 🎵 BGM：心跳声+呼吸声",
                "reference": "POV 极限运动 + FPS 游戏视角"
            },
            "🔥 情绪宣泄流（极致反转+发疯文学）": {
                "icon": "🔥",
                "desc": "不讲理，只讲情。**核心：爽感+反转+极端对立**，提供即时的情绪出口",
                "formula": "短剧逻辑，前面有多憋屈，后面就有多爽。或用极其“发疯”的口吞说出不敢说的话",
                "适配度": "极高（配合火山TTS暴躁音色）",
                "visual": "🎬 镜头：极近特写+快速推拉 | 🎨 色调：高饱和+红黑撞色 | 🎵 BGM：崩坏电子乐",
                "reference": "Daniel Schiffer + Edgar Wright"
            },
            "🐱 Meme抗象流（低成本+病毒传播）": {
                "icon": "🐱",
                "desc": "用流行棗解说严肃内容。**核心：解压+洗脑+病毒式传播+幽默**",
                "formula": "用跳舞的猫、委屈的狗来演绎深刻道理，降低接收门槛",
                "适配度": "极高（不需要高清视频）",
                "visual": "🎬 镜头：固定机位+居中构图 | 🎨 色调：高饱和+多巴胺配色 | 🎵 BGM：洗脑神曲",
                "reference": "TikTok Meme + 表情包美学"
            }
        }
                
        # 显示当前选中风格的详情 + 视觉预览
        current_style = style_descriptions[script_mode]
        with st.expander(f"{current_style['icon']} 点击查看该风格详情", expanded=False):
            st.markdown(f"""
            **风格定位**：{current_style['desc']}
                    
            **爆款公式**：{current_style['formula']}
                    
            **AI适配度**：{current_style['适配度']}
            """)
                    
            # 🎬 视觉预览卡片
            st.markdown("---")
            st.markdown("🎬 **导演简报（视觉风格）**")
            st.info(f"""
            {current_style['visual']}
                    
            🎬 **参考风格**：{current_style['reference']}
                    
            💡 **AI绘画将自动应用上述视觉约束**，确保每一帧画面都带有该风格的灵魂。
            """)
        
        # 👑 新增：画面提示词生成模式切换
        auto_image_mode = st.toggle("🤖 AI 自动生成画面分镜", value=True, help="关闭后，AI 将只写脚本文案，画面分镜由您手动输入")
        
        # 🎬 统一的生成按钮（根据风格自动适配）
        button_labels = {
            "🗡️ 认知刺客流（冲击力+优越感）": "🗡️ 呢召认知刺客",
            "👍 听勝/养成系（互动率04+评论爆炸）": "👍 呢召听勝博主",
            "🎬 POV沉浸流（第一人称+代入感）": "🎬 呢召POV导演",
            "🔥 情绪宣泄流（极致反转+发疯文学）": "🔥 呢召情绪大师",
            "🐱 Meme抗象流（低成本+病毒传播）": "🐱 呢召Meme创作者"
        }
        
        if st.button(button_labels[script_mode], help=f"基于 {script_mode} 的策略生成剧本"):
            if not llm_api_key:
                st.error("请配置 DeepSeek Key")
            else:
                # 💰 积分扣除检查
                model_cost = st.session_state.get('model_cost', 1)
                if deduct_credits(user_id, model_cost):
                    with st.status(f"🎬 {script_mode} 创作中...", expanded=True) as status:
                        st.write("📋 分析主题，选定创作策略...")
                        st.write("🎭 构思风格化剧本结构...")
                        st.write("✍️ 撰写高能量文案...")
                        
                        if auto_image_mode:
                            st.write("🎥 自动生成风格化分镜提示词...")
                        
                        # 🔑 使用新的智能路由器（包含强制自检）
                        from api_services import generate_script_by_style
                        st.session_state.scenes_data = generate_script_by_style(
                            topic=selected_topic,
                            style=script_mode,
                            api_key=llm_api_key,
                            auto_image_prompt=auto_image_mode
                        )
                        
                        status.update(label=f"✅ {script_mode} 剧本创作完成！", state="complete")
                    st.success(f"✅ 剧本生成成功！已扣除 {model_cost} 积分")
                    # 🔥 自动转换状态为 draft，并清空聊天历史
                    st.session_state.workflow_state = 'draft'
                    st.session_state.chat_history = []
                    st.rerun()
                else:
                    st.error(f"❌ 积分不足！当前操作需要 {model_cost} 积分。请明日签到或更换低消耗模型。")

    with col2:
        st.subheader("✍️ 编导微调台")
            
        # 🎯 版本管理：显示历史版本切换下拉框
        if len(st.session_state.script_versions) > 0:
            st.caption(f"💾 已保存 {len(st.session_state.script_versions)} 个版本")
                
            # 构造版本选项列表
            version_options = []
            for i, ver in enumerate(st.session_state.script_versions):
                timestamp = ver.get('timestamp', '未知时间')
                version_options.append(f"📚 版本{i+1} ({timestamp})")
                
            # 版本切换下拉框
            selected_version_label = st.selectbox(
                "🔄 切换到历史版本：",
                version_options,
                index=st.session_state.current_version_index if st.session_state.current_version_index >= 0 else 0,
                help="查看之前锁定的版本"
            )
                
            # 获取选中的版本索引
            selected_version_index = version_options.index(selected_version_label)
                
            # 如果用户切换了版本，加载该版本的剧本
            if selected_version_index != st.session_state.current_version_index:
                st.session_state.current_version_index = selected_version_index
                st.session_state.scenes_data = st.session_state.script_versions[selected_version_index]['scenes']
                st.session_state.workflow_state = 'draft'  # 切换版本后重置为草稿状态
                st.rerun()
                
            st.markdown("---")
            
        # 显示剧本编辑器
        if st.session_state.scenes_data:
            # 🔒 根据状态决定是否禁用编辑
            is_locked = (st.session_state.workflow_state == 'locked')
                
            if is_locked:
                st.info("🔒 剧本已锁定，点击下方“🔓 解锁重新编辑”恢复修改")
            else:
                st.caption("💡 提示：你可以双击单元格修改文案，或调整提示词以改变画风")
                
            # 必须将编辑后的数据存下来
            edited_scenes = st.data_editor(
                st.session_state.scenes_data,
                column_config={
                    "narration": st.column_config.TextColumn("🎹️ 口播文案", width="medium"),
                    "image_prompt": st.column_config.TextColumn("🎨 画面提示词", width="large"),
                },
                hide_index=True, 
                num_rows="dynamic",
                disabled=is_locked,  # 🔒 锁定后禁用编辑
                key=f"data_editor_{st.session_state.workflow_state}"  # 使用动态key确保重新渲染
            )
            
            # 🔥 关键修复：实时同步编辑后的数据回 session_state
            # 这样删除、新增行的操作才能生效
            if not is_locked and edited_scenes != st.session_state.scenes_data:
                st.session_state.scenes_data = edited_scenes
                
            st.markdown("---")
                
            # 💬 对话微调模块（仅在 draft 状态下显示）
            if st.session_state.workflow_state == 'draft':
                with st.expander("💬 对话微调：用自然语言修改剧本", expanded=False):
                    st.caption("💡 例如：“第二段太平淡了，加点反转”、“开头更有冲击力”、“缩短到 30 秒”")
                        
                    # 聊天输入框
                    user_request = st.text_area(
                        "📝 你希望如何修改这个剧本？",
                        placeholder="例如：第二段太平淡了，加点反转",
                        height=100,
                        key="chat_input"
                    )
                        
                    if st.button("🤖 AI 微调", use_container_width=True, help="根据你的需求智能修改剧本"):
                        if not user_request.strip():
                            st.warning("请输入你的修改需求")
                        elif not llm_api_key:
                            st.error("请配置 DeepSeek Key")
                        else:
                            with st.spinner("🤖 AI 正在理解你的需求并修改剧本..."):
                                from api_services import refine_script_by_chat
                                refined_scenes = refine_script_by_chat(
                                    current_scenes=edited_scenes,
                                    user_request=user_request,
                                    api_key=llm_api_key
                                )
                                    
                                if refined_scenes:
                                    # 保存聊天历史
                                    st.session_state.chat_history.append({
                                        "request": user_request,
                                        "result": refined_scenes
                                    })
                                    # 更新剧本
                                    st.session_state.scenes_data = refined_scenes
                                    st.success("✅ 微调完成！")
                                    st.rerun()
                        
                    # 显示聊天历史
                    if len(st.session_state.chat_history) > 0:
                        st.caption(f"📜 已微调 {len(st.session_state.chat_history)} 次")
                        with st.expander("👁️ 查看聊天历史"):
                            for i, chat in enumerate(st.session_state.chat_history):
                                st.markdown(f"**第 {i+1} 轮修改**")
                                st.markdown(f"> 你说：{chat['request']}")
                                st.markdown("---")
                
            st.markdown("---")
                
            # 🎯 状态机：根据不同状态显示不同按钮
            if st.session_state.workflow_state == 'draft':
                # 草稿状态：显示"精修"和"锁定"按钮
                col_refine, col_lock = st.columns(2)
                    
                with col_refine:
                    if st.button("✨ 让大师精修剧本", use_container_width=True, help="清除废话，强化钩子，提升文案爆款率"):
                        if not llm_api_key: 
                            st.error("请配置 DeepSeek Key")
                        else:
                            with st.spinner("大师正在逐句毒舌批改中..."):
                                refined_data = refine_script_data(edited_scenes, llm_api_key)
                                if refined_data:
                                    st.session_state.scenes_data = refined_data
                                    st.rerun()
                    
                with col_lock:
                    if st.button("🔒 锁定剧本", type="primary", use_container_width=True, help="确认剧本，进入生产阶段"):
                        # 保存当前版本
                        from datetime import datetime
                        version = {
                            'version': len(st.session_state.script_versions) + 1,
                            'timestamp': datetime.now().strftime("%H:%M"),
                            'scenes': edited_scenes.copy()
                        }
                        st.session_state.script_versions.append(version)
                        st.session_state.current_version_index = len(st.session_state.script_versions) - 1
                            
                        # 转换状态为 locked
                        st.session_state.workflow_state = 'locked'
                        st.success("✅ 剧本已锁定！")
                        st.rerun()
                
            elif st.session_state.workflow_state == 'locked':
                # 锁定状态：显示"解锁"和"一键生产"按钮
                col_unlock, col_produce = st.columns(2)
                    
                with col_unlock:
                    if st.button("🔓 解锁重新编辑", use_container_width=True, help="解锁剧本，恢复编辑模式"):
                        st.session_state.workflow_state = 'draft'
                        st.info("✅ 已解锁，可以继续编辑")
                        st.rerun()
                    
                with col_produce:
                    if st.button("🚀 一键生产视频", type="primary", use_container_width=True, help="渲染过程约2-3 分钟"):
                        if not zhipu_api_key: 
                            st.error("请配置智谱 Key！")
                        else:
                            # 转换状态为 producing
                            st.session_state.workflow_state = 'producing'
                            st.rerun()
                
            elif st.session_state.workflow_state == 'producing':
                # 生产状态：执行视频生成
                # 🎯 高级设置折叠面板：显示推荐参数并支持覆盖
                with st.expander("🏛️ 高级设置：调整BGM/音色/画风", expanded=False):
                    st.caption("💡 系统已根据风格自动匹配以下参数，你可以手动覆盖：")
                        
                    # BGM 选择
                    st.markdown("**🎵 BGM 匹配**")
                    style_name = st.session_state.get('script_mode', '🗡️ 认知刺客流（冲击力+优越感）')
                    st.info(f"推荐：根据 {style_name} 风格自动匹配 BGM")
                    # 这里可以添加手动选择BGM的逻辑，但由于MVP版本，暂时省略
                        
                    st.markdown("---")
                        
                    # 音色选择
                    st.markdown("**🎹️ 音色选择**")
                    current_voice_label = [k for k, v in VOICE_MAPPING.items() if v == st.session_state.voice_id][0]
                    st.info(f"当前：{current_voice_label}")
                    st.caption("💡 可以在侧边栏中切换音色")
                        
                    st.markdown("---")
                        
                    # 画风预览
                    st.markdown("**🎨 画面风格**")
                    st.info("根据剧本中的 image_prompt 自动绘制")
                    
                # 使用 st.status 展示实时进度
                with st.status("🚀 视频引擎全力运转中...", expanded=True) as status:
                    st.write("🎨 智谱 AI 正在绘制高清分镜...")
                        
                    # 动态展示配音提示
                    selected_label = [k for k, v in VOICE_MAPPING.items() if v == st.session_state.voice_id][0]
                    if st.session_state.voice_id.startswith("volc_"):
                        st.write(f"🔥 火山引擎正在生成高表现力配音：{selected_label}")
                    else:
                        st.write(f"🎹️ Edge TTS 正在合成配音：{selected_label}")
                        
                    st.write("🎬 MoviePy 正在进行像素压制...")
                        
                    video_file = "ai_b_roll_output.mp4"
                    # 传递 voice_id 和 style_name 参数
                    success = render_ai_video_pipeline(
                        edited_scenes, 
                        zhipu_api_key, 
                        video_file, 
                        pexels_api_key,
                        voice_id=st.session_state.voice_id,
                        style_name=st.session_state.get('script_mode')
                    )
                        
                    if success:
                        status.update(label="🎉 视频生成成功！", state="complete", expanded=False)
                        st.balloons()
                            
                        # 转换状态为 completed
                        st.session_state.workflow_state = 'completed'
                            
                        # 读取视频文件
                        with open(video_file, "rb") as file:
                            video_bytes = file.read()
                            st.video(video_bytes)
                            st.download_button(
                                "⬇️ 下载成片", 
                                data=video_bytes, 
                                file_name=f"{st.session_state.get('selected_topic', 'video')}.mp4", 
                                mime="video/mp4", 
                                help="下载生成的视频文件"
                            )
                    else:
                        status.update(label="❌ 生成失败", state="error")
                        # 重置状态为 locked
                        st.session_state.workflow_state = 'locked'
                
            elif st.session_state.workflow_state == 'completed':
                # 完成状态：显示重新创作按钮
                st.success("🎉 视频已生成完成！")
                if st.button("🆕 创作下一个视频", type="primary", use_container_width=True):
                    # 重置状态
                    st.session_state.workflow_state = 'draft'
                    st.session_state.scenes_data = []
                    st.session_state.chat_history = []
                    st.rerun()

# ==================== Tab 2: 影像工坊 ====================
with tab_video:
    st.info("🎬 **影像工坊**：生成的视频预览和素材下载将显示在这里")
    
    # 如果有已生成的视频，展示
    if st.session_state.scenes_data:
        st.markdown("### 🎬 分镜预览")
        st.caption("💡 展示当前剧本的分镜结构")
        
        # 分镜预览卡片化布局
        num_scenes = len(st.session_state.scenes_data)
        cols_per_row = 3
        
        for i in range(0, num_scenes, cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < num_scenes:
                    scene = st.session_state.scenes_data[idx]
                    with col:
                        # 用占位图模拟分镜
                        st.image("https://via.placeholder.com/300x533/1a1a1a/FF3131?text=Scene+" + str(idx+1), 
                                caption=f"🎬 分镜 {idx+1}")
                        with st.expander("📝 查看文案"):
                            # 🔥 修复：确保 narration 是字符串类型
                            narration = scene.get('narration', '')
                            if narration and isinstance(narration, str):
                                preview = narration[:50] + "..." if len(narration) > 50 else narration
                                st.write(preview)
                            else:
                                st.write("⚠️ 暂无文案")
    else:
        st.warning("👉 请先在【剧本构思】Tab 生成剧本")

# ==================== Tab 3: 历史资产 ====================
with tab_assets:
    st.info("📂 **你的云端创作库**")
    st.markdown("""
    ### 📊 创作统计
    - 总视频数：**0** （功能开发中）
    - 总播放量：**0**
    -热门作品：暂无
    
    ---
    
    ### 💾 历史项目
    🚧 此功能正在开发中...
    
    将来你可以在这里：
    - 查看所有历史创作的视频
    - 重新编辑历史剧本
    - 分享到社交媒体
    - 导出剧本为PDF
    """)