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
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from moviepy.editor import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

# 🔑 字体路径配置：多级降级策略确保100%可用
def get_font_path():
    """智能检测可用的中文字体路径"""
    # 1. 优先：仓库中的字体文件（绝对路径）
    repo_font = os.path.join(os.path.dirname(__file__), "font.ttf")
    if os.path.exists(repo_font):
        return repo_font
    
    # 2. 降级：当前工作目录的字体文件
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
            print(f"❌ 找不到火山引擎 V3 脚本: {script_path}")
            return False
        
        print(f"🚀 正在调用豆包语音合成大模型: {voice_id}...")
        
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
            print(f"✅ 豆包大模型音频流接收完毕！音频已保存至: {output_path}")
            return True
        else:
            print(f"❌ 输出文件未生成或为空: {output_path}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 火山引擎 TTS 超时（60秒）")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ 火山大模型合成失败，官方脚本报错信息：")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ 火山引擎 TTS 调用异常: {e}")
        return False

async def text_to_mp3(text, filename, voice_id="zh-CN-YunxiNeural"):
    """【云端优化版】直接联网生成配音，增加重试逻辑。支持多路 TTS 路由。"""
    
    # 🎙️ 路由 1：火山引擎 TTS (方言 + 高情绪表达)
    if voice_id.startswith("volc_"):
        # 去掉前缀，获取真实的音色 ID
        real_voice_id = voice_id.replace("volc_", "")
        success = call_volcengine_tts(text, real_voice_id, filename)
        if success:
            return True
        else:
            # 火山引擎失败，回退到 Edge TTS
            print("⚠️ 火山引擎不可用，回退到 Edge TTS 模式")
            voice_id = "zh-CN-YunxiNeural"  # 使用默认男声
    
    # 🎙️ 路由 2：Edge TTS (免费兜底)
    for attempt in range(3):
        try:
            # 删除了 proxy 参数，云端直连速度极快
            communicate = edge_tts.Communicate(text, voice_id, rate="+10%")
            await communicate.save(filename)
            return True
        except Exception as e:
            print(f"TTS 尝试 {attempt+1}/3 失败: {e}")
            await asyncio.sleep(2)
    return False

def generate_all_audios_sync(scenes_data, voice_id="zh-CN-YunxiNeural"):
    """串行生成所有分镜配音"""
    audio_files = []
    for i, scene in enumerate(scenes_data):
        audio_file = f"temp_audio_{i}.mp3"
        st.toast(f"🎙️ AI 配音生成中... {i+1}/{len(scenes_data)}")
        if asyncio.run(text_to_mp3(scene['narration'], audio_file, voice_id)):
            audio_files.append(audio_file)
        else:
            # 失败兜底逻辑
            audio_files.append(None)
        asyncio.run(asyncio.sleep(0.5))
    return audio_files

def render_ai_video_pipeline(scenes_data, zhipu_key, output_path, pexels_key=None, voice_id="zh-CN-YunxiNeural"):
    """核心视频渲染管线"""
    from api_services import generate_images_zhipu
    
    # 1. 资源生成
    image_paths = generate_images_zhipu(scenes_data, zhipu_key)
    audio_files = generate_all_audios_sync(scenes_data, voice_id)  # 传递 voice_id
    
    # 🔍 调试信息：显示成功生成的图片数量
    success_count = sum(1 for p in image_paths if p)
    st.write(f"📸 成功生成图片数量: {success_count}/{len(image_paths)}")
    
    scene_clips = []
    temp_files = []

    # 2. 逐分镜合成
    for i, scene in enumerate(scenes_data):
        if not audio_files[i]: 
            st.warning(f"⚠️ 分镜 {i+1} 音频生成失败，跳过")
            continue
            
        audio_clip = AudioFileClip(audio_files[i])
        dur = audio_clip.duration
        temp_files.append(audio_files[i])
        
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
    
    if os.path.exists("bgm.mp3"):
        bgm = AudioFileClip("bgm.mp3").volumex(0.08).set_duration(final.duration)
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
