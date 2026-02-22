# -*- coding: utf-8 -*-
"""
VideoTaxi 导航员模块：对接天行数据抖音热点
作为 FSD 异步生产线的"全球导航系统"
"""

import requests
import random
from typing import List, Dict, Optional, Tuple
import streamlit as st


class TianapiNavigator:
    """
    VideoTaxi 导航员：对接天行数据抖音热点
    
    职责：
    1. 从天行 API 获取实时热点
    2. 根据热度值和关键词自动匹配 Vibe 风格
    3. 将原始 JSON 转化为导航任务清单
    4. 提供背景扩充，将短词扩展为丰满的创作素材
    """
    
    # 🎯 Vibe 风格路由表 - 关键词映射
    VIBE_ROUTING_TABLE = {
        "🗡️ 认知刺客流（冲击力+优越感）": {
            "keywords": ["真相", "现实", "背后", "内耗", "扎心", "揭秘", "本质", "底层", "认知", "思维", "人性", "社会", "职场", "焦虑", "压力", "困境", "真相", "套路", "潜规则"],
            "description": "适合揭露真相、打破认知、引发思考的话题",
            "priority": 1
        },
        "🔥 情绪宣泄流（极致反转+发疯文学）": {
            "keywords": ["崩溃", "破防", "发疯", "离谱", "无语", "愤怒", "爽文", "反转", "打脸", "解气", "暴躁", "炸裂", "狂飙", "暴怒", "忍不了"],
            "description": "适合极端情绪、爽感反转、情绪出口的话题",
            "priority": 2
        },
        "🐱 Meme抗象流（低成本+病毒传播）": {
            "keywords": ["挑战", "神曲", "梗", "模仿", "搞笑", "魔性", "洗脑", "沙雕", "鬼畜", "爆笑", "段子", "整活", "抽象"],
            "description": "适合病毒传播、幽默解压、低门槛参与的话题",
            "priority": 3
        },
        "🎬 POV沉浸流（第一人称+代入感）": {
            "keywords": ["体验", "感受", "经历", "故事", "如果", "假设", "代入", "沉浸", "第一视角", "身临其境", "你试过", "想象一下"],
            "description": "适合第一人称叙事、代入感强、共情共鸣的话题",
            "priority": 4
        },
        "👍 听勝/养成系（互动率04+评论爆炸）": {
            "keywords": ["求助", "建议", "改", "养成", "进步", "变化", "听劝", "改造", "成长", "学习", "练习", "打卡", "坚持"],
            "description": "适合养成系、求助互动、满足好为人师欲的话题",
            "priority": 5
        }
    }
    
    def __init__(self, api_key: str):
        """
        初始化导航员
        
        Args:
            api_key: 天行数据 API Key
        """
        self.api_key = api_key
        self.url = "https://apis.tianapi.com/douyinhot/index"
        self._cache = None  # 缓存热点数据
    
    def fetch_hot_topics(self, num: int = 10) -> List[Dict]:
        """
        从天行 API 获取抖音实时热搜
        
        Args:
            num: 获取前 N 条热点
            
        Returns:
            原始热点数据列表
        """
        try:
            response = requests.post(
                self.url,
                data={"key": self.api_key},
                headers={"Content-type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            res_json = response.json()
            
            if res_json.get("code") == 200:
                raw_list = res_json.get("result", {}).get("list", [])
                # 只取前 num 条
                return raw_list[:num]
            else:
                st.error(f"❌ 天行 API 报错: {res_json.get('msg')}")
                return []
                
        except requests.Timeout:
            st.error("❌ 天行 API 请求超时")
            return []
        except Exception as e:
            st.error(f"❌ 网络请求异常: {e}")
            return []
    
    def _auto_route_style(self, topic: str) -> str:
        """
        智能风格路由算法：根据主题关键词自动匹配 Vibe 风格
        
        Args:
            topic: 热点主题词
            
        Returns:
            匹配的风格名称
        """
        topic_lower = topic.lower()
        
        # 计算每个风格的匹配得分
        scores = {}
        for style, config in self.VIBE_ROUTING_TABLE.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in topic_lower:
                    score += 1
            # 加入优先级权重（优先级高的略微加分）
            score += (6 - config["priority"]) * 0.1
            scores[style] = score
        
        # 返回得分最高的风格
        if scores:
            best_style = max(scores, key=scores.get)
            # 如果最高分为0，返回默认风格
            if scores[best_style] == 0:
                return "🗡️ 认知刺客流（冲击力+优越感）"
            return best_style
        
        return "🗡️ 认知刺客流（冲击力+优越感）"
    
    def _calculate_heat_level(self, hot_value: int) -> Tuple[str, str]:
        """
        计算热度等级
        
        Args:
            hot_value: 热度值
            
        Returns:
            (热度等级, 热度图标)
        """
        if hot_value >= 10000000:
            return "🔥🔥🔥 爆款", "red"
        elif hot_value >= 1000000:
            return "🔥🔥 高热", "orange"
        elif hot_value >= 100000:
            return "🔥 热门", "yellow"
        else:
            return "📈 潜力", "green"
    
    def fetch_today_missions(self, num: int = 5) -> List[Dict]:
        """
        获取今日导航任务清单（核心接口）
        
        Args:
            num: 获取任务数量
            
        Returns:
            任务清单列表，每个任务包含：
            - topic: 主题词
            - hot_value: 热度值
            - heat_level: 热度等级
            - recommended_style: 推荐风格
            - description: 任务描述
            - raw_data: 原始数据
        """
        raw_topics = self.fetch_hot_topics(num)
        missions = []
        
        for item in raw_topics:
            topic = item.get('word', '')
            hot_value = item.get('hotnum', 0)  # 天行数据的热度字段
            
            # 自动匹配风格
            style = self._auto_route_style(topic)
            
            # 计算热度等级
            heat_level, heat_color = self._calculate_heat_level(hot_value)
            
            missions.append({
                "topic": topic,
                "hot_value": hot_value,
                "heat_level": heat_level,
                "heat_color": heat_color,
                "recommended_style": style,
                "description": f"当前抖音热度：{hot_value:,}",
                "raw_data": item
            })
        
        # 缓存结果
        self._cache = missions
        return missions
    
    def expand_topic_context(self, topic: str, api_key: str) -> Dict:
        """
        热点背景扩充器：将短词扩展为丰满的创作素材
        
        当接收到一个简单的热搜词时，让 AI 联想相关的社会痛点和情绪母体
        
        Args:
            topic: 热点主题词
            api_key: DeepSeek API Key
            
        Returns:
            扩充后的背景信息
        """
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        
        expansion_prompt = f"""你是一位资深的社会观察家和短视频内容策划。

任务：基于热点词「{topic}」进行深度背景扩充。

请输出以下分析（JSON格式）：
{{
  "emotion_mother": "这个词背后的核心情绪母体（焦虑/愤怒/好奇/恐惧/渴望等）",
  "pain_points": ["相关的3个社会痛点"],
  "target_audience": "最关注这个话题的人群画像",
  "content_angles": ["3个不同的内容切入角度"],
  "controversy_potential": "这个话题的争议潜力评分（1-10）及原因",
  "viral_elements": ["可能引爆传播的3个元素"]
}}

要求：
1. 分析要犀利、有洞察力，不要泛泛而谈
2. 痛点要具体、真实、能引发共鸣
3. 切入角度要有差异化，避免陈词滥调
4. 只输出JSON，不要其他解释"""

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位犀利的社会观察家，擅长挖掘热点背后的深层情绪。"},
                    {"role": "user", "content": expansion_prompt}
                ],
                temperature=0.7,
                response_format={'type': 'json_object'}
            )
            
            content = response.choices[0].message.content
            import json
            import re
            clean_content = re.sub(r'```json\n|\n```|```', '', content).strip()
            expansion = json.loads(clean_content)
            
            return {
                "success": True,
                "topic": topic,
                "expansion": expansion
            }
            
        except Exception as e:
            st.error(f"背景扩充失败: {e}")
            return {
                "success": False,
                "topic": topic,
                "expansion": None
            }
    
    def get_mission_by_topic(self, topic: str) -> Optional[Dict]:
        """
        根据主题词获取任务详情
        
        Args:
            topic: 主题词
            
        Returns:
            任务详情，未找到返回 None
        """
        if not self._cache:
            return None
        
        for mission in self._cache:
            if mission["topic"] == topic:
                return mission
        return None
    
    def refresh_cache(self):
        """清除缓存，强制重新获取"""
        self._cache = None


# 🚀 全自动发车函数
def auto_pilot_generate(
    navigator: TianapiNavigator,
    deepseek_key: str,
    zhipu_key: str,
    pexels_key: str,
    voice_id: str = "zh-CN-YunxiNeural",
    num_missions: int = 1
) -> List[Dict]:
    """
    🎬 全自动发车：从热点抓取到视频生成的完整流水线
    
    Args:
        navigator: 天行导航员实例
        deepseek_key: DeepSeek API Key
        zhipu_key: 智谱 API Key
        pexels_key: Pexels API Key
        voice_id: 配音音色ID
        num_missions: 要执行的任务数量
        
    Returns:
        生成结果列表
    """
    from api_services import generate_script_by_style
    from video_engine import render_ai_video_pipeline
    
    results = []
    
    # 1. 获取今日任务
    st.info("🛰️ 正在扫描全网热点...")
    missions = navigator.fetch_today_missions(num_missions)
    
    if not missions:
        st.error("❌ 未获取到热点数据")
        return results
    
    st.success(f"✅ 获取到 {len(missions)} 个热点任务")
    
    # 2. 逐个执行任务
    for i, mission in enumerate(missions[:num_missions]):
        st.markdown(f"---")
        st.subheader(f"🚗 任务 {i+1}/{num_missions}: {mission['topic']}")
        
        topic = mission["topic"]
        style = mission["recommended_style"]
        
        st.write(f"📊 热度: {mission['heat_level']}")
        st.write(f"🎭 风格: {style}")
        
        try:
            # 2.1 生成剧本
            st.write("🎬 正在生成剧本...")
            scenes_data = generate_script_by_style(
                topic=topic,
                style=style,
                api_key=deepseek_key,
                auto_image_prompt=True
            )
            
            if not scenes_data:
                st.error(f"❌ 任务 {i+1} 剧本生成失败")
                results.append({
                    "topic": topic,
                    "status": "failed",
                    "stage": "script_generation",
                    "error": "剧本生成失败"
                })
                continue
            
            st.success(f"✅ 剧本生成完成：{len(scenes_data)} 个分镜")
            
            # 2.2 渲染视频
            st.write("🎥 正在渲染视频...")
            output_file = f"auto_video_{i+1}_{topic[:10]}.mp4"
            
            success = render_ai_video_pipeline(
                scenes_data=scenes_data,
                zhipu_key=zhipu_key,
                output_path=output_file,
                pexels_key=pexels_key,
                voice_id=voice_id,
                style_name=style
            )
            
            if success:
                st.success(f"🎉 任务 {i+1} 完成！视频已保存: {output_file}")
                results.append({
                    "topic": topic,
                    "status": "success",
                    "video_file": output_file,
                    "style": style,
                    "scenes_count": len(scenes_data)
                })
            else:
                st.error(f"❌ 任务 {i+1} 视频渲染失败")
                results.append({
                    "topic": topic,
                    "status": "failed",
                    "stage": "video_rendering",
                    "error": "视频渲染失败"
                })
                
        except Exception as e:
            st.error(f"❌ 任务 {i+1} 异常: {e}")
            results.append({
                "topic": topic,
                "status": "failed",
                "stage": "unknown",
                "error": str(e)
            })
    
    # 3. 输出总结
    st.markdown(f"---")
    st.subheader("📊 全自动发车总结")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count
    
    col1, col2, col3 = st.columns(3)
    col1.metric("总任务", len(results))
    col2.metric("成功", success_count, delta=f"{success_count/len(results)*100:.0f}%")
    col3.metric("失败", failed_count)
    
    return results


# 🧪 测试代码
if __name__ == "__main__":
    # 测试导航员功能
    import os
    
    api_key = os.getenv("TIANAPI_KEY", "")
    if api_key:
        nav = TianapiNavigator(api_key)
        missions = nav.fetch_today_missions(5)
        
        print("=" * 50)
        print("🛰️ VideoTaxi 导航员测试")
        print("=" * 50)
        
        for m in missions:
            print(f"\n🔥 {m['topic']}")
            print(f"   热度: {m['heat_level']} ({m['hot_value']:,})")
            print(f"   风格: {m['recommended_style']}")
    else:
        print("⚠️ 请设置 TIANAPI_KEY 环境变量")