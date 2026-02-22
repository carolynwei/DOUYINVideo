# -*- coding: utf-8 -*-
"""
历史资产视图 (Assets View)
负责历史创作记录、云端资产库管理
"""

import streamlit as st


def render_assets_view():
    """
    渲染历史资产 Tab 的完整界面
    资产态：成品管理与复盘分析 + 跑单里程表
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
            当前阶段: STEP 3/3
        </div>
        <div style="font-size: 18px; font-weight: 700; color: #FF3131; margin-top: 4px;">
            📂 资产态 — 我的车库
        </div>
        <div style="font-size: 13px; color: #8b949e; margin-top: 4px;">
            管理成品 → 数据分析 → 下载导出 → 回到构思态迭代优化
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== 跑单里程表（简化版）=====
    st.markdown("""
    <div style="border: 1px solid #FF3131; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
        <div style="font-size: 12px; color: #FF3131; margin-bottom: 10px;">🚖 流量跑单实时监控</div>
        <div style="font-size: 13px; color: #666; margin-bottom: 10px;">让流量为你 7×24 小时跑单</div>
        <div style="font-size: 36px; font-weight: bold; color: #FF3131; margin-bottom: 15px;">14:22:36</div>
        <div style="display: flex; gap: 20px;">
            <div><span style="font-size: 20px; font-weight: bold; color: #333;">{}</span><br><span style="font-size: 11px; color: #666;">总视频数</span></div>
            <div><span style="font-size: 20px; font-weight: bold; color: #333;">{}</span><br><span style="font-size: 11px; color: #666;">总播放量</span></div>
            <div><span style="font-size: 20px; font-weight: bold; color: #333;">{}</span><br><span style="font-size: 11px; color: #666;">热门作品</span></div>
        </div>
    </div>
    """.format(
        len(st.session_state.get('script_versions', [])),
        "0",
        "暂无"
    ))
    
    st.divider()
    
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
