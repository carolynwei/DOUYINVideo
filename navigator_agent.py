# -*- coding: utf-8 -*-
"""
热点导航员 (Hotspot Navigator)
负责扫描全网热点，自动匹配VideoTaxi风格，下达跑单任务
确保所有中文字符正确显示
"""

import requests
import json
from datetime import datetime
import streamlit as st

class HotspotNavigator:
    """
    热点导航员：VideoTaxi的自动巡航系统
    扫描抖音/知乎/微博热榜，智能匹配风格并下达任务
    """
    
    # 🎯 风格路由规则
    STYLE_ROUTING = {
        "social": "🗡️ 认知刺客流（冲击力+优越感）",
        "economy": "🗡️ 认知刺客流（冲击力+优越感）",
        "psychology": "👍 听劝/养成系（互动率04+评论爆炸）",
        "lifestyle": "🎬 POV沉浸流（第一人称+代入感）",
        "entertainment": "🔥 情绪宣泄流（极致反转+发疯文学）",
        "meme": "🐱 Meme抗象流（低成本+病毒传播）",
    }
    
    # 📊 热度阈值配置
    HEAT_THRESHOLD = {
        "high": 8000,   # 高热度：立即出车
        "medium": 5000, # 中热度：观望
        "low": 2000     # 低热度：放弃
    }
    
    def __init__(self, douyin_api_key=None, zhihu_api_key=None):
        """
        Args:
            douyin_api_key: 抖音热搜API密钥
            zhihu_api_key: 知乎热榜API密钥
        """
        self.douyin_key = douyin_api_key
        self.zhihu_key = zhihu_api_key
        self.trending_pool = []
    
    def scan_douyin_trending(self):
        """
        扫描抖音热搜榜
        接入天行API或其他热搜接口
        """
        if not self.douyin_key:
            st.warning("⚠️ 未配置抖音热搜API，使用模拟数据")
            return self._mock_trending_data()
        
        try:
            url = 'https://apis.tianapi.com/douyinhot/index'
            response = requests.post(
                url, 
                data={'key': self.douyin_key}, 
                headers={'Content-type': 'application/x-www-form-urlencoded'}, 
                timeout=10
            )
            data = response.json()
            
            if data.get('code') == 200:
                trending = []
                for item in data['result']['list'][:15]:  # 前15条热搜
                    trending.append({
                        "topic": item['word'],
                        "heat": item.get('hot_value', 0),
                        "type": self._classify_topic(item['word']),
                        "source": "抖音"
                    })
                return trending
            else:
                st.error(f"❌ 抖音热搜API错误: {data.get('msg', '未知错误')}")
                return []
        except Exception as e:
            st.error(f"❌ 抖音热搜扫描失败: {e}")
            return []
    
    def scan_zhihu_trending(self):
        """
        扫描知乎热榜（示例接口）
        """
        # TODO: 接入知乎热榜API
        st.info("🚧 知乎热榜接口待接入")
        return []
    
    def _classify_topic(self, topic):
        """
        基于关键词分类话题类型
        """
        # 社会民生类关键词
        if any(kw in topic for kw in ["裁员", "35岁", "失业", "内卷", "打工人", "社会", "现象"]):
            return "social"
        
        # 经济财富类关键词
        if any(kw in topic for kw in ["赚钱", "理财", "投资", "房价", "经济", "消费", "存款"]):
            return "economy"
        
        # 心理情感类关键词
        if any(kw in topic for kw in ["焦虑", "抑郁", "心理", "情绪", "压力", "孤独", "爱情"]):
            return "psychology"
        
        # 生活方式类关键词
        if any(kw in topic for kw in ["健康", "养生", "健身", "减肥", "美食", "旅游", "穿搭"]):
            return "lifestyle"
        
        # Meme娱乐类关键词
        if any(kw in topic for kw in ["猫", "狗", "搞笑", "沙雕", "整活", "表情包", "梗"]):
            return "meme"
        
        # 默认归为社会类
        return "social"
    
    def _mock_trending_data(self):
        """
        模拟热搜数据（开发测试用）
        """
        return [
            {"topic": "35岁程序员裸辞开网约车", "heat": 9800, "type": "social", "source": "模拟"},
            {"topic": "为什么现在的年轻人不爱买房了", "heat": 9200, "type": "economy", "source": "模拟"},
            {"topic": "猫咪版'科目三'走红", "heat": 8500, "type": "meme", "source": "模拟"},
            {"topic": "如何摆脱职场焦虑症", "heat": 7800, "type": "psychology", "source": "模拟"},
            {"topic": "一天只吃一顿饭的危害", "heat": 6900, "type": "lifestyle", "source": "模拟"},
            {"topic": "别再被PUA了！老板的套路你要懂", "heat": 8200, "type": "social", "source": "模拟"},
            {"topic": "月薪5000如何实现被动收入", "heat": 7500, "type": "economy", "source": "模拟"},
        ]
    
    def evaluate_heat(self, heat_value):
        """
        评估热度等级
        Returns: 'high' | 'medium' | 'low'
        """
        if heat_value >= self.HEAT_THRESHOLD['high']:
            return 'high'
        elif heat_value >= self.HEAT_THRESHOLD['medium']:
            return 'medium'
        else:
            return 'low'
    
    def scan_all_platforms(self):
        """
        扫描所有平台热点并汇总
        """
        st.info("🔍 开始扫描全网热点...")
        
        # 扫描抖音
        douyin_trends = self.scan_douyin_trending()
        
        # 扫描知乎（待实现）
        # zhihu_trends = self.scan_zhihu_trending()
        
        # 汇总去重
        self.trending_pool = douyin_trends
        
        # 按热度排序
        self.trending_pool = sorted(
            self.trending_pool, 
            key=lambda x: x['heat'], 
            reverse=True
        )
        
        st.success(f"✅ 扫描完成，发现 {len(self.trending_pool)} 个热点话题")
        return self.trending_pool
    
    def select_mission(self, min_heat='medium'):
        """
        选择今日跑单任务
        
        Args:
            min_heat: 最低热度要求 ('high' | 'medium' | 'low')
        
        Returns:
            任务清单字典
        """
        if not self.trending_pool:
            self.scan_all_platforms()
        
        # 筛选符合热度要求的话题
        threshold = self.HEAT_THRESHOLD[min_heat]
        qualified = [t for t in self.trending_pool if t['heat'] >= threshold]
        
        if not qualified:
            st.warning(f"⚠️ 未找到热度 >= {threshold} 的话题，降低标准...")
            qualified = self.trending_pool[:3]  # 取前3个
        
        # 选择热度最高的话题
        top_trend = qualified[0]
        
        # 自动匹配风格
        topic_type = top_trend['type']
        style = self.STYLE_ROUTING.get(topic_type, "🗡️ 认知刺客流（冲击力+优越感）")
        
        # 生成任务ID
        mission_id = f"VTAXI-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # 构建任务清单
        mission = {
            "mission_id": mission_id,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "topic": top_trend['topic'],
            "heat": top_trend['heat'],
            "heat_level": self.evaluate_heat(top_trend['heat']),
            "style": style,
            "topic_type": topic_type,
            "source": top_trend['source'],
            "target_vibe": self._get_vibe_strategy(style),
            "estimated_views": self._estimate_views(top_trend['heat'])
        }
        
        return mission
    
    def _get_vibe_strategy(self, style):
        """
        根据风格返回创作策略
        """
        strategies = {
            "🗡️ 认知刺客流（冲击力+优越感）": "高能、反转、扎心、优越感",
            "👍 听劝/养成系（互动率04+评论爆炸）": "真诚、求助、蜕变、互动",
            "🎬 POV沉浸流（第一人称+代入感）": "代入、压迫、共情、沉浸",
            "🔥 情绪宣泄流（极致反转+发疯文学）": "爽感、爆发、极端、发疯",
            "🐱 Meme抗象流（低成本+病毒传播）": "幽默、病毒、洗脑、解压",
        }
        return strategies.get(style, "高能、反转、扎心")
    
    def _estimate_views(self, heat):
        """
        根据热度预估播放量
        """
        # 简单线性估算，实际应基于历史数据
        return int(heat * 15)  # 热度 * 15 ≈ 预估播放量
    
    def generate_daily_missions(self, count=3):
        """
        生成每日任务列表
        
        Args:
            count: 任务数量（默认3条）
        
        Returns:
            任务列表
        """
        if not self.trending_pool:
            self.scan_all_platforms()
        
        missions = []
        used_topics = set()
        
        for trend in self.trending_pool:
            if len(missions) >= count:
                break
            
            # 避免重复话题
            if trend['topic'] in used_topics:
                continue
            
            # 只选择中高热度
            if trend['heat'] < self.HEAT_THRESHOLD['medium']:
                continue
            
            # 构建任务
            style = self.STYLE_ROUTING.get(trend['type'], "🗡️ 认知刺客流（冲击力+优越感）")
            
            mission = {
                "mission_id": f"VTAXI-{datetime.now().strftime('%Y%m%d')}-{len(missions)+1:02d}",
                "topic": trend['topic'],
                "heat": trend['heat'],
                "style": style,
                "target_vibe": self._get_vibe_strategy(style),
                "estimated_views": self._estimate_views(trend['heat'])
            }
            
            missions.append(mission)
            used_topics.add(trend['topic'])
        
        st.success(f"✅ 生成 {len(missions)} 个今日跑单任务")
        return missions


# 🚀 快速测试接口
def test_navigator():
    """测试热点导航员"""
    st.header("🔍 热点导航员测试")
    
    nav = HotspotNavigator()
    
    if st.button("🔍 扫描热点", use_container_width=True):
        trends = nav.scan_all_platforms()
        
        st.subheader("📊 热点扫描结果")
        for i, trend in enumerate(trends[:10], 1):
            heat_level = nav.evaluate_heat(trend['heat'])
            heat_emoji = {"high": "🔥", "medium": "⚡", "low": "💤"}[heat_level]
            
            st.write(f"{i}. {heat_emoji} **{trend['topic']}** ({trend['heat']} 热度) - {trend['type']}")
    
    if st.button("🎯 生成今日任务", use_container_width=True):
        missions = nav.generate_daily_missions(count=3)
        
        st.subheader("🚖 今日跑单任务清单")
        for mission in missions:
            with st.expander(f"任务 {mission['mission_id']}", expanded=True):
                col1, col2 = st.columns(2)
                col1.metric("📍 话题", mission['topic'][:20] + "...")
                col2.metric("🔥 热度", mission['heat'])
                
                col3, col4 = st.columns(2)
                col3.metric("🎨 风格", mission['style'][:10])
                col4.metric("👁️ 预估播放", f"{mission['estimated_views']:,}")
                
                st.caption(f"💡 策略: {mission['target_vibe']}")


if __name__ == "__main__":
    # Streamlit 调试界面
    test_navigator()
