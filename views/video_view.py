# -*- coding: utf-8 -*-
"""
影像工坊视图 (Video View)
负责视频预览、分镜展示、素材管理
"""

import streamlit as st


def render_video_view():
    """
    渲染影像工坊 Tab 的完整界面
    生产态：工业化视频渲染
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
            当前阶段: STEP 2/3
        </div>
        <div style="font-size: 18px; font-weight: 700; color: #FF3131; margin-top: 4px;">
            🎬 生产态 — 工业化渲染
        </div>
        <div style="font-size: 13px; color: #8b949e; margin-top: 4px;">
            确认剧本 → 生成画面 → 合成视频 → 进入历史资产管理
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 工作流进度条
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.progress(100, text="构思")
    with col2:
        st.progress(50, text="生产")
    with col3:
        st.progress(0, text="资产")
    
    st.divider()
    
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
                        st.image(
                            f"https://via.placeholder.com/300x533/1a1a1a/FF3131?text=Scene+{idx+1}",
                            caption=f"🎬 分镜 {idx+1}"
                        )
                        with st.expander("📝 查看文案"):
                            # 确保 narration 是字符串类型
                            narration = scene.get('narration', '')
                            if narration and isinstance(narration, str):
                                preview = narration[:50] + "..." if len(narration) > 50 else narration
                                st.write(preview)
                            else:
                                st.write("⚠️ 暂无文案")
    else:
        st.warning("👉 请先在【剧本构思】Tab 生成剧本")
