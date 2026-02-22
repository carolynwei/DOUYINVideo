import os
from moviepy.editor import ColorClip

# 1. 制造极简 Mock 数据
mock_scenes = [
    {"narration": "这是第一句测试，验证防超时串行配音是否正常。", "image_prompt": "A futuristic city"},
    {"narration": "这是第二句测试，验证奇偶推拉运镜与字幕渲染。", "image_prompt": "A cat sleeping"}
]

# 2. 模拟智谱画图：在本地生成两张纯色假图片
def mock_generate_images(scenes, key):
    img_paths = []
    for i in range(len(scenes)):
        temp_name = f"temp_mock_{i}.jpg"
        color = (100, 149, 237) if i == 0 else (220, 20, 60)
        ColorClip(size=(1080, 1920), color=color, duration=1).save_frame(temp_name, t=0)
        img_paths.append(temp_name)
    return img_paths

# 拦截(Monkey Patch)真实的画图请求，用我们的假函数替代
import api_services
api_services.generate_images_zhipu = mock_generate_images

# 3. 运行管线
if __name__ == "__main__":
    path = r"E:\ImageMagick-7.1.2-Q16-HDRI\magick.exe" # 这里填你的真实路径
    print(f"🔍 正在检查路径是否存在: {os.path.exists(path)}")
    os.environ["IMAGEMAGICK_BINARY"] = path

    from video_engine import render_ai_video_pipeline
    
    # 提前准备好 ImageMagick 环境
    os.environ["IMAGEMAGICK_BINARY"] = r"E:\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

    print("🚀 开始极速 Mock 测试流水线...")
    success = render_ai_video_pipeline(
        scenes_data=mock_scenes, 
        zhipu_key="fake_key", 
        output_path="test_output.mp4"
    )
    
    if success:
        print("\n✅ 测试完美通过！本地已生成 test_output.mp4")
    else:
        print("\n❌ 渲染失败，请检查报错日志。")