# -*- coding: utf-8 -*-
"""
步骤1：深度选题与策略定位
热点筛选 + 爆款基因提取 + 竞争度分析
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
from .base_step import BaseStep, StepResult, StepContext


class TopicResearchStep(BaseStep):
    """
    深度选题与策略定位
    
    功能：
    1. 获取热点数据（热搜榜）
    2. 筛选高潜力话题（上升速度 + 垂直契合度）
    3. 分析爆款基因（Hook提取 + 痛点挖掘）
    4. 确定情绪价值和信息增量
    """
    
    step_id = "topic_research"
    step_name = "深度选题与策略定位"
    step_emoji = "🔍"
    step_description = "热点筛选 + 爆款基因提取 + 竞争度分析"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.tianapi_key = config.get("tianapi_key", "")
        self.llm_api_key = config.get("llm_api_key", "")
    
    async def execute(self, context: StepContext) -> StepResult:
        """
        执行选题研究
        
        流程：
        1. 获取抖音热搜榜
        2. AI分析每个热点的潜力
        3. 筛选最佳选题
        4. 提取爆款基因
        """
        try:
            # 1. 获取热点数据
            hot_topics = await self._fetch_hot_topics()
            
            if not hot_topics:
                return StepResult(
                    success=False,
                    message="获取热点数据失败",
                    error="无法连接到热点数据源"
                )
            
            # 2. 分析热点潜力
            analyzed_topics = await self._analyze_topics(hot_topics)
            
            # 3. 筛选最佳选题
            selected_topic = self._select_best_topic(analyzed_topics, context)
            
            # 4. 提取爆款基因
            viral_genes = await self._extract_viral_genes(selected_topic)
            
            # 更新上下文
            context.hot_topics = analyzed_topics
            context.selected_topic = selected_topic["topic"]
            context.topic_analysis = {
                "heat_score": selected_topic.get("heat_score", 0),
                "growth_rate": selected_topic.get("growth_rate", 0),
                "competition_level": selected_topic.get("competition", "medium"),
                "viral_genes": viral_genes,
                "emotion_value": viral_genes.get("emotion_value", "共鸣"),
                "info_increment": viral_genes.get("info_increment", "新知"),
                "target_hook": viral_genes.get("hook_pattern", "悬念式")
            }
            
            return StepResult(
                success=True,
                data={
                    "selected_topic": context.selected_topic,
                    "analysis": context.topic_analysis,
                    "candidates": analyzed_topics[:5]  # 前5候选
                },
                message=f"✅ 选定选题: {context.selected_topic}"
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message="选题研究失败",
                error=str(e)
            )
    
    async def _fetch_hot_topics(self) -> List[Dict]:
        """获取抖音热搜榜"""
        # 这里调用现有的 api_services.get_hot_topics
        # 为了示例，返回模拟数据
        await asyncio.sleep(0.5)  # 模拟网络延迟
        
        # 模拟热点数据
        return [
            {"topic": "职场35岁危机真相", "heat": 95, "growth": 0.8},
            {"topic": "AI取代不了的能力", "heat": 88, "growth": 0.6},
            {"topic": "年轻人为什么不想结婚", "heat": 92, "growth": 0.5},
            {"topic": "月入过万其实很容易", "heat": 85, "growth": 0.9},
            {"topic": "被误解最深的健康常识", "heat": 80, "growth": 0.7},
        ]
    
    async def _analyze_topics(self, topics: List[Dict]) -> List[Dict]:
        """AI分析热点潜力"""
        analyzed = []
        
        for topic in topics:
            # 计算潜力分数 = 热度 * 上升速度 / 竞争度
            heat_score = topic.get("heat", 50)
            growth_rate = topic.get("growth", 0.5)
            
            # 简单评估竞争度（实际应该用更复杂的算法）
            if heat_score > 90:
                competition = "high"
                competition_score = 0.3
            elif heat_score > 80:
                competition = "medium"
                competition_score = 0.6
            else:
                competition = "low"
                competition_score = 0.9
            
            # 潜力分数
            potential = heat_score * growth_rate * competition_score
            
            analyzed.append({
                **topic,
                "heat_score": heat_score,
                "growth_rate": growth_rate,
                "competition": competition,
                "potential_score": round(potential, 2),
                "recommendation": self._get_recommendation(potential)
            })
        
        # 按潜力排序
        analyzed.sort(key=lambda x: x["potential_score"], reverse=True)
        return analyzed
    
    def _select_best_topic(self, analyzed: List[Dict], context: StepContext) -> Dict:
        """选择最佳选题"""
        # 优先选择潜力最高的
        # 实际应用中可以考虑用户的垂直领域偏好
        return analyzed[0] if analyzed else {"topic": "默认选题", "potential_score": 0}
    
    async def _extract_viral_genes(self, topic: Dict) -> Dict:
        """提取爆款基因"""
        # 这里应该调用 LLM 分析
        # 模拟分析结果
        topic_text = topic.get("topic", "")
        
        # 根据话题类型推断爆款基因
        if "职场" in topic_text or "35岁" in topic_text:
            return {
                "emotion_value": "焦虑共鸣 + 希望赋能",
                "info_increment": "打破认知误区",
                "hook_pattern": "反常识开场 + 数据冲击",
                "pain_points": ["年龄焦虑", "职业安全感", "收入不稳定"],
                "content_angle": "真相揭露 + 解决方案"
            }
        elif "AI" in topic_text:
            return {
                "emotion_value": "好奇 + 危机感",
                "info_increment": "未来能力图谱",
                "hook_pattern": "预言式开场",
                "pain_points": ["被取代恐惧", "技能过时", "学习焦虑"],
                "content_angle": "趋势洞察 + 行动指南"
            }
        else:
            return {
                "emotion_value": "共鸣",
                "info_increment": "新知",
                "hook_pattern": "悬念式",
                "pain_points": ["普遍痛点"],
                "content_angle": "观点输出"
            }
    
    def _get_recommendation(self, potential: float) -> str:
        """获取推荐等级"""
        if potential > 50:
            return "强烈推荐"
        elif potential > 30:
            return "推荐尝试"
        else:
            return "谨慎考虑"
