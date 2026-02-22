# -*- coding: utf-8 -*-
"""
VideoTaxi Views 包 - 视图层组件

重构后的视图层架构 (v3.1.0):
- script_view.py: 剧本构思 Tab (625行)
- video_view.py: 影像工坊 Tab (47行)  
- assets_view.py: 历史资产 Tab (73行)
- components/: 可复用 UI 组件
"""

from views.script_view import render_script_view
from views.video_view import render_video_view
from views.assets_view import render_assets_view

__all__ = ['render_script_view', 'render_video_view', 'render_assets_view']
