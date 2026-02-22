# -*- coding: utf-8 -*-
"""
剧本构思视图 (Script View)
负责剧本生成、编辑、锁定等工作流前端界面
"""

import streamlit as st
from datetime import datetime

# 风格配置数据 - 5大升级版爆款风格
STYLE_OPTIONS = [
    "🎬 治愈系·观察者",
    "🎭 认知重塑·破壁人",
    "🚀 逆袭见证·养成系",
    "🤯 情绪过山车·发疯艺术家",
    "🐕 萌即正义·哲学大师"
]

STYLE_DESCRIPTIONS = {
    "🎬 治愈系·观察者": {
        "icon": "🎬",
        "desc": "微小善意+神性视角。赋予观众'上帝/猫咪/路灯'的视角观察人间冷暖，发现平凡生活中的微光，让观众在快节奏中感到被治愈、被理解。",
        "formula": "（视角主体）不明白，为什么那个总是加班的人，今天会在路边哭... / 如果【城市名】的路灯会说话，它一定听过最多的秘密。",
        "适配度": "极高（独特视角，情感共鸣强）",
        "visual": "镜头：低角度拍摄（猫的视角），或隔着玻璃、水渍拍摄 | 色调：青橙色调但降低饱和度，增加颗粒感，营造电影质感 | BGM：舒缓钢琴曲+雨声白噪音，音量12%",
        "reference": "是枝裕和 + 《三分野》"
    },
    "🎭 认知重塑·破壁人": {
        "icon": "🎭",
        "desc": "打破信息茧房+提供新希望。保留冲击力但去掉优越感戾气，不是为了显得观众笨，而是告诉观众'你本可以更好，只是信息被屏蔽了'。",
        "formula": "关于【某某事】，媒体不敢说的真相反转... / 停止内耗！原来【负面情绪】可以用物理学/生物学解释。",
        "适配度": "极高（正能量传播）",
        "visual": "镜头：极简背景，人物位于画面中心，语速稍快 | 色调：关键数据/词汇用巨大的红字直接砸在屏幕上 | BGM：深沉、带有科技感的电子乐，鼓点清晰，音量15%",
        "reference": "Sam Kolder 剪辑节奏"
    },
    "🚀 逆袭见证·养成系": {
        "icon": "🚀",
        "desc": "普通人的英雄之旅+集体荣誉感。把评论区当成'智囊团'，把账号当成真人秀实验场。正能量来自于'努力真的有用'。",
        "formula": "挑战用30天，在网友的监督下成为【某领域大神】，今天是第X天... / 听劝！全网最听劝的博主又来交作业了！",
        "适配度": "高（深度粉丝关系）",
        "visual": "镜头：Casey Neistat式Vlog风格，大量手持镜头，动作衔接处有特效转场 | 色调：画面明亮，自然光优先 | BGM：轻快、有节奏感的Lofi或Funk音乐，音量8%",
        "reference": "Casey Neistat Vlog"
    },
    "🤯 情绪过山车·发疯艺术家": {
        "icon": "🤯",
        "desc": "替观众发疯+极致戏剧反差。用极度夸张和风格化的方式，演出观众内心不敢演的戏。正能量在于心理代偿。",
        "formula": "当我在会议上被老板当众羞辱，我是如何用眼神杀死他的（内心戏版）... / 给所有【某种讨厌的人】的一封'感谢信'。",
        "适配度": "极高（情绪宣泄）",
        "visual": "镜头：红黑撞色，极快的剪辑节奏，使用升格和快放结合 | 色调：高饱和度，幻想世界与现实形成强烈对比 | BGM：前半段压抑无声，进入幻想后爆发出史诗级交响乐，音量30%",
        "reference": "《王牌特工》教堂戏 + 《妈的多重宇宙》"
    },
    "🐕 萌即正义·哲学大师": {
        "icon": "🐕",
        "desc": "用最软的脸，说最硬的道理。用萌宠/动画形象作为'嘴替'，解构严肃话题。正能量来自于举重若轻的智慧。",
        "formula": "画面是猫猫在舔爪子，配音是烟嗓大叔：'关于那个不给你涨薪的老板，我的建议是...用他的头皮屑腌酸菜。'",
        "适配度": "极高（病毒传播）",
        "visual": "镜头：素材本身要萌、要高清 | 色调：字幕使用巨大彩色花字，重点词汇用emoji代替 | BGM：节奏感强的洗脑神曲或Phonk，音量20%，卡点剪辑",
        "reference": "萌宠配音 + 脑干缺失的美"
    }
}

BUTTON_LABELS = {
    "🎬 治愈系·观察者": "🎬 召唤治愈之眼",
    "🎭 认知重塑·破壁人": "🎭 召唤破壁先锋",
    "🚀 逆袭见证·养成系": "🚀 召唤逆袭见证官",
    "🤯 情绪过山车·发疯艺术家": "🤯 召唤发疯艺术家",
    "🐕 萌即正义·哲学大师": "🐕 召唤萌系哲学家"
}


def render_script_view(
    user_id: str,
    tianapi_key: str,
    llm_api_key: str,
    zhipu_api_key: str,
    pexels_api_key: str,
    voice_mapping: dict,
    check_ssml_quality_func,
    get_hot_topics_func,
    deduct_credits_func,
    save_script_version_func,
    generate_script_by_style_func,
    refine_script_data_func,
    refine_script_by_chat_func,
    render_ai_video_pipeline_func
):
    """
    渲染剧本构思 Tab 的完整界面
    
    Args:
        user_id: 当前用户ID
        tianapi_key: 天行API密钥
        llm_api_key: DeepSeek API密钥
        zhipu_api_key: 智谱API密钥
        pexels_api_key: Pexels API密钥
        voice_mapping: 音色映射字典
        check_ssml_quality_func: SSML质量检查函数
        get_hot_topics_func: 获取热点函数
        deduct_credits_func: 扣除积分函数
        save_script_version_func: 保存剧本版本函数
        generate_script_by_style_func: 按风格生成剧本函数
        refine_script_data_func: 精修剧本函数
        refine_script_by_chat_func: 对话微调剧本函数
        render_ai_video_pipeline_func: 视频渲染函数
    """
    # 🎬 工作流状态指示器
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, rgba(255,49,49,0.2) 0%, rgba(255,49,49,0.05) 100%);
        border-left: 4px solid #FF3131;
        padding: 12px 16px;
        margin-bottom: 20px;
        border-radius: 0 8px 8px 0;
    ">
        <div style="font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 2px;">
            当前阶段: STEP 1/3
        </div>
        <div style="font-size: 18px; font-weight: 700; color: #FF3131; margin-top: 4px;">
            🔥 构思态 — 创意发散
        </div>
        <div style="font-size: 13px; color: #8b949e; margin-top: 4px;">
            写剧本 → 锁定剧本 → 进入影像工坊渲染
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 工作流进度条
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.progress(33, text="构思")
    with col2:
        st.progress(0, text="生产")
    with col3:
        st.progress(0, text="资产")
    
    # 使用标签页组织内容
    script_tab1, script_tab2 = st.tabs(["🎯 快速创作", "⚙️ 高级设置"])
    
    with script_tab1:
        _render_creation_panel(
            user_id, tianapi_key, llm_api_key, zhipu_api_key, pexels_api_key,
            voice_mapping, get_hot_topics_func, deduct_credits_func,
            generate_script_by_style_func, render_ai_video_pipeline_func
        )
    
    with script_tab2:
        _render_advanced_settings(voice_mapping)
    
    # 编导微调台（全宽显示）
    _render_editor_panel(
        user_id, llm_api_key, zhipu_api_key, pexels_api_key,
        voice_mapping, check_ssml_quality_func, deduct_credits_func,
        save_script_version_func, refine_script_data_func, refine_script_by_chat_func,
        render_ai_video_pipeline_func
    )


def _render_creation_panel(
    user_id, tianapi_key, llm_api_key, zhipu_api_key, pexels_api_key,
    voice_mapping, get_hot_topics_func, deduct_credits_func,
    generate_script_by_style_func, render_ai_video_pipeline_func
):
    """渲染创作面板（主题输入 + 风格选择 + 生成按钮）"""
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📌 创作主题")
        
        # 主题输入
        default_topic = st.session_state.get('selected_topic', '')
        
        selected_topic = st.text_input(
            "输入视频主题：",
            value=default_topic,
            placeholder="例如：35岁程序员裸辞、职场内耗...",
            help="输入你想创作的视频主题，AI将自动生成剧本"
        )
        
        if st.button("🔄 获取抖音热点", use_container_width=True):
            with st.spinner("扫描中..."):
                st.session_state.hot_topics = get_hot_topics_func(tianapi_key)
                st.rerun()
        
        # 显示热点下拉（如果有）
        if st.session_state.hot_topics:
            selected_topic = st.selectbox(
                "或选择热点：",
                [""] + st.session_state.hot_topics,
                index=0
            )
    
    # 🎭 剧本生成风格选择
    default_style = st.session_state.get('selected_style', STYLE_OPTIONS[0])
    default_style_index = STYLE_OPTIONS.index(default_style) if default_style in STYLE_OPTIONS else 0
    
    script_mode = st.radio(
        "🎭 选择剧本风格：",
        STYLE_OPTIONS,
        index=default_style_index,
        help="选择不同的爆款风格，AI将自动适配创作策略"
    )
    
    # 保存风格到 session_state
    st.session_state.script_mode = script_mode
    
    # 显示风格详情
    _render_style_details(script_mode)
    
    # 画面提示词生成模式切换
    auto_image_mode = st.toggle(
        "🤖 AI 自动生成画面分镜",
        value=True,
        help="关闭后，AI 将只写脚本文案，画面分镜由您手动输入"
    )
    
    # 生成按钮
    if st.button(BUTTON_LABELS[script_mode], help=f"基于 {script_mode} 的策略生成剧本"):
        _handle_script_generation(
            user_id, selected_topic, script_mode, auto_image_mode,
            llm_api_key, deduct_credits_func, generate_script_by_style_func
        )


def _render_style_details(script_mode: str):
    """渲染风格详情展开面板"""
    current_style = STYLE_DESCRIPTIONS[script_mode]
    with st.expander(f"{current_style['icon']} 点击查看该风格详情", expanded=False):
        st.markdown(f"""
        **风格定位**：{current_style['desc']}
        
        **爆款公式**：{current_style['formula']}
        
        **AI适配度**：{current_style['适配度']}
        """)
        
        st.markdown("---")
        st.markdown("🎬 **导演简报（视觉风格）**")
        st.info(f"""
        {current_style['visual']}
        
        🎬 **参考风格**：{current_style['reference']}
        
        💡 **AI绘画将自动应用上述视觉约束**，确保每一帧画面都带有该风格的灵魂。
        """)


def _handle_script_generation(
    user_id, selected_topic, script_mode, auto_image_mode,
    llm_api_key, deduct_credits_func, generate_script_by_style_func
):
    """处理剧本生成逻辑"""
    if not llm_api_key:
        st.error("请配置 DeepSeek Key")
        return
    
    # 积分扣除检查
    model_cost = st.session_state.get('model_cost', 1)
    if not deduct_credits_func(user_id, model_cost):
        st.error(f"❌ 积分不足！当前操作需要 {model_cost} 积分。请明日签到或更换低消耗模型。")
        return
    
    with st.status(f"🎬 {script_mode} 创作中...", expanded=True) as status:
        st.write("📋 分析主题，选定创作策略...")
        st.write("🎭 构思风格化剧本结构...")
        st.write("✍️ 撰写高能量文案...")
        
        if auto_image_mode:
            st.write("🎥 自动生成风格化分镜提示词...")
        
        # 使用智能路由器生成剧本
        st.session_state.scenes_data = generate_script_by_style_func(
            topic=selected_topic,
            style=script_mode,
            api_key=llm_api_key,
            auto_image_prompt=auto_image_mode
        )
        
        status.update(label=f"✅ {script_mode} 剧本创作完成！", state="complete")
    
    st.success(f"✅ 剧本生成成功！已扣除 {model_cost} 积分")
    # 转换状态为 draft，并清空聊天历史
    st.session_state.workflow_state = 'draft'
    st.session_state.chat_history = []
    st.rerun()


def _render_advanced_settings(voice_mapping: dict):
    """渲染高级设置面板"""
    st.subheader("⚙️ 高级创作参数")
    
    st.markdown("### 🎭 模型选择")
    st.caption("💡 不同模型影响生成质量和积分消耗")
    
    model_options = {
        "🚀 DeepSeek-V3 (默认)": ("deepseek-chat", 1),
        "🧠 DeepSeek-R1 (推理增强)": ("deepseek-reasoner", 2),
        "⚡ DeepSeek-V2.5 (快速)": ("deepseek-v2.5", 1)
    }
    
    selected_model = st.radio(
        "选择大模型：",
        list(model_options.keys()),
        index=0,
        help="R1模型推理能力更强，但消耗2倍积分"
    )
    
    model_id, model_cost = model_options[selected_model]
    st.session_state.model_id = model_id
    st.session_state.model_cost = model_cost
    
    st.info(f"当前选择：{selected_model} | 消耗积分：{model_cost}")
    
    st.markdown("---")
    st.markdown("### 🎹️ 音色预览")
    
    current_voice = st.session_state.get('voice_id', 'zh-CN-YunxiNeural')
    voice_label = [k for k, v in voice_mapping.items() if v == current_voice][0]
    st.success(f"当前音色：{voice_label}")
    st.caption("💡 可以在侧边栏切换更多音色选项")


def _render_editor_panel(
    user_id, llm_api_key, zhipu_api_key, pexels_api_key,
    voice_mapping, check_ssml_quality_func, deduct_credits_func,
    save_script_version_func, refine_script_data_func, refine_script_by_chat_func,
    render_ai_video_pipeline_func
):
    """渲染编导微调台（剧本编辑器）"""
    st.markdown("---")
    st.subheader("✍️ 编导微调台")
    
    # 版本管理
    _render_version_manager()
    
    # 剧本编辑器
    if st.session_state.scenes_data:
        _render_script_editor(
            user_id, llm_api_key, zhipu_api_key, pexels_api_key,
            voice_mapping, check_ssml_quality_func, deduct_credits_func,
            save_script_version_func, refine_script_data_func, refine_script_by_chat_func,
            render_ai_video_pipeline_func
        )


def _render_version_manager():
    """渲染版本管理器"""
    if len(st.session_state.script_versions) > 0:
        st.caption(f"💾 已保存 {len(st.session_state.script_versions)} 个版本")
        
        version_options = [
            f"📚 版本{i+1} ({ver.get('timestamp', '未知时间')})"
            for i, ver in enumerate(st.session_state.script_versions)
        ]
        
        selected_version_label = st.selectbox(
            "🔄 切换到历史版本：",
            version_options,
            index=st.session_state.current_version_index if st.session_state.current_version_index >= 0 else 0,
            help="查看之前锁定的版本"
        )
        
        selected_version_index = version_options.index(selected_version_label)
        
        if selected_version_index != st.session_state.current_version_index:
            st.session_state.current_version_index = selected_version_index
            st.session_state.scenes_data = st.session_state.script_versions[selected_version_index]['scenes']
            st.session_state.workflow_state = 'draft'
            st.rerun()
        
        st.markdown("---")


def _render_script_editor(
    user_id, llm_api_key, zhipu_api_key, pexels_api_key,
    voice_mapping, check_ssml_quality_func, deduct_credits_func,
    save_script_version_func, refine_script_data_func, refine_script_by_chat_func,
    render_ai_video_pipeline_func
):
    """渲染剧本编辑器主体"""
    is_locked = (st.session_state.workflow_state == 'locked')
    
    if is_locked:
        st.info("🔒 剧本已锁定，点击下方'🔓 解锁重新编辑'恢复修改")
    else:
        st.caption("💡 提示：你可以双击单元格修改文案，或调整提示词以改变画风")
    
    # 数据编辑器
    edited_scenes = st.data_editor(
        st.session_state.scenes_data,
        column_config={
            "narration": st.column_config.TextColumn("🎹️ 口播文案", width="medium"),
            "image_prompt": st.column_config.TextColumn("🎨 画面提示词", width="large"),
        },
        hide_index=True,
        num_rows="dynamic",
        disabled=is_locked,
        key=f"data_editor_{st.session_state.workflow_state}"
    )
    
    # 实时同步编辑数据
    if not is_locked and edited_scenes != st.session_state.scenes_data:
        st.session_state.scenes_data = edited_scenes
    
    st.markdown("---")
    
    # 根据工作流状态渲染不同按钮
    if st.session_state.workflow_state == 'draft':
        _render_draft_actions(
            user_id, edited_scenes, llm_api_key,
            save_script_version_func, refine_script_data_func,
            check_ssml_quality_func, refine_script_by_chat_func
        )
    elif st.session_state.workflow_state == 'locked':
        _render_locked_actions(user_id, edited_scenes, zhipu_api_key, pexels_api_key, voice_mapping)
    elif st.session_state.workflow_state == 'producing':
        _render_producing_actions(
            user_id, edited_scenes, zhipu_api_key, pexels_api_key,
            voice_mapping, render_ai_video_pipeline_func
        )
    elif st.session_state.workflow_state == 'completed':
        _render_completed_actions()


def _render_draft_actions(
    user_id, edited_scenes, llm_api_key,
    save_script_version_func, refine_script_data_func,
    check_ssml_quality_func, refine_script_by_chat_func
):
    """渲染草稿状态的操作按钮（精修、锁定、质量检查、对话微调）"""
    col_refine, col_lock = st.columns(2)
    
    with col_refine:
        if st.button("✨ 让大师精修剧本", use_container_width=True, help="清除废话，强化钩子，提升文案爆款率"):
            if not llm_api_key:
                st.error("请配置 DeepSeek Key")
            else:
                with st.spinner("大师正在逐句毒舌批改中..."):
                    refined_data = refine_script_data_func(edited_scenes, llm_api_key)
                    if refined_data:
                        st.session_state.scenes_data = refined_data
                        st.rerun()
    
    with col_lock:
        if st.button("🔒 锁定剧本", type="primary", use_container_width=True, help="确认剧本，进入生产阶段"):
            _lock_script(user_id, edited_scenes, save_script_version_func)
    
    # SSML 质量检查
    _render_ssml_checker(check_ssml_quality_func)
    
    # 对话微调
    _render_chat_refiner(edited_scenes, llm_api_key, refine_script_by_chat_func)


def _lock_script(user_id, edited_scenes, save_script_version_func):
    """锁定剧本，保存版本"""
    timestamp = datetime.now().strftime("%H:%M")
    version_num = len(st.session_state.script_versions) + 1
    
    version = {
        'version': version_num,
        'timestamp': timestamp,
        'scenes': edited_scenes.copy()
    }
    st.session_state.script_versions.append(version)
    st.session_state.current_version_index = len(st.session_state.script_versions) - 1
    
    # 持久化到数据库
    save_script_version_func(user_id, version_num, timestamp, edited_scenes.copy())
    
    # 转换状态为 locked
    st.session_state.workflow_state = 'locked'
    st.success("✅ 剧本已锁定！已保存到历史记录")
    st.rerun()


def _render_ssml_checker(check_ssml_quality_func):
    """渲染 SSML 质量检查器"""
    with st.expander("🔍 TTS 情绪标注质量检查", expanded=False):
        st.caption("💡 检查剧本中的 SSML 情绪标签，确保语音合成具备情绪表现力")
        
        if st.button("🔍 开始检查", use_container_width=True):
            total, ssml_count, hook_ok, warns = check_ssml_quality_func(st.session_state.scenes_data)
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("🎬 总分镜数", total)
            col_b.metric("🎵 SSML 标注", f"{ssml_count}/{total}")
            
            coverage = int((ssml_count / total * 100)) if total > 0 else 0
            if coverage >= 80:
                col_c.metric("🎯 覆盖率", f"{coverage}%", delta="优秀", delta_color="normal")
            elif coverage >= 50:
                col_c.metric("🎯 覆盖率", f"{coverage}%", delta="良好", delta_color="normal")
            else:
                col_c.metric("🎯 覆盖率", f"{coverage}%", delta="需改进", delta_color="inverse")
            
            if hook_ok:
                st.success("✅ Hook（第1个分镜）已标注 SSML 情绪")
            else:
                st.error("❌ 关键问题：Hook 缺少 SSML 标注！")
            
            if warns:
                st.warning("⚠️ **检查结果**")
                for warn in warns:
                    st.write(warn)
            else:
                st.balloons()
                st.success("🎉 完美！所有分镜都包含 SSML 情绪标注！")


def _render_chat_refiner(edited_scenes, llm_api_key, refine_script_by_chat_func):
    """渲染对话微调模块"""
    with st.expander("💬 对话微调：用自然语言修改剧本", expanded=False):
        st.caption('💡 例如："第二段太平淡了，加点反转"、"开头更有冲击力"、"缩短到 30 秒"')
        
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
                    refined_scenes = refine_script_by_chat_func(
                        current_scenes=edited_scenes,
                        user_request=user_request,
                        api_key=llm_api_key
                    )
                    
                    if refined_scenes:
                        st.session_state.chat_history.append({
                            "request": user_request,
                            "result": refined_scenes
                        })
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


def _render_locked_actions(user_id, edited_scenes, zhipu_api_key, pexels_api_key, voice_mapping):
    """渲染锁定状态的操作按钮（解锁、一键生产）"""
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
                st.session_state.workflow_state = 'producing'
                st.rerun()


def _render_producing_actions(
    user_id, edited_scenes, zhipu_api_key, pexels_api_key,
    voice_mapping, render_ai_video_pipeline_func
):
    """渲染生产状态（视频生成进度）"""
    # 高级设置折叠面板
    with st.expander("🏛️ 高级设置：调整BGM/音色/画风", expanded=False):
        st.caption("💡 系统已根据风格自动匹配以下参数，你可以手动覆盖：")
        
        st.markdown("**🎵 BGM 匹配**")
        style_name = st.session_state.get('script_mode', STYLE_OPTIONS[0])
        st.info(f"推荐：根据 {style_name} 风格自动匹配 BGM")
        
        st.markdown("---")
        
        st.markdown("**🎹️ 音色选择**")
        current_voice_label = [k for k, v in voice_mapping.items() if v == st.session_state.voice_id][0]
        st.info(f"当前：{current_voice_label}")
        st.caption("💡 可以在侧边栏中切换音色")
        
        st.markdown("---")
        
        st.markdown("**🎨 画面风格**")
        st.info("根据剧本中的 image_prompt 自动绘制")
    
    # 视频生成进度
    with st.status("🚀 视频引擎全力运转中...", expanded=True) as status:
        st.write("🎨 智谱 AI 正在绘制高清分镜...")
        
        selected_label = [k for k, v in voice_mapping.items() if v == st.session_state.voice_id][0]
        if st.session_state.voice_id.startswith("volc_"):
            st.write(f"🔥 火山引擎正在生成高表现力配音：{selected_label}")
        else:
            st.write(f"🎹️ Edge TTS 正在合成配音：{selected_label}")
        
        st.write("🎬 MoviePy 正在进行像素压制...")
        
        video_file = "ai_b_roll_output.mp4"
        success = render_ai_video_pipeline_func(
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
            
            st.session_state.workflow_state = 'completed'
            
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
            st.session_state.workflow_state = 'locked'


def _render_completed_actions():
    """渲染完成状态的操作按钮"""
    st.success("🎉 视频已生成完成！")
    if st.button("🆕 创作下一个视频", type="primary", use_container_width=True):
        st.session_state.workflow_state = 'draft'
        st.session_state.scenes_data = []
        st.session_state.chat_history = []
        st.rerun()
