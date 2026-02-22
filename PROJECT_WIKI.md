# 🎬 VideoTaxi (VibeDrive) - 项目全景 Wiki

> **开你的 VideoTaxi，在抖音公路上自由驰骋**

---

## 📋 项目概览

| 属性 | 详情 |
|------|------|
| **项目名称** | VideoTaxi / ASSASSIN AI / 认知刺客创作平台 |
| **核心定位** | AI驱动的全自动短视频生成工具 |
| **目标平台** | 抖音（竖屏 9:16，1080x1920） |
| **技术栈** | Python + Streamlit + DeepSeek + 智谱AI + 火山引擎 |
| **部署方式** | 本地运行 / Streamlit Cloud |
| **当前版本** | v3.0.0 (2026-02-22) |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层 (UI Layer)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ 剧本构思 Tab │  │ 影像工坊 Tab │  │      历史资产 Tab        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              对话创作模式 (Chat Mode)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (Service Layer)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  导航员系统  │  │  剧本生成器  │  │      视频渲染引擎        │  │
│  │TianapiNavigator│ │api_services │  │     video_engine        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  调度塔台    │  │  用户系统    │  │      对话助手           │  │
│  │SchedulerTower│ │ db_manager  │  │      chat_page          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      外部服务层 (API Layer)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ DeepSeek │ │  智谱AI   │ │ 天行数据  │ │ 火山引擎  │ │ Pexels │ │
│  │  LLM     │ │ CogView  │ │ 抖音热搜  │ │   TTS    │ │ 视频   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构详解

```
douyinVideo/
│
├── 📄 核心应用文件
│   ├── app.py                    # 🎯 主应用入口 (1277行)
│   │                              #    - Streamlit页面配置
│   │                              #    - 赛博驾驶舱主题CSS
│   │                              #    - 三Tab工作台布局
│   │                              #    - 侧边栏用户系统
│   │                              #    - 渐进式工作流状态机
│   │
│   ├── api_services.py           # 🔌 AI API服务层 (548行)
│   │                              #    - get_hot_topics(): 抖音热搜获取
│   │                              #    - generate_script_json(): 标准剧本生成
│   │                              #    - generate_viral_script(): 爆款剧本生成
│   │                              #    - generate_script_by_style(): 5风格剧本生成
│   │                              #    - generate_images_zhipu(): 智谱AI绘画
│   │                              #    - refine_script_data(): 大师精修
│   │                              #    - refine_script_by_chat(): 对话微调
│   │
│   ├── video_engine.py           # 🎬 视频渲染引擎 (868行)
│   │                              #    - VIBE_ROUTING_TABLE: 情绪-参数路由表
│   │                              #    - get_bgm_by_style(): BGM风格路由
│   │                              #    - create_subtitle_image(): Pillow字幕绘制
│   │                              #    - call_volcengine_tts(): 火山引擎TTS
│   │                              #    - text_to_mp3(): Edge TTS合成
│   │                              #    - synthesize_emotional_segments_parallel(): 情绪片段并行合成
│   │                              #    - render_ai_video_pipeline(): 核心渲染管线
│   │                              #    - VideoAssembler: 导演时间轴引擎
│   │
│   ├── db_manager.py             # 💾 数据库管理 (146行)
│   │                              #    - init_db(): 初始化用户表
│   │                              #    - get_or_create_user(): 用户注册/登录
│   │                              #    - check_in(): 每日签到逻辑
│   │                              #    - deduct_credits(): 积分扣除
│   │                              #    - init_chat_db(): 聊天记录表
│   │                              #    - save_message/load_messages(): 对话持久化
│   │
│   ├── chat_page.py              # 💬 对话创作页 (168行)
│   │                              #    - call_deepseek_chat(): DeepSeek API调用
│   │                              #    - render_chat_page(): 聊天界面渲染
│   │                              #    - 系统提示词(爆款创作大师)
│   │
│   ├── tianapi_navigator.py      # 🛰️ 热点导航员 (429行)
│   │                              #    - TianapiNavigator: 天行数据对接
│   │                              #    - VIBE_ROUTING_TABLE: 风格关键词映射
│   │                              #    - fetch_today_missions(): 今日任务清单
│   │                              #    - expand_topic_context(): 热点背景扩充
│   │                              #    - auto_pilot_generate(): 全自动发车
│   │
│   └── scheduler_tower.py        # 🗼 调度塔台 (545行)
│                                   #    - PerformanceMetrics: 视频表现数据模型
│                                   #    - FeedbackDatabase: 反馈数据持久化
│                                   #    - DataAwareNavigator: 数据感应导航
│                                   #    - SchedulerTower: 7x24小时自动调度
│
├── 🎨 资源文件
│   └── assets/
│       ├── font.ttf              # 中文字体 (字幕渲染必需)
│       ├── bgm.mp3               # 默认背景音乐
│       └── bgm/                  # BGM风格库
│           ├── assassin/         # 🗡️ 认知刺客流BGM
│           ├── growth/           # 👍 听劝养成BGM
│           ├── pov/              # 🎬 POV沉浸BGM
│           ├── venting/          # 🔥 情绪宣泄BGM
│           └── meme/             # 🐱 Meme抗象BGM
│
├── ⚙️ 配置与部署
│   ├── .streamlit/
│   │   ├── config.toml           # Streamlit配置
│   │   └── secrets.toml          # API密钥 (需自行创建)
│   │                               #    - DEEPSEEK_KEY
│   │                               #    - ZHIPU_KEY
│   │                               #    - TIANAPI_KEY
│   │                               #    - PEXELS_KEY (可选)
│   │                               #    - VOLC_APPID / VOLC_ACCESS_TOKEN (可选)
│   │
│   ├── requirements.txt          # Python依赖
│   ├── packages.txt              # 系统依赖 (fonts-noto-cjk)
│   ├── runtime.txt               # Python版本 (3.9)
│   └── environment.yml           # Conda环境配置
│
├── 🧪 测试与示例
│   ├── tests/
│   │   ├── test_pipeline.py      # 功能测试脚本
│   │   └── test_zhipu_api.py     # 智谱API测试
│   │
│   └── examples/volcengine/
│       └── bidirection.py        # 火山引擎TTS V3 SDK
│
├── 📝 文档
│   └── docs/
│       └── 改进.md               # 开发思路与改进建议
│
└── 📊 数据文件
    └── app_data.db               # SQLite数据库 (自动生成)
```

---

## 🎮 核心功能模块

### 1️⃣ 渐进式工作流 (Progressive Workflow)

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│  draft  │ → │ locked  │ → │ producing │ → │ completed │
│  草稿   │    │  锁定   │    │  生产中   │    │  已完成   │
└─────────┘    └─────────┘    └──────────┘    └──────────┘
     │              │              │              │
   可编辑         不可编辑       渲染中          可下载
   可微调         可解锁         进度显示        可重置
```

**状态流转规则：**
- **draft → locked**: 点击"锁定剧本"，保存版本快照
- **locked → producing**: 点击"一键生产"，开始渲染
- **producing → completed**: 渲染成功，显示下载按钮
- **locked → draft**: 点击"解锁"，恢复编辑
- **completed → draft**: 点击"创作下一个"，重置状态

---

### 2️⃣ 五大爆款风格系统

| 风格 | 核心特征 | 视觉风格 | BGM音量 | 适用场景 |
|------|----------|----------|---------|----------|
| 🗡️ 认知刺客 | 冲击+扎心+人间清醒 | Sam Kolder 电影感 | 0.15 | 揭露真相、打破认知 |
| 👍 听劝养成 | 真诚+低姿态+蜕变 | Brandon Li Vlog | 0.08 | 养成系、求助互动 |
| 🎬 POV沉浸 | 代入感+压迫感+共情 | 第一人称视角 | 0.12 | 故事叙述、身临其境 |
| 🔥 情绪宣泄 | 爽感+反转+发疯文学 | 极近特写+快速剪辑 | 0.25 | 情绪出口、爽文剧情 |
| 🐱 Meme抗象 | 幽默+病毒+解压 | 扁平化+高饱和 | 0.20 | 病毒传播、低成本 |

---

### 3️⃣ TTS 情绪标注系统 (SSML)

```xml
<!-- 语速控制 -->
<prosody rate="fast">紧张冲击</prosody>
<prosody rate="slow">强调沉思</prosody>

<!-- 音调控制 -->
<prosody pitch="+15%">兴奋惊讶</prosody>
<prosody pitch="-10%">严肃低沉</prosody>

<!-- 音量控制 -->
<prosody volume="+20%">核心结论</prosody>
<prosody volume="-10%">低声秘密</prosody>

<!-- 组合使用 -->
<prosody rate="fast" pitch="+10%" volume="+15%">
  爆点金句！
</prosody>
```

**情绪曲线规范：**
- Hook(冷启动): `cold_question` / `sarcastic_mock`
- Content(深入): `deep_mystery` / `neutral_narrate`
- Gold(爆发): `angry_shout` / `excited_announce` / `fierce_warning`
- Outro(余韵): `sad_sigh` / `neutral_narrate`

---

### 4️⃣ 用户积分系统

| 操作 | 积分变化 | 说明 |
|------|----------|------|
| 新用户注册 | +20 | 初始赠送 |
| 每日签到 | +5~15 | 连续签到递增，封顶15 |
| DeepSeek调用 | -1 | 性价比之选 |
| Claude 3.5调用 | -4 | 文笔极佳 |
| GPT-4o调用 | -5 | 高智能深度重写 |

---

## 🔌 API 服务映射

### 外部API清单

| 服务 | 用途 | 关键函数 | 配置项 |
|------|------|----------|--------|
| **DeepSeek** | LLM剧本生成 | `generate_script_by_style()` | `DEEPSEEK_KEY` |
| **智谱AI** | AI绘画(CogView-3-Plus) | `generate_images_zhipu()` | `ZHIPU_KEY` |
| **天行数据** | 抖音热搜榜单 | `get_hot_topics()` | `TIANAPI_KEY` |
| **火山引擎** | 高阶TTS(豆包大模型) | `call_volcengine_tts()` | `VOLC_APPID`, `VOLC_ACCESS_TOKEN` |
| **Pexels** | 真实素材视频(可选) | `get_pexels_videos()` | `PEXELS_KEY` |

### 内部模块依赖图

```
app.py
├── api_services.py
│   ├── DeepSeek API
│   └── 智谱AI API
├── video_engine.py
│   ├── 智谱AI API (图片生成)
│   ├── 火山引擎 TTS / Edge TTS
│   └── MoviePy (视频合成)
├── db_manager.py
│   └── SQLite
├── chat_page.py
│   └── DeepSeek API
├── tianapi_navigator.py
│   └── 天行数据 API
└── scheduler_tower.py
    └── 依赖上述所有模块
```

---

## 🎨 主题系统

### 赛博驾驶舱主题 (Cyber Taxi Dashboard)

```css
/* 核心配色 */
--bg-primary: #0d1117      /* 深邃背景 */
--bg-secondary: #161b22    /* 卡片背景 */
--accent: #FF3131          /* 刺客红 */
--accent-hover: #FF6161    /* 呼吸灯效果 */
--text-primary: #E6EDF3    /* 主文字 */
--text-secondary: #8b949e  /* 次要文字 */
--border: #30363d          /* 边框 */
```

**视觉特效：**
- 刺客红呼吸灯动画 (metric-pulse)
- 赛道条纹进度条 (progress-move)
- 电子脉冲按钮效果
- 3D卡片悬浮效果
- 霓虹灯流光Hero区

---

## 🚀 部署指南

### 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/douyinVideo.git
cd douyinVideo

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置密钥 (创建 .streamlit/secrets.toml)
echo '[secrets]
DEEPSEEK_KEY = "sk-your-key"
ZHIPU_KEY = "your-key"
TIANAPI_KEY = "your-key"' > .streamlit/secrets.toml

# 4. 运行
streamlit run app.py
```

### Streamlit Cloud 部署

1. Fork 本仓库到 GitHub
2. 登录 [share.streamlit.io](https://share.streamlit.io)
3. 创建新应用，选择本仓库
4. 在 Settings → Secrets 中配置 API Keys
5. 点击 Deploy

---

## 📊 数据模型

### 用户表 (users)
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    credits INTEGER DEFAULT 0,
    last_login_date DATE,
    consecutive_days INTEGER DEFAULT 0
);
```

### 聊天记录表 (chat_history)
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 视频表现表 (video_performance)
```sql
CREATE TABLE video_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT UNIQUE,
    topic TEXT,
    style TEXT,
    publish_time TIMESTAMP,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    completion_rate REAL DEFAULT 0.0
);
```

---

## 🔄 版本演进

| 版本 | 时间 | 核心特性 |
|------|------|----------|
| v1.0.0 | 2024-01 | 基础视频生成 |
| v1.5.0 | 2024-02 | 火山引擎TTS、AI精修 |
| v2.0.0 | 2024-02 | 对话创作模式、积分系统 |
| v3.0.0 | 2026-02 | 渐进式工作流、BGM路由、SSML标注 |

---

## 🛠️ 开发规范

### 代码风格
- 文件编码: UTF-8
- 缩进: 4空格
- 字符串: 双引号优先
- 注释: 中文，说明"为什么"而非"是什么"

### 命名约定
- 模块: `snake_case.py`
- 类: `PascalCase`
- 函数: `snake_case()`
- 常量: `UPPER_SNAKE_CASE`

### Session State 键名规范
```python
# 工作流状态
st.session_state.workflow_state      # draft/locked/producing/completed
st.session_state.script_versions     # 版本历史列表
st.session_state.current_version_index # 当前版本索引

# 用户数据
st.session_state.user_id             # 当前用户ID
st.session_state.page_mode           # 页面模式

# 创作数据
st.session_state.scenes_data         # 当前剧本数据
st.session_state.chat_history        # 对话微调历史
st.session_state.voice_id            # 选中的音色ID
st.session_state.model_id            # 选中的模型ID
```

---

## 🐛 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 字幕乱码 | 字体文件缺失 | 确保 `assets/font.ttf` 存在 |
| 视频生成失败 | ImageMagick未安装 | Windows手动安装，Linux自动安装 |
| 音频生成失败 | 网络问题 | 检查网络，查看详细错误日志 |
| 积分不足 | 余额不够 | 每日签到或切换低消耗模型 |
| BGM无法播放 | 文件缺失 | 确保 `assets/bgm.mp3` 存在 |

---

## 📝 待办事项 (TODO)

- [ ] 视频发布对接 (抖音API)
- [ ] 历史资产页面完善
- [ ] 多语言支持
- [ ] 移动端适配优化
- [ ] A/B测试框架
- [ ] 实时协作功能

---

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

**提交规范：**
- `feat`: 新功能
- `fix`: 问题修复
- `docs`: 文档更新
- `refactor`: 重构
- `perf`: 性能优化

---

## 📄 许可证

MIT License

---

> **流量正在 7x24 小时为你跑单** 🚖
