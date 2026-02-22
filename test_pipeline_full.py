# -*- coding: utf-8 -*-
"""
完整流水线测试脚本
目标:不使用真实 API Key,通过 Mock 数据测试整个视频生成流程
"""

import os
import sys
import numpy as np
from PIL import Image
import asyncio

# 尝试导入 scipy，如果不存在则使用替代方案
try:
    from scipy.io import wavfile
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("⚠️ scipy 未安装，使用替代方案生成音频")

print("=" * 80)
print("抖音 AI 视频工具 - 完整流水线测试")
print("=" * 80)

# ==========================================
# Step 1: 准备 Mock 剧本数据
# ==========================================
print("\n[Step 1] 准备 Mock 剧本数据...")

mock_scenes_data = [
    {
        "narration": "这就是今天的爆款秘密!",
        "image_prompt": "A dramatic close-up shot of a shocked Asian young woman, cinematic lighting, 8k, photorealistic"
    },
    {
        "narration": "你根本想不到真相是什么!",
        "image_prompt": "A futuristic cyberpunk city street with neon lights, rainy atmosphere, cinematic composition"
    },
    {
        "narration": "看完这个你会感谢我!",
        "image_prompt": "A beautiful sunset over mountains, golden hour lighting, wide angle landscape, professional photography"
    }
]

print(f"✓ Mock 剧本已准备: {len(mock_scenes_data)} 个分镜")
for i, scene in enumerate(mock_scenes_data):
    print(f"  分镜 {i+1}: {scene['narration'][:30]}...")

# ==========================================
# Step 2: 生成本地测试图片 (模拟智谱AI)
# ==========================================
print("\n[Step 2] 生成本地测试图片...")

def create_mock_image(index, color, text):
    """生成带文字的测试图片"""
    # 创建 1080x1920 竖屏图片
    img = Image.new('RGB', (1080, 1920), color=color)
    
    # 保存文件
    filename = f"temp_scene_{index}.jpg"
    img.save(filename)
    print(f"✓ 已生成测试图片 {index+1}: {filename} (颜色: {color})")
    return filename

# 生成三张不同颜色的测试图
test_colors = [
    (100, 149, 237),  # 蓝色
    (220, 20, 60),    # 红色
    (34, 139, 34)     # 绿色
]

test_images = []
for i, color in enumerate(test_colors):
    img_path = create_mock_image(i, color, f"分镜 {i+1}")
    test_images.append(img_path)

# ==========================================
# Step 3: 生成本地测试音频 (模拟 Edge TTS)
# ==========================================
print("\n[Step 3] 生成本地静默音频...")

def create_mock_audio(index, duration=3):
    """生成静默音频文件"""
    audio_file = f"temp_audio_{index}.mp3"
    wav_file = f"temp_audio_{index}.wav"
    
    # 生成静默 WAV
    sample_rate = 44100
    silence = np.zeros(int(sample_rate * duration), dtype=np.int16)
    
    if HAS_SCIPY:
        wavfile.write(wav_file, sample_rate, silence)
    else:
        # 使用标准库 wave 模块
        import wave
        with wave.open(wav_file, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(silence.tobytes())
    
    # 尝试转换为 MP3
    try:
        import subprocess
        subprocess.run(
            ['ffmpeg', '-i', wav_file, '-ar', '44100', '-ac', '2', '-b:a', '192k', audio_file, '-y'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=10
        )
        os.remove(wav_file)
        print(f"✓ 已生成测试音频 {index+1}: {audio_file} (MP3)")
        return audio_file
    except:
        # ffmpeg 失败,使用 WAV
        print(f"✓ 已生成测试音频 {index+1}: {wav_file} (WAV - ffmpeg不可用)")
        return wav_file

test_audios = []
for i in range(len(mock_scenes_data)):
    audio_path = create_mock_audio(i, duration=3)
    test_audios.append(audio_path)

# ==========================================
# Step 4: Monkey Patch 核心模块
# ==========================================
print("\n[Step 4] Monkey Patch API 模块...")

# 导入核心模块
import api_services
import video_engine

# 4.1 Mock 智谱 AI 图片生成
original_generate_images = api_services.generate_images_zhipu

def mock_generate_images(scenes_data, api_key):
    """返回本地测试图片"""
    print("✓ [Mock] 跳过智谱 AI 调用,使用本地测试图片")
    return test_images

api_services.generate_images_zhipu = mock_generate_images

# 4.2 Mock 音频生成函数
original_generate_audios = video_engine.generate_all_audios_sync

def mock_generate_audios(scenes_data, voice_id="zh-CN-YunxiNeural"):
    """返回本地测试音频"""
    print("✓ [Mock] 跳过 Edge TTS 调用,使用本地测试音频")
    return test_audios

video_engine.generate_all_audios_sync = mock_generate_audios

# 4.3 Mock Streamlit 的 toast/info/success 等方法
class MockStreamlit:
    @staticmethod
    def toast(msg):
        print(f"  [Toast] {msg}")
    
    @staticmethod
    def info(msg):
        print(f"  [Info] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"  [Success] {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"  [Warning] {msg}")
    
    @staticmethod
    def error(msg):
        print(f"  [Error] {msg}")
    
    @staticmethod
    def write(msg):
        print(f"  [Write] {msg}")

# 替换 api_services 和 video_engine 中的 st
api_services.st = MockStreamlit()
video_engine.st = MockStreamlit()

print("✓ Mock 模块注入完成")

# ==========================================
# Step 5: 调用核心渲染引擎
# ==========================================
print("\n[Step 5] 调用视频渲染引擎...")

output_file = "test_output_full.mp4"

# 清理旧的测试输出
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"✓ 已清理旧的测试输出")

print("\n" + "=" * 80)
print("开始渲染流水线 (预计 30-60 秒)...")
print("=" * 80 + "\n")

# 虚拟 API Keys
fake_zhipu_key = "mock_zhipu_key_12345"
fake_pexels_key = None

try:
    # 调用核心渲染函数
    success = video_engine.render_ai_video_pipeline(
        scenes_data=mock_scenes_data,
        zhipu_key=fake_zhipu_key,
        output_path=output_file,
        pexels_key=fake_pexels_key,
        voice_id="zh-CN-YunxiNeural"
    )
    
    # 检查结果
    if success and os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print("\n" + "=" * 80)
        print("✅ 测试成功！视频已生成！")
        print("=" * 80)
        print(f"输出文件: {output_file}")
        print(f"文件大小: {file_size:.2f} MB")
        print("\n请播放 test_output_full.mp4 验证效果")
        print("\n测试覆盖:")
        print("  ✓ API 服务模块 (Mock)")
        print("  ✓ 图片生成 (本地图片)")
        print("  ✓ 音频合成 (本地音频)")
        print("  ✓ 视频渲染引擎")
        print("  ✓ 字幕烧录")
        print("  ✓ 最终压制")
    else:
        print("\n" + "=" * 80)
        print("❌ 渲染失败,未生成视频文件")
        print("=" * 80)
        sys.exit(1)
        
except Exception as e:
    print("\n" + "=" * 80)
    print("❌ 发生异常:")
    print("=" * 80)
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    # ==========================================
    # Step 6: 清理临时文件
    # ==========================================
    print("\n[Step 6] 清理临时文件...")
    
    temp_files = test_images + test_audios
    cleaned_count = 0
    
    for f in temp_files:
        if f and os.path.exists(f):
            try:
                os.remove(f)
                cleaned_count += 1
            except:
                pass
    
    print(f"✓ 已清理 {cleaned_count} 个临时文件")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
