# -*- coding: utf-8 -*-
"""
侧边栏视图 - VideoTaxi 驾驶员监控面板
"""

import streamlit as st
from datetime import datetime
from db_manager import (
    get_or_create_user, check_in, get_user_credits,
    load_script_versions
)
from tianapi_navigator import TianapiNavigator, auto_pilot_generate
from scheduler_tower import SchedulerTower, FeedbackDatabase


def render_sidebar():
    """
    渲染侧边栏
    返回: bool - 用户是否已认证
    """
    with st.sidebar:
        # Logo 区域
        st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="margin: 0; color: #FF3131;">🚖 VideoTaxi</h2>
            <p style="margin: 0; font-size: 12px; color: #8b949e;">让流量为你 7x24 小时跑单</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        # 用户登录
        user_id = st.text_input(
            "👤 用户名",
            value=st.session_state.user_id,
            placeholder="输入用户名",
            key="user_login"
        )
        
        if not user_id:
            st.warning("👈 请先登录")
            return False
        
        st.session_state.user_id = user_id
        user_info = get_or_create_user(user_id)
        
        # 加载历史剧本版本
        if 'script_versions_loaded' not in st.session_state:
            st.session_state.script_versions = load_script_versions(user_id)
            st.session_state.current_version_index = len(st.session_state.script_versions) - 1 if st.session_state.script_versions else -1
            st.session_state.script_versions_loaded = True
        
        # 用户信息和签到
        col_cred, col_btn = st.columns([1, 1])
        with col_cred:
            st.metric("💎 积分", user_info["credits"], label_visibility="collapsed")
        with col_btn:
            if st.button("📅 签到", use_container_width=True):
                success, msg = check_in(user_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.info(msg)
        
        if st.session_state.script_versions:
            st.caption(f"📚 已保存 {len(st.session_state.script_versions)} 个剧本版本")
        
        st.divider()
        
        # 渲染热点雷达
        _render_hotspot_radar()
        
        st.divider()
        
        # 渲染全自动发车
        _render_auto_pilot()
        
        st.divider()
        
        # 渲染调度塔台
        _render_scheduler_tower()
        
        st.divider()
        
        # 渲染引擎设置
        _render_engine_settings()
        
        return True


def _render_hotspot_radar():
    """热点雷达模块"""
    st.subheader("📡 热点雷达")
    
    try:
        tianapi_key = st.secrets["TIANAPI_KEY"]
    except:
        st.error("❌ 缺少 TIANAPI_KEY")
        return
    
    if st.button("🔄 刷新全网热点", use_container_width=True):
        with st.spinner("正在扫描抖音热搜..."):
            navigator = TianapiNavigator(tianapi_key)
            st.session_state.navigator = navigator
            st.session_state.missions = navigator.fetch_today_missions(num=5)
            if st.session_state.missions:
                st.success(f"✅ 获取到 {len(st.session_state.missions)} 个热点")
            else:
                st.error("❌ 获取热点失败")
    
    # 显示热点列表
    if st.session_state.missions:
        st.caption("💡 点击「锁定」将热点填入创作主题")
        
        for i, mission in enumerate(st.session_state.missions):
            with st.expander(f"{mission['heat_level']} {mission['topic'][:12]}..."):
                st.write(f"**热度值**: {mission['hot_value']:,}")
                st.write(f"**推荐风格**: {mission['recommended_style']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🚩 锁定", key=f"lock_{i}", use_container_width=True):
                        st.session_state.selected_topic = mission['topic']
                        st.session_state.selected_style = mission['recommended_style']
                        st.toast(f"🎯 已锁定: {mission['topic']}")
                        st.rerun()
                
                with col2:
                    if st.button(f"🔍 扩充", key=f"expand_{i}", use_container_width=True):
                        with st.spinner("正在分析热点背景..."):
                            expansion = st.session_state.navigator.expand_topic_context(
                                mission['topic'],
                                st.secrets["DEEPSEEK_KEY"]
                            )
                            if expansion['success']:
                                st.session_state[f"expansion_{i}"] = expansion['expansion']
                            else:
                                st.error("扩充失败")
                
                # 显示扩充结果
                if f"expansion_{i}" in st.session_state:
                    exp = st.session_state[f"expansion_{i}"]
                    st.markdown("---")
                    st.markdown("**🎯 情绪母体**: " + exp.get('emotion_mother', '未知'))
                    st.markdown("**👥 目标人群**: " + exp.get('target_audience', '未知'))


def _render_auto_pilot():
    """全自动发车模块"""
    st.header("🤖 全自动发车")
    st.caption("一键执行：抓取热点 → 生成剧本 → 渲染视频")
    
    auto_num = st.number_input(
        "生成数量",
        min_value=1,
        max_value=3,
        value=1,
        help="一次自动生成多少个视频（建议1-3个）"
    )
    
    if st.button("🚀 全自动发车", type="primary", use_container_width=True):
        if not st.session_state.missions:
            st.error("❌ 请先刷新热点雷达")
            return
        
        try:
            pexels_key = st.secrets.get("PEXELS_KEY", "")
        except:
            pexels_key = ""
        
        with st.spinner("🚗 VideoTaxi 正在全自动跑单..."):
            results = auto_pilot_generate(
                navigator=st.session_state.navigator,
                deepseek_key=st.secrets["DEEPSEEK_KEY"],
                zhipu_key=st.secrets["ZHIPU_KEY"],
                pexels_key=pexels_key,
                voice_id=st.session_state.get('voice_id', 'zh-CN-YunxiNeural'),
                num_missions=int(auto_num)
            )
            
            if results:
                success_videos = [r for r in results if r['status'] == 'success']
                if success_videos:
                    st.balloons()
                    st.success(f"🎉 成功生成 {len(success_videos)} 个视频！")
                    
                    import os
                    for video in success_videos:
                        if os.path.exists(video['video_file']):
                            with open(video['video_file'], 'rb') as f:
                                st.download_button(
                                    f"⬇️ 下载: {video['topic'][:10]}...",
                                    data=f.read(),
                                    file_name=video['video_file'],
                                    mime="video/mp4",
                                    key=f"dl_{video['topic']}"
                                )


def _render_scheduler_tower():
    """调度塔台模块"""
    st.header("🗼 调度塔台")
    st.caption("7x24小时无人值守自动驾驶")
    
    if 'feedback_db' not in st.session_state:
        st.session_state.feedback_db = FeedbackDatabase()
    
    # 数据感应导航员报告
    with st.expander("📊 数据感应报告"):
        feedback_db = st.session_state.feedback_db
        ranking = feedback_db.get_style_ranking()
        
        if ranking:
            st.markdown("**🏆 风格表现排名**")
            for i, item in enumerate(ranking[:3]):
                medal = ["🥇", "🥈", "🥉"][i]
                st.markdown(f"{medal} **{item['style'][:10]}...** - 均分: {item['avg_score']:.2f}")
        else:
            st.info("暂无历史数据，开始创作后会自动生成报告")
    
    # 定时调度设置
    st.markdown("---")
    st.markdown("**⏰ 定时调度**")
    
    schedule_time = st.time_input(
        "每日发车时间",
        value=datetime.strptime("04:00", "%H:%M").time()
    )
    schedule_num = st.number_input(
        "每次生成数量",
        min_value=1,
        max_value=5,
        value=1,
        key="schedule_num"
    )
    
    col_schedule, col_now = st.columns(2)
    
    with col_schedule:
        if st.button("⏰ 设置定时", use_container_width=True):
            st.info(f"⏰ 已设置每日 {schedule_time.strftime('%H:%M')} 自动发车")
            st.caption("💡 提示：部署到服务器后可实现真正的7x24小时运行")
    
    with col_now:
        if st.button("▶️ 立即执行", type="primary", use_container_width=True):
            _execute_scheduler_task(schedule_num)


def _execute_scheduler_task(num_videos):
    """执行调度任务"""
    import os
    
    try:
        pexels_key = st.secrets.get("PEXELS_KEY", "")
    except:
        pexels_key = ""
    
    with st.spinner("🚗 调度塔台正在执行任务..."):
        tower = SchedulerTower(
            tianapi_key=st.secrets["TIANAPI_KEY"],
            deepseek_key=st.secrets["DEEPSEEK_KEY"],
            zhipu_key=st.secrets["ZHIPU_KEY"],
            pexels_key=pexels_key
        )
        results = tower.auto_drive_mission(num_videos=int(num_videos))
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        if success_count > 0:
            st.success(f"✅ 成功生成 {success_count} 个视频！")
            for r in results:
                if r['status'] == 'success' and os.path.exists(r['video_file']):
                    with open(r['video_file'], 'rb') as f:
                        st.download_button(
                            f"⬇️ {r['topic'][:15]}...",
                            data=f.read(),
                            file_name=r['video_file'],
                            mime="video/mp4",
                            key=f"tower_dl_{r['video_id']}"
                        )
        else:
            st.error("❌ 任务执行失败")


def _render_engine_settings():
    """引擎设置模块"""
    st.header("⚙️ 核心引擎设置")
    
    # API 密钥检查
    try:
        tianapi_key = st.secrets["TIANAPI_KEY"]
        llm_api_key = st.secrets["DEEPSEEK_KEY"]
        zhipu_api_key = st.secrets["ZHIPU_KEY"]
        pexels_api_key = st.secrets.get("PEXELS_KEY", "")
        st.success("✅ 密钥加载成功（已安全隐藏）")
    except Exception as e:
        st.error("❌ 密钥缺失：请在 Streamlit Cloud 后台配置 Secrets")
        st.stop()
    
    st.info("💡 你的个人 API 密钥已通过 Streamlit Cloud 加密保护。")
    st.divider()
    
    # 大语言模型选择
    st.header("🧠 大语言模型")
    
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
    
    current_model_id = MODEL_CONFIG[selected_model_label]["id"]
    current_model_cost = MODEL_CONFIG[selected_model_label]["cost"]
    
    st.session_state.model_id = current_model_id
    st.session_state.model_cost = current_model_cost
    
    st.info(f"💰 当前模型单次调用消耗: **{current_model_cost} 积分**")
    st.divider()
    
    # 创作模式切换
    st.header("🎯 创作模式")
    page_mode = st.radio(
        "选择你的创作方式：",
        ["📝 工作流模式", "💬 对话创作模式"],
        help="工作流：适合系统化创作 | 对话：自然聊天式创作",
        horizontal=True
    )
    st.session_state.page_mode = page_mode
    st.divider()
    
    # 配音音色选择
    st.header("🎙️ 配音音色选择")
    
    VOICE_MAPPING = {
        "标准男声 (免费/Edge)": "zh-CN-YunxiNeural",
        "标准女声 (免费/Edge)": "zh-CN-XiaoxiaoNeural",
        "温柔女声 (免费/Edge)": "zh-CN-XiaoyiNeural",
        "🍵 京腔侃爷 (火山)": "volc_zh_male_jingqiangkanye_moon_bigtts",
        "✨ 俊朗男友 (火山)": "volc_zh_male_junlangnanyou_emo_v2_mars_bigtts",
        "🎀 甜心小妹 (火山)": "volc_zh_female_tianxinxiaomei_emo_v2_mars_bigtts",
    }
    
    selected_voice_label = st.selectbox(
        "请选择配音音色与方言：",
        list(VOICE_MAPPING.keys()),
        help="火山引擎音色支持方言和情绪表达，Edge TTS 免费但表现力有限"
    )
    
    st.session_state.voice_id = VOICE_MAPPING[selected_voice_label]
