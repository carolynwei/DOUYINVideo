import os
import re
import json
import requests
import urllib.request
import streamlit as st
from openai import OpenAI

def get_hot_topics(api_key):
    """获取抖音热搜榜单"""
    url = 'https://apis.tianapi.com/douyinhot/index'.strip()
    try:
        res = requests.post(url, data={'key': api_key}, 
                          headers={'Content-type': 'application/x-www-form-urlencoded'}, 
                          timeout=10)
        data = res.json()
        if data.get('code') == 200:
            return [item['word'] for item in data['result']['list'][:10]]
        return []
    except Exception as e:
        st.error(f"热搜接口异常: {e}")
        return []

def generate_script_json(topic, api_key):
    """使用 DeepSeek 生成剧本"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    system_prompt = """你是一位短视频导演。请根据热搜创作分镜脚本。
    必须严格输出 JSON 数组，包含 4-6 个分镜。格式：[{"narration": "...", "image_prompt": "..."}]"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": f"主题：{topic}"}],
            temperature=0.7,
            response_format={'type': 'json_object'}
        )
        content = response.choices[0].message.content
        clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
        scenes = json.loads(clean_content)
        if isinstance(scenes, dict):
            for v in scenes.values():
                if isinstance(v, list): return v
        return scenes
    except Exception as e:
        st.error(f"剧本生成失败: {e}")
        return []

def generate_viral_script(topic, api_key):
    """🔥 使用爆款剧本大师 Agent 生成高能量脚本 (注入完整 Skill)"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 🎯 终极爆款剧本大师 System Prompt (深度注入运营日记精髓)
    viral_system_prompt = """你是全网最顶尖的抖音爆款视频制作人、深谙人性的"认知刺客"。你精通算法推流底层逻辑（完播率>30%，点赞率>5%）。你的任务是根据用户主题，输出一套招招致命、毫无废话的爆款短视频脚本与分镜。

**【核心知识库与强制执行规则】**

**1. 情绪收割与心理学武器（必须选用至少1个作为底层逻辑）：**
- 契可尼效应：制造留白与遗憾。痛苦选题优于快乐（如：没考上的学校）。故事不要讲完，给观众想象空间。
- 损失厌恶：暗示"错过这条视频就是你的损失"。强调折现价值和带来改变的方法。
- 巴纳姆效应：使用笼统但极易对号入座的人格描述，拉满群体共鸣。
- 富兰克林效应：设定"听劝/求助"的养成系人设，引发网友指导欲。
- 从众效应：预设热点BGM或洗脑梗，制造围观。

**2. "认知刺客"文案法则（必须严格执行"三步删改法"）：**
- 【第一步：删除废话】：绝对禁用"那么、其实、众所周知、接下来我给大家讲、我觉得"等连接词。直接上结论！
- 【第二步：名词/动词替换】：拒绝模糊形容词！把"很生气"改为"把手机狠狠摔在墙上"；把"速度快"改为"推背感把你死死按在座椅上"。
- 【第三步：高频钩子与密度】：
  -> 黄金前3秒：必须是强视觉冲突 + 悬念预示（例如："这碗面卖88块，我要看看他怎么退钱"），绝不铺垫！
  -> 正文节奏：每15秒1个记忆点，每隔三句话必须埋入一个新钩子（提问、反转或预告）。
- 【刺客心法】：别当温吞的科普机器。敢下狠话直戳痛处（如"你不是内耗，你是懒"）；讲真实血肉的故事，不讲干板逻辑。

**3. 爆款视觉与分镜法则：**
- 画面Prompt必须像"导演分镜单"，包含：主体、动作、场景、光线、镜头语言。
- 必须融入顶级大师审美（如：Sam Kolder的电影感与转场、Brandon Li的粗粝手持纪实、Daniel Schiffer的商业光影微距）。

**【严格输出格式要求】**
必须严格输出纯 JSON 数组，包含 4-6 个高能量分镜，不要输出任何 Markdown 标记（如 ```json）或其他解释性文字。格式如下：
[
  {
    "narration": "刺客文案（第一句必须是极具冲击力的黄金3秒Hook，后续文案严格运用三步删改法，高能量密度）",
    "image_prompt": "导演级分镜提示词（必须全英文，包含光影、运镜及上述大师风格，如 'Brandon Li style, hand-held tracking shot...'）"
  }
]"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": viral_system_prompt},
                {"role": "user", "content": f"主题：{topic}\n\n请严格运用上述心理学武器和刺客文案法则，输出纯 JSON 数组格式的分镜脚本。"}
            ],
            temperature=0.8,  # 保持0.8以获得高创造性和情绪张力
            response_format={'type': 'json_object'} # 强制 JSON 模式
        )
        
        content = response.choices[0].message.content
        # 深度清理可能的 markdown 符号，确保 JSON 解析不出错
        clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
        scenes = json.loads(clean_content)
        
        # 兼容 DeepSeek JSON 模式可能返回 {"scenes": [...]} 的情况
        if isinstance(scenes, dict):
            for v in scenes.values():
                if isinstance(v, list): 
                    return v
        
        return scenes if isinstance(scenes, list) else []
        
    except Exception as e:
        st.error(f"爆款剧本生成失败: {e}")
        return []

def generate_images_zhipu(scenes_data, api_key):
    """调用智谱 CogView-3-Plus"""
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations".strip()  # 🔑 核心修复：清理URL
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    image_paths = []
    
    for i, scene in enumerate(scenes_data):
        payload = {"model": "cogview-3-plus", "prompt": scene['image_prompt'], "size": "1080x1920"}
        st.toast(f"🎨 正在绘制分镜 {i+1}/{len(scenes_data)} ...")
        
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=60).json()
            if 'data' in res:
                img_url = res['data'][0]['url']
                temp_name = f"temp_scene_{i}.jpg"
                urllib.request.urlretrieve(img_url, temp_name)
                image_paths.append(temp_name)
            else:
                image_paths.append(None)
        except:
            image_paths.append(None)
    return image_paths

def get_pexels_videos(query, api_key, required_duration):
    """Pexels API 真实素材兜底"""
    url = "https://api.pexels.com/videos/search".strip()
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 5, "orientation": "portrait"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if not data.get('videos'):
            params['query'] = "nature landscape"  # 英文风景保底
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()

        downloaded_files = []
        current_dur = 0.0
        from moviepy.editor import VideoFileClip
        
        for i, video in enumerate(data.get('videos', [])):
            if current_dur >= required_duration:
                break
            video_files = video.get('video_files', [])
            hd_file = next((f for f in video_files if f['quality'] == 'hd'), video_files[0])
            link = hd_file['link']
            
            temp_name = f"temp_pexels_{i}.mp4"
            urllib.request.urlretrieve(link, temp_name)
            
            clip = VideoFileClip(temp_name)
            current_dur += clip.duration
            clip.close()
            downloaded_files.append(temp_name)
            
        return downloaded_files
    except Exception as e:
        print(f"Pexels素材获取失败：{e}")
        return []