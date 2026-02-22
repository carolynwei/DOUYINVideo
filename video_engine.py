# -*- coding: utf-8 -*-
"""
视频引擎模块：处理视频渲染、TTS合成、BGM混音等功能
VideoTaxi 片段式情绪引擎 (Segmented Emotional Engine)
确保所有中文字符正确显社
"""

import os
import platform
import asyncio
import edge_tts
import numpy as np
import requests
import json
import base64
import uuid
import subprocess
import sys
import random
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip, afx, concatenate_audioclips

# 🎭 情绪-参数路由表 (Emotion-Parameter Routing Table)
# 基于“语义-情绪映射”的工业化架构
VIBE_ROUTING_TABLE = {
    # 冷静类
    "cold_question": {
        "desc": "沉稳/冷淡/质疑",
        "edge_params": {"rate": "-5%", "pitch": "0%", "volume": "+0%"},
        "volc_voice": "zh_male_junlangnanyou_emo_v2_mars_bigtts",  # 俊朗男友-冷静
    },
    "deep_mystery": {
        "desc": "悬疑/低沉/神秘",
        "edge_params": {"rate": "-10%", "pitch": "-10%", "volume": "-5%"},
        "volc_voice": "zh_male_junlangnanyou_emo_v2_mars_bigtts",
    },
    
    # 兴奋类
    "excited_announce": {
        "desc": "兴奋/宣告/惊喜",
        "edge_params": {"rate": "+10%", "pitch": "+15%", "volume": "+10%"},
        "volc_voice": "zh_female_tianmeixiaomei_emo_moon_bigtts",  # 甜心小妹-兴奋
    },
    
    # 愤怒类
    "angry_shout": {
        "desc": "嘶吼/愤怒/爆发",
        "edge_params": {"rate": "+15%", "pitch": "+10%", "volume": "+20%"},
        "volc_voice": "zh_male_jingqiangkanye_emo_v2_mars_bigtts",  # 京腔侃爷-暴躁
    },
    "fierce_warning": {
        "desc": "猛烈/警告/喉哧",
        "edge_params": {"rate": "+10%", "pitch": "+5%", "volume": "+15%"},
        "volc_voice": "zh_male_jingqiangkanye_emo_v2_mars_bigtts",
    },
    
    # 崩溃类
    "sad_sigh": {
        "desc": "崩溃/叹息/委屈",
        "edge_params": {"rate": "-15%", "pitch": "-15%", "volume": "-10%"},
        "volc_voice": "zh_male_junlangnanyou_emo_v2_mars_bigtts",
    },
    
    # 嘲讽类
    "sarcastic_mock": {
        "desc": "嘲讽/嘲笑/轻蔑",
        "edge_params": {"rate": "+5%", "pitch": "-5%", "volume": "+5%"},
        "volc_voice": "zh_male_jingqiangkanye_emo_v2_mars_bigtts",
    },
    
    # 中性类（默认）
    "neutral_narrate": {
        "desc": "中性/平静/叙述",
        "edge_params": {"rate": "+0%", "pitch": "+0%", "volume": "+0%"},
        "volc_voice": "zh_male_junlangnanyou_emo_v2_mars_bigtts",
    },
}

# 🔑 字体路径配置：多级降级策略确保100%可用
def get_font_path():
    """智能检测可用的中文字体路径"""
    # 1. 优先：assets目录中的字体文件（绝对路径）
    repo_font = os.path.join(os.path.dirname(__file__), "assets", "font.ttf")
    if os.path.exists(repo_font):
        return repo_font
    
    # 2. 降级：当前工作目录的assets/font.ttf
    if os.path.exists("assets/font.ttf"):
        return os.path.abspath("assets/font.ttf")
    
    # 3. 兼容旧版本：根目录的font.ttf（向后兼容）
    if os.path.exists("font.ttf"):
        return os.path.abspath("font.ttf")
    
    # 3. 最终降级：寻找系统字体文件
    if platform.system() == "Linux":
        linux_fonts = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        for font in linux_fonts:
            if os.path.exists(font):
                return font
    
    # 如果都找不到，返回 None（后续会有错误提示）
    return None

FONT_PATH = get_font_path()

# 🔍 调试信息：在 Streamlit 侧边栏显示字体路径
try:
    if st and hasattr(st, 'sidebar'):
        with st.sidebar:
            if FONT_PATH:
                st.success(f"✅ 字体加载成功: {os.path.basename(FONT_PATH)}")
            else:
                st.error("❌ 未找到字体文件！请上传 font.ttf")
except:
    pass  # 非 Streamlit 环境下忽略

# 🎵 BGM 风格路由系统
def get_bgm_by_style(style_name, video_duration):
    """
    根据风格随机抽取一首 BGM，并根据视频时长自动循环和调整音量
    
    Args:
        style_name: 风格名称（如 "🗡️ 认知刺客流（冲击力+优越感）"）
        video_duration: 视频总时长（秒）
    
    Returns:
        AudioFileClip: 处理后的 BGM 音频剗辑，已调整音量和时长
    """
    # 风格与文件夹的映射
    style_folder_map = {
        "🗡️ 认知刺客流（冲击力+优越感）": "assassin",
        "👍 听勝/养成系（互动率04+评论爆炸）": "growth",
        "🎬 POV沉浸流（第一人称+代入感）": "pov",
        "🔥 情绪宣泄流（极致反转+发疯文学）": "venting",
        "🐱 Meme抗象流（低成本+病毒传播）": "meme"
    }
    
    folder_name = style_folder_map.get(style_name, "assassin")
    bgm_dir = os.path.join("assets", "bgm", folder_name)
    
    # 从目录下随机选一首歌
    if os.path.exists(bgm_dir):
        bgm_files = [f for f in os.listdir(bgm_dir) if f.endswith(('.mp3', '.wav'))]
        if bgm_files:
            selected_bgm = random.choice(bgm_files)
            bgm_path = os.path.join(bgm_dir, selected_bgm)
            st.info(f"🎵 使用 {style_name} 风格 BGM: {selected_bgm}")
        else:
            # 如果目录为空，使用默认 BGM
            bgm_path = "assets/bgm.mp3"
            st.warning(f"⚠️ {folder_name} 目录为空，使用默认 BGM")
    else:
        # 目录不存在，使用默认 BGM
        bgm_path = "assets/bgm.mp3"
        st.warning(f"⚠️ {bgm_dir} 不存在，使用默认 BGM")
    
    # 检查默认 BGM 是否存在（兼容旧版本）
    if not os.path.exists(bgm_path):
        # 尝试旧版本路径
        if os.path.exists("bgm.mp3"):
            bgm_path = "bgm.mp3"
        else:
            st.error("❌ 未找到 BGM 文件！请在 assets 目录下添加 bgm.mp3")
            return None
    
    try:
        # 加载音频
        bgm_clip = AudioFileClip(bgm_path)
        
        # 核心处理 1：如果 BGM 短于视频，则循环播放
        if bgm_clip.duration < video_duration:
            # 使用 afx.audio_loop 循环播放
            bgm_clip = afx.audio_loop(bgm_clip, duration=video_duration)
        else:
            # 截取所需长度
            bgm_clip = bgm_clip.subclip(0, video_duration)
            
        # 核心处理 2：设置 BGM 音量（通常设为 0.08 - 0.25，避免盖过人声）
        volume_map = {
            "🗡️ 认知刺客流（冲击力+优越感）": 0.15,
            "👍 听勝/养成系（互动率04+评论爆炸）": 0.08,
            "🎬 POV沉浸流（第一人称+代入感）": 0.12,
            "🔥 情绪宣泄流（极致反转+发疯文学）": 0.25,
            "🐱 Meme抗象流（低成本+病毒传播）": 0.20
        }
        
        volume = volume_map.get(style_name, 0.1)
        return bgm_clip.volumex(volume)
        
    except Exception as e:
        st.error(f"❌ BGM 加载失败: {e}")
        return None

def create_subtitle_image(text, width=1080, height=400, fontsize=70):
    """🎨 用 Pillow 手工绘制字幕图片（彻底绕过 ImageMagick）"""
    if not FONT_PATH:
        raise FileNotFoundError("未找到字体文件！请确保 font.ttf 存在于仓库根目录")
    
    # 创建透明背景图片
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font = ImageFont.truetype(FONT_PATH, fontsize)
    except Exception as e:
        st.error(f"字体加载失败: {e}")
        raise
    
    # 文本自动换行
    lines = []
    words = text
    max_width = width - 100  # 左右边距50px
    
    # 简单换行逻辑：按字符宽度切分
    current_line = ""
    for char in words:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    
    # 计算总高度并居中
    line_height = fontsize + 20
    total_height = len(lines) * line_height
    start_y = (height - total_height) // 2
    
    # 绘制每行文字（先画黑边，再画白字）
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = start_y + i * line_height
        
        # 黑色描边（stroke效果）
        for offset_x in [-2, 0, 2]:
            for offset_y in [-2, 0, 2]:
                if offset_x != 0 or offset_y != 0:
                    draw.text((x + offset_x, y + offset_y), line, font=font, fill=(0, 0, 0, 255))
        
        # 白色主文字
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    
    # 转为 numpy 数组供 MoviePy 使用
    return np.array(img)

def call_volcengine_tts(text, voice_id, output_path):
    """
    通过调用官方 V3 bidirection.py 脚本来生成豆包大模型音频
    支持 WebSocket 流式传输，适用于豆包语音合成模型 2.0
    """
    try:
        # 1. 安全获取鉴权信息
        appid = st.secrets.get("VOLC_APPID", "")
        access_token = st.secrets.get("VOLC_ACCESS_TOKEN", "")
        
        if not appid or not access_token:
            # 如果没有配置火山引擎，回退到 Edge TTS
            return False
        
        # 2. 官方脚本路径
        script_path = os.path.join(os.path.dirname(__file__), "examples", "volcengine", "bidirection.py")
        
        if not os.path.exists(script_path):
            st.error(f"❌ 找不到火山引擎 V3 脚本: {script_path}")
            return False
        
        st.info(f"🚀 正在调用豆包语音合成大模型: {voice_id}...")
        
        # 3. 构建命令行指令
        command = [
            sys.executable,  # 使用当前 Python 解释器
            script_path,
            "--appid", appid,
            "--access_token", access_token,
            "--voice_type", voice_id,
            "--text", text,
            "--encoding", "mp3",
            "--output", output_path  # 指定输出路径
        ]
        
        # 4. 执行脚本
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=60  # 60秒超时
        )
        
        # 5. 验证输出文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            st.success(f"✅ 豆包大模型音频流接收完毕！音频已保存至: {output_path}")
            return True
        else:
            st.error(f"❌ 输出文件未生成或为空: {output_path}")
            return False
            
    except subprocess.TimeoutExpired:
        st.error("❌ 火山引擎 TTS 超时（60秒）")
        return False
    except subprocess.CalledProcessError as e:
        st.error(f"❌ 火山大模型合成失败，官方脚本报错信息：")
        st.error(e.stderr)
        return False
    except Exception as e:
        st.error(f"❌ 火山引擎 TTS 调用异常: {e}")
        return False

async def text_to_mp3(text, filename, voice_id="zh-CN-YunxiNeural"):
    """【云端优化版】直接联网生成配音，增加重试逻辑。支持多路 TTS 路由。"""
    
    # 🎹️ 路由 1：火山引擎 TTS (方言 + 高情绪表达)
    if voice_id.startswith("volc_"):
        # 去掉前缀，获取真实的音色 ID
        real_voice_id = voice_id.replace("volc_", "")
        success = call_volcengine_tts(text, real_voice_id, filename)
        if success:
            return True
        else:
            # 火山引擎失败，回退到 Edge TTS
            st.warning("⚠️ 火山引擎不可用，回退到 Edge TTS 模式")
            voice_id = "zh-CN-YunxiNeural"  # 使用默认男声
    
    # 🎹️ 路由 2：Edge TTS (免费兼底)
    for attempt in range(3):
        try:
            # 🎵 支持SSML情绪标签：如果文本中包含<prosody>标签，Edge TTS会自动识别
            # 注意：Edge TTS原生支持SSML，直接传入包含<prosody>的文本即可
            communicate = edge_tts.Communicate(text, voice_id, rate="+10%")
            await communicate.save(filename)
            
            # 🔥 新增：验证文件是否生成成功
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                return True
            else:
                st.error(f"❌ 音频文件生成失败或为空: {filename}")
                return False
                
        except Exception as e:
            st.warning(f"TTS 尝试 {attempt+1}/3 失败: {e}")
            await asyncio.sleep(2)
    
    st.error(f"❌ 音频生成失败（3次重试后）: {filename}")
    return False

# 🎬 片段式情绪引擎 (Segmented Emotional Engine)
async def synthesize_emotional_segment(text, vibe, output_file, use_volcengine=False):
    """
    根据情绪标签合成单个音频片段
    
    Args:
        text: 文案内容
        vibe: 情绪标签（如 "cold_question", "angry_shout"）
        output_file: 输出文件路径
        use_volcengine: 是否使用火山引擎（默认False使用Edge TTS）
    
    Returns:
        bool: 是否成功
    """
    # 获取情绪参数，如果找不到则使用默认
    vibe_config = VIBE_ROUTING_TABLE.get(vibe, VIBE_ROUTING_TABLE["neutral_narrate"])
    
    if use_volcengine:
        # 使用火山引擎：直接调用，通过音色切换实现情绪
        voice_id = vibe_config["volc_voice"]
        success = call_volcengine_tts(text, voice_id, output_file)
        return success
    else:
        # 使用 Edge TTS：通过参数控制
        params = vibe_config["edge_params"]
        try:
            communicate = edge_tts.Communicate(
                text, 
                "zh-CN-YunxiNeural",  # 基础音色
                rate=params["rate"],
                pitch=params["pitch"],
                volume=params["volume"]
            )
            await communicate.save(output_file)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return True
            else:
                return False
        except Exception as e:
            st.warning(f"⚠️ 情绪片段 [{vibe}] 生成失败: {e}")
            return False

async def synthesize_emotional_segments_parallel(segments, use_volcengine=False):
    """
    并行合成多个情绪片段（核心加速逻辑）
    
    Args:
        segments: 片段列表 [{"text": "...", "vibe": "..."}, ...]
        use_volcengine: 是否使用火山引擎
    
    Returns:
        list: 成功生成的音频文件路径列表
    """
    tasks = []
    output_files = []
    
    for i, seg in enumerate(segments):
        output_file = f"temp_emotional_segment_{i}_{uuid.uuid4().hex[:8]}.mp3"
        output_files.append(output_file)
        
        # 创建并行任务
        task = synthesize_emotional_segment(
            text=seg.get("text", ""),
            vibe=seg.get("vibe", "neutral_narrate"),
            output_file=output_file,
            use_volcengine=use_volcengine
        )
        tasks.append(task)
    
    # 🚀 关键：并行执行所有任务（5个片段 = 1个片段的时间）
    st.info(f"🎬 并行合成 {len(segments)} 个情绪片段...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 验证结果
    success_files = []
    for i, (result, file) in enumerate(zip(results, output_files)):
        if result is True and os.path.exists(file):
            success_files.append(file)
            st.success(f"✅ 片殶 {i+1}/{len(segments)}: {segments[i].get('vibe', 'neutral')} - 成功")
        else:
            st.error(f"❌ 片殶 {i+1}/{len(segments)}: 失败")
            success_files.append(None)
    
    return success_files

def concatenate_audio_segments_with_breath(audio_files, output_path, breath_duration=0.2):
    """
    拼接音频片段，并在接缝处插入呼吸停顿（增强真人感）
    
    Args:
        audio_files: 音频文件路径列表
        output_path: 输出文件路径
        breath_duration: 呼吸停顿时长（秒）
    
    Returns:
        str: 输出文件路径，失败返回 None
    """
    try:
        # 加载所有有效的音频片殶
        clips = []
        for i, file in enumerate(audio_files):
            if file and os.path.exists(file):
                try:
                    clip = AudioFileClip(file)
                    clips.append(clip)
                    
                    # 在片殶之间插入静音（模拟呼吸）
                    if i < len(audio_files) - 1:  # 不在最后一个后面加
                        # 创建静音片殶
                        silence = AudioFileClip(file).volumex(0).subclip(0, breath_duration)
                        clips.append(silence)
                except Exception as e:
                    st.warning(f"⚠️ 片殶 {i+1} 加载失败: {e}")
        
        if not clips:
            st.error("❌ 没有有效的音频片殶")
            return None
        
        # 🎵 拼接所有片殶
        final_audio = concatenate_audioclips(clips)
        final_audio.write_audiofile(output_path, codec='libmp3lame')
        
        # 清理临时文件
        for clip in clips:
            clip.close()
        for file in audio_files:
            if file and os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
        
        st.success(f"✅ 音频拼接完成，共 {len(clips)} 个片殶")
        return output_path
        
    except Exception as e:
        st.error(f"❌ 音频拼接失败: {e}")
        return None

def generate_all_audios_sync(scenes_data, voice_id="zh-CN-YunxiNeural"):
    """串行生成所有分镜配音"""
    audio_files = []
    failed_count = 0
    
    for i, scene in enumerate(scenes_data):
        audio_file = f"temp_audio_{i}.mp3"
        st.toast(f"🎹️ AI 配音生成中... {i+1}/{len(scenes_data)}")
        
        # 🔥 新增：显示当前处理的文本（前50个字符）
        narration_preview = scene['narration'][:50] + "..." if len(scene['narration']) > 50 else scene['narration']
        st.caption(f"📝 正在处理: {narration_preview}")
        
        try:
            success = asyncio.run(text_to_mp3(scene['narration'], audio_file, voice_id))
            if success:
                audio_files.append(audio_file)
                st.success(f"✅ 分镜 {i+1} 音频生成成功")
            else:
                audio_files.append(None)
                failed_count += 1
                st.error(f"❌ 分镜 {i+1} 音频生成失败")
        except Exception as e:
            audio_files.append(None)
            failed_count += 1
            st.error(f"❌ 分镜 {i+1} 音频生成异常: {e}")
        
        asyncio.run(asyncio.sleep(0.5))
    
    # 🔥 新增：显示总结
    if failed_count > 0:
        st.warning(f"⚠️ 音频生成完成，但有 {failed_count}/{len(scenes_data)} 个失败")
    else:
        st.success(f"✅ 所有 {len(scenes_data)} 个音频生成成功！")
    
    return audio_files

def render_ai_video_pipeline(scenes_data, zhipu_key, output_path, pexels_key=None, voice_id="zh-CN-YunxiNeural", style_name=None):
    """核心视频渲染管线
    
    Args:
        scenes_data: 分镜数据列表
        zhipu_key: 智谱 API Key
        output_path: 输出视频路径
        pexels_key: Pexels API Key
        voice_id: 声音 ID
        style_name: 风格名称（用于匹配 BGM）
    """
    from api_services import generate_images_zhipu
    
    # 1. 资源生成
    image_paths = generate_images_zhipu(scenes_data, zhipu_key)
    audio_files = generate_all_audios_sync(scenes_data, voice_id)  # 传递 voice_id
    
    # 🔍 调试信息：显示成功生成的图片数量
    success_count = sum(1 for p in image_paths if p)
    st.write(f"📸 成功生成图片数量: {success_count}/{len(image_paths)}")
    
    # 🔍 新增：调试音频文件状态
    audio_success_count = sum(1 for a in audio_files if a and os.path.exists(a))
    st.write(f"🎹️ 成功生成音频数量: {audio_success_count}/{len(audio_files)}")
    
    # 🔥 关键修复：如果所有音频都失败，直接返回错误
    if audio_success_count == 0:
        st.error("❌ 所有音频生成失败！请检查网络连接或TTS配置")
        return False
    
    scene_clips = []
    temp_files = []

    # 2. 逐分镜合成
    for i, scene in enumerate(scenes_data):
        # 🔥 修复：先检查audio_files[i]是否为None，再检查文件是否存在
        if not audio_files[i] or not os.path.exists(audio_files[i]): 
            st.warning(f"⚠️ 分镜 {i+1} 音频生成失败或文件不存在，跳过")
            continue
            
        try:
            audio_clip = AudioFileClip(audio_files[i])
            dur = audio_clip.duration
            temp_files.append(audio_files[i])
        except Exception as e:
            st.error(f"❌ 分镜 {i+1} 音频加载失败: {e}")
            continue
        
        # 画面逻辑：AI绘画 > 黑屏占位
        if image_paths[i]:
            st.write(f"🖼️ 分镜 {i+1} 使用AI绘画: {image_paths[i]}")
            try:
                # 🔑 核心修复：用 Pillow 预处理图片，避免 MoviePy 的 resize 触发 ANTIALIAS
                from PIL import Image as PILImage
                img = PILImage.open(image_paths[i])
                
                # 计算缩放比例（目标高度 1920）
                scale = 1920 / img.height
                new_width = int(img.width * scale)
                
                # 使用 Pillow 的 LANCZOS 重采样（兼容新旧版本）
                try:
                    # Pillow >= 10.0.0
                    img_resized = img.resize((new_width, 1920), PILImage.Resampling.LANCZOS)
                except AttributeError:
                    # Pillow < 10.0.0
                    img_resized = img.resize((new_width, 1920), PILImage.LANCZOS)
                
                # 裁剪到 1080x1920（居中裁剪）
                left = (new_width - 1080) // 2
                img_cropped = img_resized.crop((left, 0, left + 1080, 1920))
                
                # 转为 numpy 数组，传给 MoviePy（不再调用 resize）
                img_array = np.array(img_cropped)
                bg = ImageClip(img_array).set_duration(dur)
                temp_files.append(image_paths[i])
                st.success(f"✅ 分镜 {i+1} 图片处理成功")
            except Exception as e:
                st.error(f"❌ 分镜 {i+1} 图片加载失败: {e}，使用黑屏占位")
                bg = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(dur)
        else:
            st.write(f"⚫ 分镜 {i+1} 图片为空，使用黑屏占位")
            # 🔑 修复：使用 ColorClip 创建纯黑背景
            bg = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(dur)

        # 🎨 字幕逻辑：用 Pillow 手工绘制 + 正确处理透明度
        subtitle_rgba = create_subtitle_image(scene['narration'], width=1080, height=400, fontsize=70)
        
        # 🔑 核心修复：拆分 RGB 和 Alpha 通道，确保透明度正确
        # RGBA 数组的前3个通道是颜色，第4个通道是透明度
        rgb_array = subtitle_rgba[:, :, :3]  # 取前3个通道（RGB）
        alpha_array = subtitle_rgba[:, :, 3] / 255.0  # 取第4个通道（Alpha），归一化到0-1
        
        # 创建字幕图层，明确指定 mask
        txt_clip = ImageClip(rgb_array).set_duration(dur)
        txt_clip = txt_clip.set_mask(ImageClip(alpha_array, ismask=True).set_duration(dur))
        txt_clip = txt_clip.set_position(('center', 0.75), relative=True)
        
        scene_clips.append(CompositeVideoClip([bg, txt_clip]).set_audio(audio_clip))

    # 3. 最终压制与 BGM 混音
    if not scene_clips: return False
    
    final = concatenate_videoclips(scene_clips, method="compose")
    
    # 🎵 使用新的 BGM 风格路由系统
    if style_name:
        st.write(f"🎵 根据 {style_name} 风格匹配 BGM...")
        bgm_clip = get_bgm_by_style(style_name, final.duration)
        if bgm_clip:
            # 混合人声和 BGM
            final = final.set_audio(CompositeAudioClip([
                final.audio.volumex(1.2),  # 稍微调高人声，确保清晰
                bgm_clip
            ]))
        else:
            st.warning("⚠️ BGM 加载失败，使用原始音频")
    else:
        # 如果没有指定风格，尝试使用默认 BGM（兼容旧版本）
        default_bgm_paths = ["assets/bgm.mp3", "bgm.mp3"]
        bgm_path = None
        for path in default_bgm_paths:
            if os.path.exists(path):
                bgm_path = path
                break
        
        if bgm_path:
            st.info("🎵 使用默认 BGM")
            bgm = AudioFileClip(bgm_path).volumex(0.08).set_duration(final.duration)
            final = final.set_audio(CompositeAudioClip([final.audio, bgm]))

    # 4. 导出 (优化参数防止云端内存溢出)
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", 
                          threads=4, preset="ultrafast", logger=None)
    
    # 5. 资源清理
    final.close()
    for f in temp_files:
        if f and os.path.exists(f): 
            try: os.remove(f)
            except: pass
    return True

# 🎬 导演时间轴引擎 (Director's Timeline Engine)
class VideoAssembler:
    """
    基于 Manifest JSON 的一键混剪引擎
    解决音画同步、SFX自动匹配、情绪语音等核心问题
    """
    
    # 🔊 音效库路由表
    SFX_LIBRARY = {
        "heartbeat_heavy": "assets/sfx/heartbeat_heavy.mp3",
        "glass_shatter": "assets/sfx/glass_shatter.mp3",
        "whoosh": "assets/sfx/whoosh.mp3",
        "tension_riser": "assets/sfx/tension_riser.mp3",
        "emotional_swell": "assets/sfx/emotional_swell.mp3",
        "silence": None  # 静音，不加载音效
    }
    
    def __init__(self, manifest_data, voice_id="zh-CN-YunxiNeural", use_volcengine=False):
        """
        Args:
            manifest_data: 导演时间轴 JSON 列表
            voice_id: TTS 音色 ID
            use_volcengine: 是否使用火山引擎
        """
        self.manifest = manifest_data
        self.voice_id = voice_id
        self.use_volcengine = use_volcengine
        self.validate_manifest()
    
    def validate_manifest(self):
        """验证 Manifest 格式合法性"""
        required_fields = ["start_time", "end_time", "narration", "emotion_vibe", "image_prompt"]
        
        for i, segment in enumerate(self.manifest):
            for field in required_fields:
                if field not in segment:
                    raise ValueError(f"分镜 {i+1} 缺少必要字段: {field}")
            
            # 验证时间连续性
            if i > 0:
                prev_end = self.manifest[i-1]["end_time"]
                curr_start = segment["start_time"]
                if curr_start != prev_end:
                    st.warning(f"⚠️ 时间轴不连续：分镜{i} 结束于 {prev_end}s，但分镜{i+1} 开始于 {curr_start}s")
        
        st.success(f"✅ Manifest 验证通过：{len(self.manifest)} 个分镜，总时长 {self.manifest[-1]['end_time']}s")
    
    async def synthesize_segment_with_emotion(self, segment, output_file):
        """
        根据 emotion_vibe 合成单个音频片段
        """
        text = segment["narration"]
        vibe = segment.get("emotion_vibe", "neutral_narrate")
        
        # 调用片段式情绪引擎
        success = await synthesize_emotional_segment(
            text=text,
            vibe=vibe,
            output_file=output_file,
            use_volcengine=self.use_volcengine
        )
        
        return success
    
    async def synthesize_all_audio_parallel(self):
        """
        并行合成所有音频片段
        Returns: [(audio_file, sfx_file, start, end), ...]
        """
        tasks = []
        audio_info = []
        
        for i, segment in enumerate(self.manifest):
            audio_file = f"temp_timeline_audio_{i}_{uuid.uuid4().hex[:8]}.mp3"
            audio_info.append({
                "audio_file": audio_file,
                "sfx": segment.get("sfx"),
                "start": segment["start_time"],
                "end": segment["end_time"]
            })
            
            task = self.synthesize_segment_with_emotion(segment, audio_file)
            tasks.append(task)
        
        # 🚀 并行执行
        st.info(f"🎬 并行合成 {len(tasks)} 个情绪音频片段...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证结果
        success_info = []
        for i, (result, info) in enumerate(zip(results, audio_info)):
            if result is True and os.path.exists(info["audio_file"]):
                success_info.append(info)
                emotion = self.manifest[i].get("emotion_vibe", "neutral")
                st.success(f"✅ 分镜 {i+1}: {emotion} - 音频合成成功")
            else:
                st.error(f"❌ 分镜 {i+1}: 音频合成失败")
        
        return success_info
    
    def load_sfx(self, sfx_name):
        """
        加载音效文件
        Returns: AudioFileClip 或 None
        """
        if not sfx_name or sfx_name == "silence":
            return None
        
        sfx_path = self.SFX_LIBRARY.get(sfx_name)
        if sfx_path and os.path.exists(sfx_path):
            try:
                return AudioFileClip(sfx_path)
            except Exception as e:
                st.warning(f"⚠️ 音效 {sfx_name} 加载失败: {e}")
        else:
            st.warning(f"⚠️ 音效 {sfx_name} 不存在")
        
        return None
    
    def assemble_timeline_audio(self, audio_info_list, output_path):
        """
        按照时间轴组装音频（包括 TTS + SFX）
        """
        try:
            audio_clips = []
            
            for info in audio_info_list:
                # 加载 TTS 音频
                if os.path.exists(info["audio_file"]):
                    tts_clip = AudioFileClip(info["audio_file"])
                    
                    # 加载 SFX
                    sfx_clip = self.load_sfx(info["sfx"])
                    
                    if sfx_clip:
                        # 混合 TTS + SFX
                        combined = CompositeAudioClip([tts_clip, sfx_clip.volumex(0.3)])
                        audio_clips.append(combined)
                    else:
                        audio_clips.append(tts_clip)
            
            if not audio_clips:
                st.error("❌ 没有有效的音频片段")
                return None
            
            # 🎵 拼接所有片殶
            final_audio = concatenate_audioclips(audio_clips)
            final_audio.write_audiofile(output_path, codec='libmp3lame')
            
            # 清理临时文件
            for clip in audio_clips:
                clip.close()
            for info in audio_info_list:
                if os.path.exists(info["audio_file"]):
                    try:
                        os.remove(info["audio_file"])
                    except:
                        pass
            
            st.success(f"✅ 时间轴音频组装完成，共 {len(audio_clips)} 个片殶")
            return output_path
            
        except Exception as e:
            st.error(f"❌ 音频组装失败: {e}")
            return None
    
    async def render_video_from_manifest(self, output_path="final_video.mp4", bgm_style=None):
        """
        🎬 一键混剪：从 Manifest 生成完整视频
        """
        st.info("🎬 开始基于导演时间轴的视频渲染...")
        
        # 1. 并行合成所有音频
        audio_info_list = await self.synthesize_all_audio_parallel()
        
        if not audio_info_list:
            st.error("❌ 音频合成失败")
            return False
        
        # 2. 组装时间轴音频（TTS + SFX）
        timeline_audio = self.assemble_timeline_audio(audio_info_list, "temp_timeline_audio.mp3")
        
        if not timeline_audio:
            return False
        
        # 3. TODO: 生成图片并组装视频（复用现有 render_ai_video_pipeline 逻辑）
        # 这里暂时返回成功，完整实现需要整合图片生成和 MoviePy 渲染
        st.success("✅ 时间轴音频生成成功！")
        st.info("🚧 视频渲染功能待完善，当前仅生成音频轨")
        
        return True
