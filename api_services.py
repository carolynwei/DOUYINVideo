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

def generate_script_by_style(topic, style, api_key, auto_image_prompt=True):
    """
    【🎯 智能路由器】根据风格动态构建 System Prompt + 强制自检
    支持5种爆款风格，共享通用爆款法则 + 风格化差异
    """
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1".strip())
    
    # 1️⃣ 风格定义库（动态插件）- 升级版：添加影像美学插件
    STYLE_CONFIGS = {
        "🗡️ 认知刺客流（冲击力+优越感）": {
            "tone": "冲击、扎心、人间清醒。目标：摧毁旧认知，建立高阶真相。语言：短句、倒装、高频反问。",
            "hook": "前3秒必须是反常识金句，直接否定普遍认知（“你以为…其实…”逻辑）",
            "visual_base": "Sam Kolder 风格，高对比度，冷色调，极简主体，锐利线条",
            "visual_rules": "视觉：高冷电影感。镜头：多用中远景切换特写，稳定器运镜。色调：深邃冷色调，强调光影明暗对比。参考：Sean Tucker 街头人文感 + Blade Runner 2049 视觉风格。",
            "shot_keywords": "Cinematic, Deep shadows, Chiaroscuro lighting, Cold color grading, Minimalist composition, Sharp lines, Medium shot to extreme close-up transition",
            "bgm_style": "深沉鼓点，低频Bass，紧迫感氛围音乐（参考：Hans Zimmer 风格）"
        },
        "👍 听勝/养成系（互动率04+评论爆炸）": {
            "tone": "真诚、低姿态、蜕变感。目标：激发好为人师欲。语言：口语化、求助式、带评论区互动点。",
            "hook": "以“求助”或“反差展示”开场（“上次你们说我XX，我改了…”）",
            "visual_base": "生活化场景，手机第一人称拍摄，生动表情，真实感强",
            "visual_rules": "视觉：生活化、Vlog感。镜头：手持摇晃，画面粗糙但真实，适当焦外。色调：自然光，略带杂乱的生活背景。参考：Brandon Li 纪实风格 + Casey Neistat Vlog 美学。",
            "shot_keywords": "Handheld camera, Vlog aesthetic, Natural lighting, Shallow depth of field, Casual background, Authentic expressions, Slightly shaky footage",
            "bgm_style": "温暖原声吉他，轻快钢琴，治愈系背景Lofi（参考：Indie Folk 风格）"
        },
        "🎬 POV沉浸流（第一人称+代入感）": {
            "tone": "压迫感、代入感、共情。目标：打破屏幕隔阙。语言：大量使用‘你’，强调感官细节。",
            "hook": "用“如果你是…”或“想象一下你正在…”直接把观众拉入场景",
            "visual_base": "Brandon Li 风格，第一人称视角，近距离特写，焦虑感或压迫感氛围",
            "visual_rules": "视觉：第一人称视角。镜头：超广角，模拟人眼，画面边缘有轻微畸变和动态模糊。参考：POV 极限运动运镜 + FPS 游戏视角。",
            "shot_keywords": "First-person POV, Ultra-wide angle, Motion blur, Edge distortion, Immersive perspective, Claustrophobic framing, Dynamic movement",
            "bgm_style": "紧张悬疑音效，心跳声，呼吸声，环境音增强沉浸感（参考：Horror Game OST）"
        },
        "🔥 情绪宣泄流（极致反转+发疯文学）": {
            "tone": "极端、爽感、发疯文学。目标：提供情绪出口。语言：情绪波动剧烈，使用夸张动词。",
            "hook": "用极端情绪词开场（“我真的忠了！”“给我笑死了！”），不讲道理只讲情",
            "visual_base": "Daniel Schiffer 风格，夹杂快闪切换，夏张表情，高饱和度色彩",
            "visual_rules": "视觉：极具张力和压迫感。镜头：极近特写（眼睛/嘴巴），快速推拉镜头，摇晃镜头增强混乱感。色调：高饱和度，红黑撞色。参考：电影级的特写剪辑 + Edgar Wright 快速剪辑风格。",
            "shot_keywords": "Extreme close-up, Shaky cam, Rapid zoom, High saturation, Red and black color palette, Intense facial expressions, Quick cuts",
            "bgm_style": "崩坏电子乐，混沌鼓点，尖叫声效，极具爆发力（参考：Trap/Dubstep 风格）"
        },
        "🐱 Meme抗象流（低成本+病毒传播）": {
            "tone": "幽默、病毒、解压。目标：极低门槛传播。语言：洗脑棗、配合简单视觉节奏。",
            "hook": "用网络棗或流行Emoji开场，降低接收门槛",
            "visual_base": "简单Meme图配文，猫狗表情包，低成本动画风，洗脑BGM",
            "visual_rules": "视觉：扁平化、高饱和。镜头：固定机位，主体居中，简单清晰。色调：明亮通透，多巴胺配色。参考：表情包美学 + TikTok 简易动画。",
            "shot_keywords": "Flat design, High saturation, Pop colors, Centered composition, Simple background, Meme template style, Clean and bright",
            "bgm_style": "洗脑神曲，魔性循环，高频电音，搭配特效音（参考：Vine/TikTok Viral Sounds）"
        }
    }
    
    # 获取当前风格配置
    style_config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["🗡️ 认知刺客流（冲击力+优越感）"])
    
    # 2️⃣ 构建万能主控提示词（融合方案一：自检环节）
    master_system_prompt = f"""你是一位顶尖视频制片人，现在正在执行【{style}】风格的任务。

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

【通用爆款法则】：
1. 黄金前3秒：直接切入冲突，禁止铺垫
2. 动词为王：用血肉感、动作感替换空洞的形容词
3. 钩子加密：每15秒必有一个新转折或视觉提示
4. 真实性红线：不编造数据，逻辑必须自洽

【🔍 强制自检环节】：
在输出JSON前，你必须进行内部审计，如有违反立刻重写：
1. **搜寻并删除**：查找是否存在“其实、那么、总之、让我们、大家好”等AI废话，一律删掉
2. **锐化动词**：检查前3秒是否有“很、非常、比较”等虚词，必须替换为具体动作
3. **逻辑对齐**：检查结尾是否在讲大道理，如果是，强制改为反问句或悬念钩子
4. **真实感检查**：确保语气像个活人，带点方言感或江湖气，不要像AI给人科普
5. **视觉检查**：确认每个 image_prompt 是否包含了镜头角度、光影和视觉参考，必须符合【视觉约束】

【输出要求】：
必须严格输出JSON数组，包含4-6个分镜。格式：
[{{"narration": "口播文案（经过自检的刺客文案）", "image_prompt": "English prompt with {style_config['shot_keywords']}, cinematic lighting, detailed scene"}}]

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
        scenes = json.loads(clean_content)
        
        # 解析返回的JSON结构
        if isinstance(scenes, dict):
            for v in scenes.values():
                if isinstance(v, list):
                    st.success(f"✅ {style} 剧本已通过自检审计！")
                    return v
        
        st.success(f"✅ {style} 剧本已通过自检审计！")
        return scenes
        
    except Exception as e:
        st.error(f"{style} 剧本生成失败: {e}")
        return []

def generate_images_zhipu(scenes_data, api_key):
    """调用智谱 CogView-3-Plus"""
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations".strip()  # 🔑 核心修复：清理URL
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    image_paths = []
    
    for i, scene in enumerate(scenes_data):
        # 🔍 检查 image_prompt 是否为空
        if not scene.get('image_prompt') or scene['image_prompt'].strip() == "":
            st.warning(f"⚠️ 分镜 {i+1} 的 image_prompt 为空，跳过图片生成")
            image_paths.append(None)
            continue
            
        payload = {"model": "cogview-3-plus", "prompt": scene['image_prompt'], "size": "1024x1920"}
        st.toast(f"🎨 正在绘制分镜 {i+1}/{len(scenes_data)} ...")
        
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
        print(f"Pexels素材获取失败：{e}")
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
