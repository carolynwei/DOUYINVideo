import os
import platform
import asyncio
import edge_tts
import streamlit as st
from moviepy.editor import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

# 🔑 环境自适应配置：自动识别 Linux 云端或 Windows 本地
if platform.system() == "Linux":
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"  # 云端路径
else:
    # 这里的路径需与你本地安装路径一致
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

async def text_to_mp3(text, filename):
    """【云端优化版】直接联网生成配音，增加重试逻辑"""
    for attempt in range(3):
        try:
            # 删除了 proxy 参数，云端直连速度极快
            communicate = edge_tts.Communicate(text, "zh-CN-YunxiNeural", rate="+10%")
            await communicate.save(filename)
            return True
        except Exception as e:
            print(f"TTS 尝试 {attempt+1}/3 失败: {e}")
            await asyncio.sleep(2)
    return False

def generate_all_audios_sync(scenes_data):
    """串行生成所有分镜配音"""
    audio_files = []
    for i, scene in enumerate(scenes_data):
        audio_file = f"temp_audio_{i}.mp3"
        st.toast(f"🎙️ AI 配音生成中... {i+1}/{len(scenes_data)}")
        if asyncio.run(text_to_mp3(scene['narration'], audio_file)):
            audio_files.append(audio_file)
        else:
            # 失败兜底逻辑
            audio_files.append(None)
        asyncio.run(asyncio.sleep(0.5))
    return audio_files

def render_ai_video_pipeline(scenes_data, zhipu_key, output_path, pexels_key=None):
    """核心视频渲染管线"""
    from api_services import generate_images_zhipu
    
    # 1. 资源生成
    image_paths = generate_images_zhipu(scenes_data, zhipu_key)
    audio_files = generate_all_audios_sync(scenes_data)
    
    scene_clips = []
    temp_files = []

    # 2. 逐分镜合成
    for i, scene in enumerate(scenes_data):
        if not audio_files[i]: continue
            
        audio_clip = AudioFileClip(audio_files[i])
        dur = audio_clip.duration
        temp_files.append(audio_files[i])
        
        # 画面逻辑：AI绘画 > 黑屏占位
        if image_paths[i]:
            bg = ImageClip(image_paths[i]).set_duration(dur).resize(height=1920).crop(x_center=1080/2, width=1080)
            temp_files.append(image_paths[i])
        else:
            bg = ImageClip("black", duration=dur).resize((1080, 1920))

        # 字幕逻辑
        txt = TextClip(scene['narration'], fontsize=70, color='white', font='SimHei',
                       method='caption', size=(900, None), stroke_color='black', stroke_width=2)
        txt = txt.set_duration(dur).set_position(('center', 0.8), relative=True)
        
        scene_clips.append(CompositeVideoClip([bg, txt]).set_audio(audio_clip))

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
