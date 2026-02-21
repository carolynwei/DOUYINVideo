# 🎬 抖音AI视频自动生成系统

基于 Streamlit + DeepSeek + 智谱AI + Edge-TTS 的全自动短视频生成工具。

## ✨ 核心功能

- 📡 实时抓取抖音热搜榜单
- 🤖 AI自动生成视频分镜脚本
- 🎨 智谱CogView-3-Plus AI绘画
- 🎙️ Edge-TTS 真人配音
- 🎬 自动合成竖屏短视频（1080x1920）
- 🎵 支持背景音乐混音

## 🚀 快速开始

### 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置密钥：
在 `.streamlit/secrets.toml` 中填入你的 API Keys：
```toml
TIANAPI_KEY = "your_tianapi_key"
DEEPSEEK_KEY = "your_deepseek_key"
ZHIPU_KEY = "your_zhipu_key"
PEXELS_KEY = "your_pexels_key"
```

3. 运行应用：
```bash
streamlit run app.py
```

### 云端部署（Streamlit Community Cloud）

1. Fork 本仓库到你的 GitHub
2. 登录 [Streamlit Cloud](https://share.streamlit.io/)
3. 创建新应用，选择本仓库
4. 在 Settings → Secrets 中配置 API Keys
5. 部署完成！

## 📦 技术栈

- **前端框架**: Streamlit
- **AI模型**: DeepSeek（剧本生成）、智谱CogView-3-Plus（图像生成）
- **语音合成**: Edge-TTS
- **视频处理**: MoviePy
- **数据源**: 天行数据API（热搜榜）

## ⚙️ 环境要求

- Python 3.8+
- ImageMagick（Linux自动安装，Windows需手动安装）
- 1GB+ 内存

## 📝 许可证

MIT License
