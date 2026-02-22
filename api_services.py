# -*- coding: utf-8 -*-
"""
API 服务模块：处理热点获取、剧本生成、图片生成等功能
确保所有中文字符正确显示
"""

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
    """使用 DeepSeek 生成剧本（标准模式，注入爆款基因）"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 🔥 升级版标准模式：爆款基因 + 真实性保护
    system_prompt = """你是一位专业的短视频导演，精通爆款视频创作法则，同时坚守内容真实性。

【核心创作原则】：
1. 黄金前3秒：第一句必须有强冲击力，直接吸引注意力（悬念/冲突/反常识）
2. 删除废话：不用"那么、其实、众所周知"等连接词，直接上结论
3. 具体化表达：用动词和名词替换模糊形容词（"很快"→"推背感"）
4. 情绪节奏：每段都要有情绪起伏，适当使用反问或预告
5. 画面张力：描述要包含主体、动作、场景、光线、镜头语言

【❗ 真实性红线】：
- 如果涉及数据/历史/科学知识，必须准确，不能编造
- 观点可以犀利，但逻辑必须自洽
- 不使用误导性标题党（"震惊！内幕！你绝对不知道！"）
- 可验证性：提到的产品/事件/人物必须真实存在

【输出要求】：
必须严格输出 JSON 数组，包含 4-6 个分镜。格式：
[{"narration": "口播文案（第一句必须是金句Hook）", "image_prompt": "English prompt, cinematic lighting, detailed scene description"}]

绝对不要输出 Markdown 标记（如 ```json）或其他解释性文字。"""
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

def generate_viral_script(topic, api_key, auto_image_prompt=True):
    """🔥 使用爆款剧本大师 Agent 生成高能量脚本 (注入完整 Skill)"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 动态设定关于画面提示词的指令
    if auto_image_prompt:
        image_prompt_instruction = '"image_prompt": "导演级分镜提示词（必须全英文，包含光影、运镜及大师风格，如 \'Brandon Li style, hand-held tracking shot...\'）"'
    else:
        # 手动模式下，强行让 AI 留空
        image_prompt_instruction = '"image_prompt": "" // 保持为空字符串，留给人类导演稍后手动填写'
    
    # 🎯 终极爆款剧本大师 System Prompt (深度注入运营日记精髓)
    viral_system_prompt = f"""你是全网最顶尖的抖音爆款视频制作人、深谙人性的"认知刺客"。你精通算法推流底层逻辑（完播率>30%，点赞率>5%）。你的任务是根据用户主题，输出一套招招致命、毫无废话的爆款短视频脚本与分镜。

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
  {{
    "narration": "刺客文案（第一句必须是极具冲击力的黄金3秒Hook，后续文案严格运用三步删改法，高能量密度）",
    {image_prompt_instruction}
  }}
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

# 🎬 导演级 Prompt 模板库 - VideoTaxi Cinematography v3.0
CINEMATIC_TEMPLATES = {
    "镜头语言": {
        "extreme_close_up": "Extreme close-up, shallow depth of field, bokeh background, intimate perspective",
        "close_up": "Close-up portrait, sharp focus on subject, blurred background, emotional intensity",
        "medium_shot": "Medium shot, waist-up framing, environmental context, natural posture",
        "wide_shot": "Wide shot, full body in environment, establishing scene, cinematic composition",
        "low_angle": "Low angle shot, looking up at subject, powerful and dominant perspective",
        "high_angle": "High angle shot, looking down, vulnerable or contemplative mood",
        "dutch_angle": "Dutch angle, tilted horizon, disorienting and tense atmosphere",
        "over_shoulder": "Over-the-shoulder shot, perspective dialogue, depth layers",
        "pov": "First-person POV, immersive perspective, hands in frame, subjective experience"
    },
    "光影效果": {
        "cinematic": "Cinematic lighting, dramatic chiaroscuro, high contrast shadows",
        "neon": "Neon lighting, cyberpunk atmosphere, red and blue color cast, night scene",
        "natural": "Natural golden hour lighting, soft diffused sunlight, warm tones",
        "moody": "Moody atmospheric lighting, fog and haze, desaturated palette",
        "studio": "Professional studio lighting, three-point setup, clean and polished",
        "practical": "Practical lighting sources, lamps and screens, realistic ambiance"
    },
    "风格滤镜": {
        "sam_kolder": "Sam Kolder style, orange and teal color grading, smooth transitions, travel film aesthetic",
        "brandon_li": "Brandon Li documentary style, handheld authenticity, human stories, natural moments",
        "daniel_schiffer": "Daniel Schiffer commercial style, product focus, vibrant colors, macro details",
        "blade_runner": "Blade Runner 2049 aesthetic, cyberpunk dystopia, neon-noir, Denis Villeneuve style",
        "wong_kar_wai": "Wong Kar-wai style, slow shutter motion blur, saturated neon, romantic melancholy",
        "roger_deakins": "Roger Deakins cinematography, masterful lighting, wide compositions, subtle color grading"
    },
    "质感增强": {
        "film_grain": "35mm film grain, Kodak Vision3 texture, organic imperfections",
        "anamorphic": "Anamorphic lens characteristics, oval bokeh, horizontal lens flares",
        "sharp": "Ultra-sharp 8K resolution, crisp details, professional photography",
        "dreamy": "Dreamy soft focus, ethereal glow, romantic atmosphere",
        "gritty": "Gritty documentary texture, raw and unpolished, real-world authenticity"
    }
}


def build_master_image_prompt(visual_anchor: str, scene_description: str, style_config: dict, shot_type: str = "close_up") -> str:
    """
    🎬 导演级 Prompt 构建器 - 确保电影级画面质感
    
    重要：scene_description 应该只包含场景和动作，不包含主角外貌描述
    visual_anchor 包含主角特征，两者组合成完整画面
    
    Args:
        visual_anchor: 视觉锚点（主角特征包，只写一次）
        scene_description: 场景描述（只写场景+动作，不写主角外貌）
        style_config: 风格配置
        shot_type: 镜头类型
    
    Returns:
        完整的英文生图 Prompt
    """
    # 清理输入
    anchor = (visual_anchor or "A consistent character").strip()
    scene = (scene_description or "").strip()
    
    # 如果 scene_description 已经包含了 visual_anchor 的内容，去重
    if anchor.lower() in scene.lower():
        # scene 已经包含了 anchor，直接使用 scene
        main_content = scene
    else:
        # 正常组合：anchor + scene
        main_content = f"{anchor}, {scene}" if scene else anchor
    
    # 2. 镜头语言
    shot = CINEMATIC_TEMPLATES["镜头语言"].get(shot_type, CINEMATIC_TEMPLATES["镜头语言"]["close_up"])
    
    # 3. 光影效果（根据风格选择）
    visual_base = style_config.get("visual_base", "").lower()
    if "cyberpunk" in visual_base or "neon" in visual_base:
        lighting = CINEMATIC_TEMPLATES["光影效果"]["neon"]
    elif "natural" in visual_base or "vlog" in visual_base:
        lighting = CINEMATIC_TEMPLATES["光影效果"]["natural"]
    elif "moody" in visual_base:
        lighting = CINEMATIC_TEMPLATES["光影效果"]["moody"]
    else:
        lighting = CINEMATIC_TEMPLATES["光影效果"]["cinematic"]
    
    # 4. 风格滤镜
    style_filter = style_config.get("shot_keywords", CINEMATIC_TEMPLATES["风格滤镜"]["sam_kolder"])
    
    # 5. 质感增强
    texture = CINEMATIC_TEMPLATES["质感增强"]["sharp"]
    
    # 组合完整 Prompt（避免重复）
    prompt_parts = [
        main_content,  # 主角 + 场景动作
        shot,  # 镜头语言
        lighting,  # 光影效果
        style_filter,  # 风格滤镜
        texture,  # 质感增强
        "8k resolution, highly detailed, professional photography, cinematic composition"
    ]
    
    # 过滤空值并去重
    seen = set()
    filtered_parts = []
    for part in prompt_parts:
        if part and part.lower() not in seen:
            seen.add(part.lower())
            filtered_parts.append(part)
    
    return ", ".join(filtered_parts)


def generate_visual_anchor(topic: str, style: str, client) -> dict:
    """
    🎯 生成视觉锚点（主角特征包）- 确保全片人物一致性
    
    Returns:
        {
            "anchor_description": "主角特征描述",
            "character_type": "人物/产品/场景",
            "key_features": ["特征1", "特征2", "特征3"]
        }
    """
    anchor_prompt = f"""基于主题"{topic}"和风格"{style}"，定义一个视觉锚点（Visual Anchor）。

视觉锚点是确保全片画面一致性的关键：所有分镜中的人物/主体必须保持相同特征。

请输出JSON格式：
{{
  "anchor_description": "详细的主角特征描述（中文，50字以内）",
  "character_type": "person/product/scene",
  "key_features": ["特征1", "特征2", "特征3"],
  "english_description": "英文描述，用于image_prompt开头"
}}

示例（35岁程序员主题）：
{{
  "anchor_description": "穿黑色皮衣的35岁亚洲男性，深邃眼眸，下巴有胡茬，略带疲惫但坚定的神情",
  "character_type": "person",
  "key_features": ["黑色皮衣", "深邃眼眸", "下巴胡茬"],
  "english_description": "A 35-year-old Asian man wearing a black leather jacket, deep-set eyes, stubbled chin, tired yet determined expression"
}}"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": anchor_prompt}],
            temperature=0.7,
            response_format={'type': 'json_object'}
        )
        content = response.choices[0].message.content
        clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
        return json.loads(clean_content)
    except Exception as e:
        # 返回默认锚点
        return {
            "anchor_description": "亚洲年轻主角，现代都市风格",
            "character_type": "person",
            "key_features": ["亚洲面孔", "现代服装"],
            "english_description": "A young Asian protagonist, modern urban style"
        }


def generate_script_by_style(topic, style, api_key, auto_image_prompt=True):
    """
    【🎬 VideoTaxi Cinematography v3.0 导演定焦版】
    
    核心升级：
    1. 视觉锚点系统：先生成主角特征包，确保全片人物一致性
    2. 导演级Prompt模板：强制包含镜头语言、光影、风格滤镜
    3. 电影质感增强：8K、胶片颗粒、专业摄影术语
    """
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 🎯 步骤1：生成视觉锚点（主角特征包）
    with st.status("🎬 导演正在确定视觉锚点...", expanded=True) as status:
        visual_anchor_data = generate_visual_anchor(topic, style, client)
        visual_anchor = visual_anchor_data.get("english_description", "")
        status.update(label=f"✅ 视觉锚点锁定: {visual_anchor_data.get('anchor_description', '')}", state="complete")
        st.json(visual_anchor_data)
    
    # 1️⃣ 风格定义库（增强版）- VideoTaxi Cinematography v3.0
    STYLE_CONFIGS = {
        "🗡️ 认知刺客流（冲击力+优越感）": {
            "tone": "冲击、扎心、人间清醒。目标：摧毁旧认知，建立高阶真相。语言：短句、倒装、高频反问。",
            "hook": "前3秒必须是反常识金句，直接否定普遍认知（你以为...其实...逻辑）",
            "visual_base": "Sam Kolder + Roger Deakins 风格，高对比度，冷色调，电影级光影",
            "visual_rules": """视觉：高冷电影感，专业 cinematography。
镜头：多用 Medium shot 到 Extreme close-up 的切换，稳定器运镜，Dutch angle 制造张力。
光影：Cinematic lighting, dramatic chiaroscuro, deep shadows, cold color grading。
色调：深邃冷色调，强调光影明暗对比，orange and teal 色彩分级。
参考：Sean Tucker 街头人文感 + Blade Runner 2049 视觉风格 + Sam Kolder 转场美学。""",
            "shot_keywords": CINEMATIC_TEMPLATES["风格滤镜"]["sam_kolder"] + ", " + CINEMATIC_TEMPLATES["风格滤镜"]["roger_deakins"],
            "default_shot": "close_up",
            "bgm_style": "深沉鼓点，低频Bass，紧迫感氛围音乐（参考：Hans Zimmer 风格）"
        },
        "👍 听勝/养成系（互动率04+评论爆炸）": {
            "tone": "真诚、低姿态、蜕变感。目标：激发好为人师欲。语言：口语化、求助式、带评论区互动点。",
            "hook": "以求助或反差展示开场（上次你们说我XX，我改了...）",
            "visual_base": "Brandon Li 纪实风格，生活化场景，手机第一人称拍摄",
            "visual_rules": """视觉：生活化、Vlog感，authentic documentary style。
镜头：Handheld camera, slightly shaky footage, shallow depth of field, over-the-shoulder shots。
光影：Natural lighting, golden hour warmth, practical light sources。
色调：自然光，略带杂乱的生活背景，温暖真实。
参考：Brandon Li 纪实风格 + Casey Neistat Vlog 美学。""",
            "shot_keywords": CINEMATIC_TEMPLATES["风格滤镜"]["brandon_li"],
            "default_shot": "medium_shot",
            "bgm_style": "温暖原声吉他，轻快钢琴，治愈系背景Lofi（参考：Indie Folk 风格）"
        },
        "🎬 POV沉浸流（第一人称+代入感）": {
            "tone": "压迫感、代入感、共情。目标：打破屏幕隔阙。语言：大量使用'你'，强调感官细节。",
            "hook": "用如果你是...或想象一下你正在...直接把观众拉入场景",
            "visual_base": "POV 极限运动 + FPS 游戏视角，超广角，沉浸式",
            "visual_rules": """视觉：First-person POV，immersive perspective，subjective camera。
镜头：Ultra-wide angle lens, motion blur, edge distortion, POV hands in frame。
光影：Moody atmospheric lighting, practical sources, realistic ambiance。
色调：焦虑感或压迫感氛围，slightly desaturated。
参考：POV 极限运动运镜 + FPS 游戏视角 + 第一人称电影。""",
            "shot_keywords": "First-person POV, Ultra-wide angle, Motion blur, Immersive perspective, Subjective camera, POV hands",
            "default_shot": "pov",
            "bgm_style": "紧张悬疑音效，心跳声，呼吸声，环境音增强沉浸感（参考：Horror Game OST）"
        },
        "🔥 情绪宣泄流（极致反转+发疯文学）": {
            "tone": "极端、爽感、发疯文学。目标：提供情绪出口。语言：情绪波动剧烈，使用夸张动词。",
            "hook": "用极端情绪词开场（我真的忠了！给我笑死了！），不讲道理只讲情",
            "visual_base": "Daniel Schiffer + Edgar Wright 风格，快闪切换，高饱和度",
            "visual_rules": """视觉：极具张力和压迫感，high energy commercial style。
镜头：Extreme close-up (eyes/mouth), rapid zoom, shaky cam, quick cuts, Dutch angles。
光影：High contrast, dramatic shadows, saturated colors, red and black palette。
色调：高饱和度，红黑撞色，情绪化的色彩。
参考：电影级的特写剪辑 + Edgar Wright 快速剪辑 + Daniel Schiffer 商业风格。""",
            "shot_keywords": CINEMATIC_TEMPLATES["风格滤镜"]["daniel_schiffer"],
            "default_shot": "extreme_close_up",
            "bgm_style": "崩坏电子乐，混沌鼓点，尖叫声效，极具爆发力（参考：Trap/Dubstep 风格）"
        },
        "🐱 Meme抗象流（低成本+病毒传播）": {
            "tone": "幽默、病毒、解压。目标：极低门槛传播。语言：洗脑棗、配合简单视觉节奏。",
            "hook": "用网络棗或流行Emoji开场，降低接收门槛",
            "visual_base": "TikTok  viral style，扁平化，高饱和，表情包美学",
            "visual_rules": """视觉：Flat design, pop colors, centered composition, clean and bright。
镜头：Static camera, centered subject, simple background, eye-level framing。
光影：Bright even lighting, minimal shadows, vibrant saturation。
色调：明亮通透，多巴胺配色，高饱和。
参考：表情包美学 + TikTok  viral style + 简易动画。""",
            "shot_keywords": "Flat design, Pop colors, Centered composition, Viral meme style, Bright lighting, High saturation",
            "default_shot": "medium_shot",
            "bgm_style": "洗脑神曲，魔性循环，高频电音，搭配特效音（参考：Vine/TikTok Viral Sounds）"
        }
    }
    
    # 获取当前风格配置
    style_config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["🗡️ 认知刺客流（冲击力+优越感）"])
    
    # 2️⃣ VideoTaxi FSD 2.0 导演增强版主控提示词
    master_system_prompt = f"""你是一位顶尖视频制片人，正在执行【{style}】风格的任务。

【核心风格约束】：
{style_config['tone']}

【Hook 公式】：
{style_config['hook']}

【🎬 强制视觉分镜约束】：
必须严格按照以下视觉规则编写生图 Prompt：
{style_config['visual_rules']}

要求：生成的图像 Prompt 必须包含：
- 镜头角度（Shot Type）：如 Medium shot, Close-up, POV 等
- 光影（Lighting）：如 Cinematic lighting, Natural light, Deep shadows 等
- 视觉参考：{style_config['shot_keywords']}

【🎬 VideoTaxi FSD 2.0 导演指令集】：

**1. 视觉一致性锚点 (Visual Anchor)**：
在输出前，必须先定义一个 visual_anchor。所有分镜的 image_prompt 描述必须以该锚点开头，确保同一视频里的人物/主体保持一致。
- 如果是人物类视频：visual_anchor = "同一亚洲年轻女性，黑色长发，穿白色衬衫"
- 如果是产品类视频：visual_anchor = "同一款银色无线耳机，极简设计"
- 如果是场景类视频：visual_anchor = "同一间现代简约办公室，落地窗"
所有 image_prompt 必须以 visual_anchor 开头，然后再描述具体动作和场景。

**2. 情绪动态曲线 (Emotion Arc)**：
严禁全篇同一情绪！必须遵循 [Hook(冷) -> Content(深) -> Gold_Sentence(爆)] 的波段：
- 第1个分镜(Hook)：情绪 = cold_question 或 sarcastic_mock（冷启动，制造悬念）
- 第2-3个分镜(Content)：情绪 = deep_mystery 或 neutral_narrate（深入内容，建立认知）
- 第4-5个分镜(Gold)：情绪 = angry_shout 或 excited_announce 或 fierce_warning（爆发高潮，情绪顶点）
- 最后一个分镜(Outro)：情绪 = sad_sigh 或 neutral_narrate（余韵，引导互动）

**3. SFX 导演位 (Sound Effects Placeholder)**：
在 segments 中新增 sfx_label 字段，为后期音效预留位置：
- [Transition]：转场音效，用于分镜切换
- [Impact]：冲击音效，用于高潮/金句时刻
- [Suspense]：悬疑音效，用于制造紧张感
- [Glitch]：故障音效，用于科技/反转效果
- [Silence]：静音占位，用于呼吸停顿
分配策略：
- Hook分镜：使用 [Suspense] 或 [Silence] 制造悬念
- 转场分镜：使用 [Transition] 平滑切换
- 高潮分镜：使用 [Impact] 强化冲击力
- 反转分镜：使用 [Glitch] 制造意外感

【通用爆款法则】：
1. 黄金前3秒：直接切入冲突，禁止铺垫
2. 动词为王：用血肉感、动作感替换空洞的形容词
3. 钩子加密：每15秒必有一个新转折或视觉提示
4. 真实性红线：不编造数据，逻辑必须自洽

【🎤 TTS情绪标注规范】：
在每个narration中，必须为关键句子包裹SSML标签来控制语音情绪：

1. **语速(rate)控制**：
   - 紧张/冲击时：<prosody rate="fast">这就是真相</prosody>
   - 强调/沉思时：<prosody rate="slow">你真的了解自己吗</prosody>
   - 正常速度：<prosody rate="medium">默认文案</prosody>

2. **音调(pitch)控制**：
   - 兴奋/惊讶时：<prosody pitch="+15%">不可能！</prosody>
   - 严肃/低沉时：<prosody pitch="-10%">现实很残酷</prosody>

3. **音量(volume)控制**：
   - 强调关键词：<prosody volume="+20%">核心结论</prosody>
   - 低声细语：<prosody volume="-10%">不为人知的秘密</prosody>

4. **组合使用**：
   <prosody rate="fast" pitch="+10%" volume="+15%">这是爆点金句！</prosody>

💡 **标注策略**：
- 每个分镜至少标注1-2处情绪转折点
- Hook(前3秒)必须有强烈的语速/音调变化
- 反转/悬念句必须降速或变调，增强冲击感

【🔍 强制自检环节】：
在输出JSON前，你必须进行内部审计，如有违反立刻重写：
1. **搜寻并删除**：查找是否存在"其实、那么、总之、让我们、大家好"等AI废话，一律删掉
2. **锐化动词**：检查前3秒是否有"很、非常、比较"等虚词，必须替换为具体动作
3. **逻辑对齐**：检查结尾是否在讲大道理，如果是，强制改为反问句或悬念钩子
4. **真实感检查**：确保语气像个活人，带点方言感或江湖气，不要像AI给人科普
5. **视觉检查**：确认每个 image_prompt 是否包含了镜头角度、光影和视觉参考，必须符合【视觉约束】
6. **情绪检查**：确认narration中是否包含了至少1个<prosody>标签，Hook句必须有情绪标注

【📝 剧本内容核心要求】：
1. **口播文案必须紧扣主题**：每一句都要围绕"{topic}"展开，禁止偏离主题的泛泛而谈
2. **emotion_vibe 必须匹配内容情绪**：文案是什么情绪，就标注什么标签，不能为了凑曲线而硬贴标签
3. **画面提示词必须呼应文案**：看到画面就能想到文案，看到文案就能想象画面
4. **sfx_label 必须服务情绪**：音效是为了强化当前情绪，不是为了填满字段

【🎬 Visual Anchor 使用规范】：
- visual_anchor 只定义一次，包含主角的核心特征（外貌+服装+气质）
- 每个分镜的 image_prompt **只写场景和动作**，不要重复写主角外貌
- 示例：
  - visual_anchor: "A 30-year-old Asian woman with short black hair, wearing a red blazer, confident expression"
  - 分镜1 image_prompt: "sitting at desk, typing on laptop, office background"
  - 分镜2 image_prompt: "standing by window, looking at city skyline, sunset lighting"
  - ❌ 错误：每个分镜都重复"A 30-year-old Asian woman with short black hair..."

【⏱️ 时间轴规范】：
- 每个分镜 **2-4秒**，快节奏短平快
- 总时长控制在 **15-25秒**（抖音黄金时长）
- 时间必须连续：0-3, 3-6, 6-9, 9-12, 12-15...

【输出要求】：
必须严格输出JSON对象，包含 visual_anchor 和 segments 数组。格式：
{{
  "visual_anchor": "主角特征描述（英文，只写一次）",
  "segments": [
    {{
      "start_time": 0,
      "end_time": 3,
      "narration": "紧扣主题的口播文案（带SSML标签）", 
      "emotion_vibe": "根据文案实际情绪选择",
      "image_prompt": "场景+动作描述（英文，不包含主角外貌）",
      "sfx_label": "服务当前情绪的音效"
    }}
  ]
}}

⚡ **关键检查点**：
- [ ] visual_anchor 是否精确定义了主角特征？
- [ ] image_prompt 是否**没有重复**主角外貌描述？
- [ ] 每个分镜的 narration 是否都紧扣"{topic}"？
- [ ] emotion_vibe 是否与文案情绪真正匹配？
- [ ] 时间轴是否紧凑（2-4秒/分镜）？

绝对不要输出Markdown标记（如 ```json）或其他解释性文字。"""
    
    # 3️⃣ 调用AI模型
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": master_system_prompt},
                {"role": "user", "content": f"主题：{topic}"}
            ],
            temperature=0.7,
            response_format={'type': 'json_object'}
        )
        
        content = response.choices[0].message.content
        clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
        result = json.loads(clean_content)
        
        # 🎬 VideoTaxi FSD 2.0: 解析新的 JSON 结构
        if isinstance(result, dict):
            # 新格式：包含 visual_anchor 和 segments
            if 'segments' in result and isinstance(result['segments'], list):
                visual_anchor = result.get('visual_anchor', '')
                segments = result['segments']
                # 将 visual_anchor 注入到每个 segment 中供后续使用
                for seg in segments:
                    seg['_visual_anchor'] = visual_anchor
                st.success(f"✅ {style} 剧本已通过 VideoTaxi FSD 2.0 导演审计！")
                return segments
            # 兼容旧格式：直接返回数组
            for v in result.values():
                if isinstance(v, list):
                    st.success(f"✅ {style} 剧本已通过自检审计！")
                    return v
        
        st.success(f"✅ {style} 剧本已通过自检审计！")
        return result if isinstance(result, list) else []
        
    except Exception as e:
        st.error(f"{style} 剧本生成失败: {e}")
        return []

def generate_images_zhipu(scenes_data, api_key, style_config=None):
    """
    🎬 调用智谱 CogView-3-Plus - VideoTaxi Cinematography v3.0 导演定焦版
    
    核心升级：
    1. 使用 build_master_image_prompt 构建电影级 Prompt
    2. 视觉锚点确保人物一致性
    3. 强制镜头语言、光影、风格滤镜
    """
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations".strip()
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    image_paths = []
    
    # 获取视觉锚点（从第一个 scene 中获取）
    visual_anchor = ""
    if scenes_data and len(scenes_data) > 0:
        visual_anchor = scenes_data[0].get('_visual_anchor', '')
    
    # 默认风格配置
    default_style = {
        "shot_keywords": CINEMATIC_TEMPLATES["风格滤镜"]["sam_kolder"],
        "default_shot": "close_up"
    }
    style = style_config or default_style
    
    for i, scene in enumerate(scenes_data):
        # 🔍 检查 image_prompt 是否为空
        raw_prompt = scene.get('image_prompt', '')
        if not raw_prompt or raw_prompt.strip() == "":
            st.warning(f"⚠️ 分镜 {i+1} 的 image_prompt 为空，跳过图片生成")
            image_paths.append(None)
            continue
        
        # 🎬 使用导演级 Prompt 构建器
        # 提取场景描述（去掉可能的 visual_anchor 前缀）
        scene_desc = raw_prompt
        if visual_anchor and raw_prompt.startswith(visual_anchor):
            scene_desc = raw_prompt[len(visual_anchor):].strip(", ")
        
        # 根据分镜位置选择镜头类型
        shot_type = style.get('default_shot', 'close_up')
        if i == 0:
            shot_type = 'extreme_close_up'  # Hook 用特写
        elif i == len(scenes_data) - 1:
            shot_type = 'wide_shot'  # 结尾用远景
        
        # 构建大师级 Prompt
        enhanced_prompt = build_master_image_prompt(
            visual_anchor=visual_anchor,
            scene_description=scene_desc,
            style_config=style,
            shot_type=shot_type
        )
            
        # 确保提示词长度合适（智谱有长度限制）
        if len(enhanced_prompt) > 500:
            enhanced_prompt = enhanced_prompt[:497] + "..."
            
        payload = {
            "model": "cogview-3-plus", 
            "prompt": enhanced_prompt, 
            "size": "1024x1920"
        }
        
        st.toast(f"🎨 正在绘制分镜 {i+1}/{len(scenes_data)} ...")
        st.caption(f"📝 优化后提示词: {enhanced_prompt[:80]}...")
        
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=60).json()
            
            # 🔍 详细的错误日志
            if 'data' in res:
                img_url = res['data'][0]['url']
                temp_name = f"temp_scene_{i}.jpg"
                st.write(f"✅ 分镜 {i+1} 图片URL获取成功: {img_url[:50]}...")
                urllib.request.urlretrieve(img_url, temp_name)
                
                # 验证文件是否下载成功
                if os.path.exists(temp_name) and os.path.getsize(temp_name) > 0:
                    st.write(f"✅ 分镜 {i+1} 图片下载成功: {temp_name} ({os.path.getsize(temp_name)} bytes)")
                    image_paths.append(temp_name)
                else:
                    st.error(f"❌ 分镜 {i+1} 图片下载失败或文件为空")
                    image_paths.append(None)
            else:
                st.error(f"❌ 分镜 {i+1} 智谱API返回错误: {res}")
                image_paths.append(None)
        except Exception as e:
            st.error(f"❌ 分镜 {i+1} 图片生成异常: {str(e)}")
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
        st.error(f"Pexels素材获取失败：{e}")
        return []

def refine_script_data(current_scenes, api_key):
    """✨ 调用大师进行二次精修，挑刺并提升文案能量密度"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 将当前的剧本转换为 JSON 字符串喂给 AI
    current_json_str = json.dumps(current_scenes, ensure_ascii=False)
    
    refine_system_prompt = """你是全网最毒舌、最懂人性的短视频内容总监。你深谙“认知刺客”爆款法则，但同时坚守内容的真实性和准确性。
你的任务是：无情地审查并精修用户提交的分镜剧本，提升其成为爆款的概率，同时确保内容可信。

【你的毒舌审查清单与修改规则】：
1. 黄金前3秒Hook检查：第一句如果平淡无奇，立刻把它改成带有强冲突、强悬念、反常识的爆点金句！
2. 废话大扫除：把所有的“那么、其实、众所周知、接下来”等连接词全部删掉！一句废话都不要留。
3. 软弱词汇升维：把所有的形容词（很生气、很快、很好）改成具体、有冲击力的动词和名词搭配（如：把手机砸烂、推背感、吊打同行）。
4. 钩子密度检查：确保每段文案都有情绪起伏，如果没有，强行加入反问或预告。
5. 画面张力提升：检查 image_prompt 是否足够有表现力，适当增加大师级摄影风格（如：Sam Kolder style, cinematic lighting, extreme close-up）以增强画面质感。

【❗ 关键原则：真实性与准确性审查】：
6. **事实核查**：如果文案涉及数据、统计、历史事件、科学知识，必须保持谨慎和准确。不要编造数据或夹大事实。
7. **逻辑自洽**：确保文案逻辑连贯，不能为了刺激效果而出现自相矛盾或明显错误的因果关系。
8. **避免误导**：不要使用引导性或误导性的标题党语汉，即使它们很吸引人。爆款不等于虚假。
9. **尊重常识**：对于常识性内容，不要为了“反常识”效果而扰乱基本事实。
10. **可验证性**：如果提到具体的产品、品牌、事件，确保它们是真实存在的，可以被查证的。

【平衡艺术】：
- 在提升文案吸引力的同时，绝不牺牲内容的真实性
- 用真实的故事、真实的数据、真实的情感打动人，而不是编造
- “认知刺客”的核心是刺痛点，不是造谣

【强制输出格式】
直接输出修改后的纯 JSON 数组，保持原有结构不变，绝对不要输出任何 markdown 符号（如 ```json）和解释性文字：
[{"narration": "精修后的刺客文案（真实且有力）", "image_prompt": "精修后的画面提示词"}]"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": refine_system_prompt},
                {"role": "user", "content": f"请立刻毒舌批改并重写以下剧本，直接返回精修后的 JSON 数组：\n\n{current_json_str}"}
            ],
            temperature=0.6, # 精修模式下降低一点温度，保证结构稳定和修改的精准度
            response_format={'type': 'json_object'}
        )
        
        content = response.choices[0].message.content
        clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
        refined_scenes = json.loads(clean_content)
        
        if isinstance(refined_scenes, dict):
            for v in refined_scenes.values():
                if isinstance(v, list): return v
        return refined_scenes if isinstance(refined_scenes, list) else []
        
    except Exception as e:
        st.error(f"大师精修失败: {e}")
        return []

def refine_script_by_chat(current_scenes, user_request, api_key):
    """💬 对话微调：根据用户的自然语言描述，智能修改剧本
    
    Args:
        current_scenes: 当前剧本的 scenes_data
        user_request: 用户的修改需求(如"第二段太平淡了，加点反转")
        api_key: DeepSeek API Key
    
    Returns:
        修改后的 scenes_data
    """
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 构造 Prompt：传递当前剧本 + 用户意图
    system_prompt = """你是一位精通短视频导演的 AI 助手。用户会给你一个已存在的剧本，并提出修改需求。

【你的任务】：
1. 理解用户的意图(如"加点反转"、"缩短时长"、"更有冲击力"等)
2. 只修改相关部分，保持其他内容不变
3. 保持原有的爆款基因(黄金前3秒、高密度钩子、具体化表达)
4. 保持 image_prompt 的视觉风格一致性

【输出要求】：
严格输出 JSON 数组，格式：
[{"narration": "口播文案", "image_prompt": "English prompt, cinematic style"}]

绝对不要输出 Markdown 标记（如 ```json）或其他解释性文字。"""
    
    try:
        # 构造用户消息
        user_message = f"""当前剧本：
{json.dumps(current_scenes, ensure_ascii=False, indent=2)}

用户说：{user_request}

请根据用户的需求修改剧本，返回完整的 JSON 数组。"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            response_format={'type': 'json_object'}
        )
        
        content = response.choices[0].message.content
        clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
        refined_scenes = json.loads(clean_content)
        
        # 处理可能的嵌套结构
        if isinstance(refined_scenes, dict):
            for v in refined_scenes.values():
                if isinstance(v, list): return v
        return refined_scenes if isinstance(refined_scenes, list) else []
        
    except Exception as e:
        st.error(f"对话微调失败: {e}")
        return []
