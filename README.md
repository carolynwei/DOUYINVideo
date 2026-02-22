# 🚖 VideoTaxi - AI短视频创作平台

> **开你的 VideoTaxi，在抖音公路上自由驰骋**

基于 Streamlit + DeepSeek + 智谱AI + 火山引擎的全自动短视频生成工具。
支持**渐进式工作流**和**对话创作**两种模式。

**v3.1.0 模块化重构版** - 代码从 1277 行精简至 276 行，采用路由中心化架构

## ✨ 核心功能

### 📝 渐进式工作流模式
- 🤖 **AI编剧**：支持5种爆款风格（认知刺客、听劝养成、POV沉浸、情绪宣泄、Meme抗象）
- 💬 **对话微调**：用自然语言描述修改需求，AI智能调整剧本
- 💾 **版本管理**：自动保存历史版本，支持一键回滚
- 🔒 **状态机**：draft → locked → producing → completed 流转控制
- 🎨 **AI绘画**：智谱CogView-3-Plus 生成高清分镜
- 🎵 **BGM风格路由**：根据剧本风格自动匹配背景音乐
- 🎤 **TTS情绪标注**：SSML语音合成，支持语速/音调/音量控制
- 🎬 **视频合成**：自动生成21:9竖屏短视频（1080x1920）

### 💬 对话创作模式
- 🧠 **连续对话**：AI记住完整上下文，提供连贯建议
- 💾 **数据持久化**：聊天记录存入SQLite，随时恢复
- 🔄 **多账号支持**：不同用户拥有独立的对话历史
- 🎯 **专业助手**：系统提示让AI扮演视频创作专家

### 👤 用户系统
- 🎫 **积分机制**：新用户赠送20积分，每日签到赠积分
- 📅 **连续签到**：连续签到奖励递增，最高15积分/天
- 🧩 **多模型支持**：DeepSeek（1积分）、GPT-4o（5积分）、Claude 3.5（4积分）
- 📊 **差异化计费**：根据模型智能程度消耗不同积分

## 🚀 快速开始

### 本地运行

1. **克隆仓库**：
```bash
git clone https://github.com/your-username/douyinVideo.git
cd douyinVideo
```

2. **安装依赖**：
```bash
pip install -r requirements.txt
```

3. **配置密钥**：
在 `.streamlit/secrets.toml` 中填入你的 API Keys：
```toml
# 必需配置
DEEPSEEK_KEY = "sk-your-deepseek-key"
ZHIPU_KEY = "your-zhipu-key"
TIANAPI_KEY = "your-tianapi-key"

# 可选配置
PEXELS_KEY = "your-pexels-key"  # 用于真实素材视频

# 火山引擎 TTS（高级音色）
VOLC_APPID = "your-appid"
VOLC_ACCESS_TOKEN = "your-access-token"
```

4. **运行应用**：
```bash
streamlit run app.py
```

### 云端部署（Streamlit Community Cloud）

1. Fork 本仓库到你的 GitHub
2. 登录 [Streamlit Cloud](https://share.streamlit.io/)
3. 创建新应用，选择本仓库
4. 在 Settings → Secrets 中配置 API Keys
5. 部署完成！

## 📚 项目结构 (v3.1.0 模块化重构版)

```
douyinVideo/
├── 📄 核心模块
│   ├── app.py                 # 🎯 主应用入口 (276行) - 路由中心化架构
│   ├── api_services.py        # 🔌 AI API 服务层 (548行)
│   ├── video_engine.py        # 🎬 视频渲染引擎 (890行)
│   ├── db_manager.py          # 💾 数据库管理 (146行)
│   ├── chat_page.py           # 💬 对话创作页面
│   ├── tianapi_navigator.py   # 🛰️ 热点导航员
│   ├── scheduler_tower.py     # 🗼 调度塔台
│   └── cyber_theme.py         # 🎨 赛博主题系统
│
├── 🖼️ 视图层 (views/)
│   ├── __init__.py
│   ├── script_view.py         # 🔥 剧本构思 Tab (625行)
│   ├── video_view.py          # 🎬 影像工坊 Tab (47行)
│   ├── assets_view.py         # 📂 历史资产 Tab (73行)
│   └── components/
│       └── hero_section.py    # Hero 视觉组件
│
├── 🎨 资源文件
│   └── assets/
│       ├── font.ttf           # 中文字体文件
│       ├── bgm.mp3            # 默认背景音乐
│       └── bgm/               # BGM风格库
│           ├── assassin/      # 认知刺客流BGM
│           ├── growth/        # 听劝养成BGM
│           ├── pov/           # POV沉浸BGM
│           ├── venting/       # 情绪宣泄BGM
│           └── meme/          # Meme抗象BGM
│
├── 🧪 测试文件
│   └── tests/
│       ├── test_pipeline.py   # 功能测试脚本
│       └── test_zhipu_api.py  # 智谱API测试
│
├── 📝 文档
│   ├── PROJECT_WIKI.md        # 📖 项目全景Wiki
│   └── docs/
│       └── 改进.md            # 开发思路
│
├── ⚙️ 配置文件
│   ├── .streamlit/
│   │   └── secrets.toml      # API 密钥配置（需自行创建）
│   ├── requirements.txt      # Python 依赖
│   ├── packages.txt          # 系统依赖（ImageMagick）
│   ├── runtime.txt           # Python 版本指定
│   └── environment.yml       # Conda 环境配置
├── 📦 示例代码
│   └── examples/
│       └── volcengine/       # 火山引擎 TTS SDK
└── 📊 数据库
    └── app_data.db           # SQLite 数据库（自动生成）
```

## 🛠️ 技术架构

### 前端框架
- **Streamlit**: 快速构建Web应用
- **st.session_state**: 会话状态管理
- **st.chat_message**: 现代化聊天界面

### AI模型
- **DeepSeek-V3**: 剧本生成、对话创作
- **智谱CogView-3-Plus**: 高清图像生成
- **GPT-4o / Claude 3.5**: 高级创作模式

### 语音合成
- **火山引擎 TTS V3**: WebSocket 流式传输，支持豆包大模型 2.0
- **Edge-TTS**: 免费兜底方案

### 视频处理
- **MoviePy**: 视频剪辑和合成
- **Pillow**: 字幕绘制（替代 ImageMagick TextClip）

### 数据存储
- **SQLite**: 轻量级本地数据库
- 用户表：积分、签到记录
- 聊天表：对话历史持久化

### 数据源
- **天行数据API**: 抖音热搜榜单
- **Pexels API**: 真实素材视频（可选）

## 🎮 使用指南

### 渐进式工作流模式
1. 在侧边栏登录用户名
2. 选择大语言模型（DeepSeek/GPT-4o/Claude）
3. 选择配音音色
4. 选择爆款风格（5种：刺客/听劝/POV/宣泄/Meme）
5. 输入主题或点击“刷新热点”获取抖音热搜
6. 点击“生成剧本”生成AI剧本
7. 在表格中微调文案和画面描述
8. 可选：使用“对话微调”用自然语言描述修改需求
9. 点击“锁定剧本”保存当前版本
10. 在高级设置中调整BGM/音色/画风（可选）
11. 点击“一键生产”开始渲染（2-3分钟）

### 对话创作模式
1. 在侧边栏选择“对话创作模式”
2. 直接和AI对话，描述你的创作需求
3. AI会记住所有对话，提供连贯建议
4. 切换账号或重新登录，历史记录自动恢复

## ⚠️ 注意事项

1. **字体文件**: `assets/font.ttf` 必须存在，否则字幕渲染会失败
2. **BGM文件**: `assets/bgm.mp3` 为默认背景音乐，风格化BGM在 `assets/bgm/` 子目录
3. **ImageMagick**: Windows用户需要手动安装
4. **积分系统**: 每次API调用会消耗积分，请注意余额
5. **火山引擎TTS**: 未配置时自动回退到 Edge-TTS
6. **数据库**: `app_data.db` 会自动创建，不要删除
7. **SSML标签**: AI生成的剧本自动包含SSML情绪标签，增强语音表现力

## 📝 API 密钥获取

- **DeepSeek**: [https://platform.deepseek.com](https://platform.deepseek.com)
- **智谱AI**: [https://open.bigmodel.cn](https://open.bigmodel.cn)
- **天行数据**: [https://www.tianapi.com](https://www.tianapi.com)
- **火山引擎**: [https://www.volcengine.com](https://www.volcengine.com)
- **Pexels**: [https://www.pexels.com/api](https://www.pexels.com/api)

## ⚙️ 环境要求

- Python 3.8+
- 1GB+ 内存
- ImageMagick（Linux自动安装，Windows需手动安装）

## 🐛 常见问题

**Q: 字幕显示乱码怎么办？**  
A: 确保 `assets/font.ttf` 文件存在于项目目录。

**Q: 视频生成失败？**  
A: 检查 ImageMagick 是否安装，Windows用户需要手动安装。

**Q: 积分不足怎么办？**  
A: 每日签到领取积分，或者选择低消耗模型（DeepSeek）。

**Q: 火山引擎音色无法使用？**  
A: 检查是否配置了 `VOLC_APPID` 和 `VOLC_ACCESS_TOKEN`，未配置时会自动使用 Edge-TTS。

**Q: 对话记录丢失？**  
A: 对话记录存储在 `app_data.db` 中，确保数据库文件没有被删除。

**Q: BGM无法播放？**  
A: 确保 `assets/bgm.mp3` 存在，或在 `assets/bgm/` 子目录添加风格化BGM。

**Q: 如何使用对话微调功能？**  
A: 生成剧本后，在“对话微调”框中输入修改需求（如“加点反转”、“缩短时长”），AI会智能调整。

## 📦 更新日志

### v3.0.0 (2026-02)
- ✨ 渐进式工作流系统：对话微调 + 版本管理 + 状态机
- 🎵 BGM风格路由系统：5种风格自动匹配背景音乐
- 🎤 TTS情绪标注：SSML语音合成，支持语速/音调/音量控制
- 🎨 浅色模式完善：30项CSS规则全面覆盖
- ⚙️ 字体和BGM路径优化：移至assets目录，多级降级策略
- 📚 仓库结构整理：tests/docs/scripts目录规范化

### v2.0.0 (2024-02)
- ✨ 新增对话创作模式
- 💾 聊天记录数据库持久化
- 👤 用户积分系统
- 🧠 多模型切换（DeepSeek/GPT-4o/Claude）
- 📅 每日签到功能

### v1.5.0 (2024-02)
- 🎤 火山引擎 TTS V3 集成
- 🎵 多音色支持（京腔、emo风格）
- ✨ AI二次精修功能
- 🎨 画面提示词自动/手动切换

### v1.0.0 (2024-01)
- 🎉 项目初始版本
- 基础视频生成功能

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

---

⭐ 如果这个项目对你有帮助，请给个 Star 吧！
