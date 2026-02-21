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