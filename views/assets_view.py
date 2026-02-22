# -*- coding: utf-8 -*-
"""
历史资产视图 (Assets View)
负责历史创作记录、云端资产库管理
"""

import streamlit as st


def render_assets_view():
    """
    渲染历史资产 Tab 的完整界面
    """
    st.info("📂 **你的云端创作库**")
    
    # 创作统计
    st.markdown("""
    ### 📊 创作统计
    - 总视频数：**{}**
    - 总播放量：**{}**
    - 热门作品：**{}**
    """.format(
        len(st.session_state.get('script_versions', [])),
        "0",  # TODO: 从数据库获取
        "暂无"  # TODO: 从数据库获取
    ))
    
    st.markdown("---")
    
    # 历史版本列表
    if st.session_state.get('script_versions'):
        st.markdown("### 💾 历史剧本版本")
        
        for i, version in enumerate(reversed(st.session_state.script_versions[-10:])):
            with st.expander(f"📚 版本 {version.get('version', i+1)} - {version.get('timestamp', '未知时间')}"):
                scenes = version.get('scenes', [])
                st.caption(f"包含 {len(scenes)} 个分镜")
                
                if scenes:
                    for j, scene in enumerate(scenes[:3]):  # 只显示前3个
                        narration = scene.get('narration', '')
                        if narration and isinstance(narration, str):
                            preview = narration[:30] + "..." if len(narration) > 30 else narration
                            st.write(f"{j+1}. {preview}")
                    
                    if len(scenes) > 3:
                        st.caption(f"... 还有 {len(scenes) - 3} 个分镜")
                
                # 恢复此版本按钮
                if st.button(f"🔄 恢复此版本", key=f"restore_version_{version.get('version', i)}"):
                    st.session_state.scenes_data = scenes
                    st.session_state.workflow_state = 'draft'
                    st.success(f"✅ 已恢复到版本 {version.get('version', i+1)}")
                    st.rerun()
    else:
        st.markdown("""
        ### 💾 历史项目
        🚧 暂无历史创作记录
        
        开始创作后，你的剧本版本将自动保存到这里。
        """)
    
    st.markdown("---")
    
    # 未来功能预告
    with st.expander("🔮 即将上线功能"):
        st.markdown("""
        - 📤 分享到社交媒体
        - 📄 导出剧本为PDF
        - 📊 视频数据分析
        - 🎯 智能推荐优化
        """)
