# -*- coding: utf-8 -*-
"""
影像工坊视图 (Video View)
负责视频预览、分镜展示、素材管理
"""

import streamlit as st


def render_video_view():
    """
    渲染影像工坊 Tab 的完整界面
    """
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
