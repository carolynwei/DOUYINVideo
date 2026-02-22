# -*- coding: utf-8 -*-
"""
VideoTaxi 调度塔台 (Scheduler Tower)
7x24小时无人值守自动驾驶系统

核心功能：
1. 定时任务调度 - 每日凌晨自动扫描热点并生成视频
2. 数据感应导航 - 根据历史表现自动优化创作策略
3. 自动发布对接 - 将成品推送至抖音草稿箱
4. 反馈闭环学习 - 让AI越跑越聪明
"""

import os
import json
import time
import schedule
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import streamlit as st


@dataclass
class PerformanceMetrics:
    """视频表现数据模型"""
    video_id: str
    topic: str
    style: str
    publish_time: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    completion_rate: float = 0.0  # 完播率
    sentiment_score: float = 0.0  # 情绪得分（基于评论）
    
    def calculate_score(self) -> float:
        """计算综合表现分数"""
        # 权重：完播率40% + 互动率30% + 点赞率20% + 分享率10%
        if self.views == 0:
            return 0.0
        
        engagement_rate = (self.likes + self.comments + self.shares) / self.views
        like_rate = self.likes / self.views
        share_rate = self.shares / self.views
        
        score = (
            self.completion_rate * 0.4 +
            engagement_rate * 0.3 +
            like_rate * 0.2 +
            share_rate * 0.1
        ) * 100
        
        return round(score, 2)


class FeedbackDatabase:
    """
    反馈数据持久化层
    存储视频表现数据，用于策略优化
    """
    
    def __init__(self, db_path: str = "videotaxi_feedback.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 视频表现数据表
        c.execute('''
            CREATE TABLE IF NOT EXISTS video_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                topic TEXT,
                style TEXT,
                emotion_vibe TEXT,
                publish_time TIMESTAMP,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                completion_rate REAL DEFAULT 0.0,
                sentiment_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 风格表现统计表（用于策略优化）
        c.execute('''
            CREATE TABLE IF NOT EXISTS style_performance (
                style TEXT PRIMARY KEY,
                total_videos INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0.0,
                best_topic TEXT,
                best_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 情绪表现统计表
        c.execute('''
            CREATE TABLE IF NOT EXISTS emotion_performance (
                emotion_vibe TEXT PRIMARY KEY,
                total_videos INTEGER DEFAULT 0,
                avg_completion_rate REAL DEFAULT 0.0,
                avg_engagement_rate REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_performance(self, metrics: PerformanceMetrics):
        """保存视频表现数据"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO video_performance 
            (video_id, topic, style, publish_time, views, likes, comments, shares, completion_rate, sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.video_id, metrics.topic, metrics.style, metrics.publish_time,
            metrics.views, metrics.likes, metrics.comments, metrics.shares,
            metrics.completion_rate, metrics.sentiment_score
        ))
        
        conn.commit()
        conn.close()
        
        # 更新统计表
        self._update_style_stats(metrics.style)
    
    def _update_style_stats(self, style: str):
        """更新风格表现统计"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 计算该风格的平均表现
        c.execute('''
            SELECT AVG(completion_rate), COUNT(*), MAX(completion_rate), topic
            FROM video_performance 
            WHERE style = ?
            GROUP BY style
        ''', (style,))
        
        result = c.fetchone()
        if result:
            avg_score, total, best_score, best_topic = result
            
            c.execute('''
                INSERT OR REPLACE INTO style_performance 
                (style, total_videos, avg_score, best_topic, best_score, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (style, total, avg_score, best_topic, best_score, datetime.now()))
            
            conn.commit()
        
        conn.close()
    
    def get_style_ranking(self) -> List[Dict]:
        """获取风格表现排名"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT style, total_videos, avg_score, best_topic, best_score
            FROM style_performance
            ORDER BY avg_score DESC
        ''')
        
        results = []
        for row in c.fetchall():
            results.append({
                'style': row[0],
                'total_videos': row[1],
                'avg_score': row[2],
                'best_topic': row[3],
                'best_score': row[4]
            })
        
        conn.close()
        return results
    
    def get_best_performing_style(self) -> Optional[str]:
        """获取表现最好的风格"""
        ranking = self.get_style_ranking()
        if ranking:
            return ranking[0]['style']
        return None
    
    def get_recent_performance(self, days: int = 7) -> List[PerformanceMetrics]:
        """获取最近N天的表现数据"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        c.execute('''
            SELECT video_id, topic, style, publish_time, views, likes, comments, shares, completion_rate, sentiment_score
            FROM video_performance
            WHERE publish_time > ?
            ORDER BY publish_time DESC
        ''', (since,))
        
        results = []
        for row in c.fetchall():
            results.append(PerformanceMetrics(
                video_id=row[0],
                topic=row[1],
                style=row[2],
                publish_time=row[3],
                views=row[4],
                likes=row[5],
                comments=row[6],
                shares=row[7],
                completion_rate=row[8],
                sentiment_score=row[9]
            ))
        
        conn.close()
        return results


class DataAwareNavigator:
    """
    数据感应导航员
    基于历史表现数据优化热点选择和风格分配
    """
    
    def __init__(self, navigator, feedback_db: FeedbackDatabase):
        self.navigator = navigator
        self.feedback_db = feedback_db
        self.style_weights = self._load_style_weights()
    
    def _load_style_weights(self) -> Dict[str, float]:
        """加载风格权重（基于历史表现）"""
        ranking = self.feedback_db.get_style_ranking()
        weights = {}
        
        # 基础权重
        base_weight = 1.0
        
        for i, item in enumerate(ranking):
            # 排名越高，权重越高
            # 第1名：1.5倍，第2名：1.3倍，第3名：1.1倍...
            weight = base_weight + (0.5 - i * 0.1)
            weights[item['style']] = max(weight, 0.8)  # 最低0.8
        
        return weights
    
    def scan_high_value_target(self, num: int = 3) -> List[Dict]:
        """
        扫描高价值目标
        结合热度、风格表现历史、时段因素综合评估
        """
        # 获取原始热点
        raw_missions = self.navigator.fetch_today_missions(num * 2)  # 多获取一些用于筛选
        
        scored_missions = []
        for mission in raw_missions:
            base_score = mission['hot_value']
            style = mission['recommended_style']
            
            # 应用风格权重
            weight = self.style_weights.get(style, 1.0)
            adjusted_score = base_score * weight
            
            # 添加策略评分
            mission['strategy_score'] = adjusted_score
            mission['style_weight'] = weight
            
            scored_missions.append(mission)
        
        # 按策略评分排序，返回前N个
        scored_missions.sort(key=lambda x: x['strategy_score'], reverse=True)
        return scored_missions[:num]
    
    def get_strategy_report(self) -> Dict:
        """生成策略报告"""
        ranking = self.feedback_db.get_style_ranking()
        recent = self.feedback_db.get_recent_performance(days=7)
        
        # 计算最近7天的平均表现
        if recent:
            avg_completion = sum(r.completion_rate for r in recent) / len(recent)
            total_views = sum(r.views for r in recent)
        else:
            avg_completion = 0
            total_views = 0
        
        return {
            'style_ranking': ranking,
            'recent_avg_completion': round(avg_completion * 100, 2),
            'recent_total_views': total_views,
            'total_videos_7d': len(recent),
            'recommended_style': self.feedback_db.get_best_performing_style()
        }


class SchedulerTower:
    """
    VideoTaxi 调度塔台
    核心调度逻辑，实现全自动无人值守
    """
    
    def __init__(self, 
                 tianapi_key: str,
                 deepseek_key: str,
                 zhipu_key: str,
                 pexels_key: str = "",
                 output_dir: str = "./output"):
        
        self.tianapi_key = tianapi_key
        self.deepseek_key = deepseek_key
        self.zhipu_key = zhipu_key
        self.pexels_key = pexels_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化组件
        from tianapi_navigator import TianapiNavigator
        self.navigator = TianapiNavigator(tianapi_key)
        self.feedback_db = FeedbackDatabase()
        self.data_navigator = DataAwareNavigator(self.navigator, self.feedback_db)
        
        # 运行状态
        self.is_running = False
        self.daily_stats = {
            'generated_today': 0,
            'last_run': None
        }
    
    def auto_drive_mission(self, num_videos: int = 1) -> List[Dict]:
        """
        自动驾驶任务核心逻辑
        
        Args:
            num_videos: 本次生成视频数量
            
        Returns:
            任务结果列表
        """
        print(f"\n{'='*60}")
        print(f"🚗 VideoTaxi 自动驾驶任务启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        results = []
        
        # 1. 数据感应导航 - 获取高价值目标
        print("🛰️ 步骤1: 数据感应导航 - 扫描高价值目标...")
        missions = self.data_navigator.scan_high_value_target(num_videos)
        
        if not missions:
            print("❌ 未找到合适的热点任务")
            return results
        
        print(f"✅ 锁定 {len(missions)} 个高价值目标")
        for m in missions:
            print(f"   🔥 {m['topic']} (策略评分: {m['strategy_score']:.0f})")
        
        # 2. 逐个生成视频
        for i, mission in enumerate(missions):
            print(f"\n📦 任务 {i+1}/{len(missions)}: {mission['topic']}")
            
            try:
                result = self._generate_single_video(mission, i+1)
                results.append(result)
                
                if result['status'] == 'success':
                    self.daily_stats['generated_today'] += 1
                    print(f"   ✅ 成功: {result['video_file']}")
                else:
                    print(f"   ❌ 失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append({
                    'topic': mission['topic'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 3. 更新统计
        self.daily_stats['last_run'] = datetime.now().isoformat()
        
        # 4. 输出总结
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\n{'='*60}")
        print(f"📊 任务总结: 成功 {success_count}/{len(results)}")
        print(f"{'='*60}\n")
        
        return results
    
    def _generate_single_video(self, mission: Dict, index: int) -> Dict:
        """生成单个视频"""
        from api_services import generate_script_by_style
        from video_engine import render_ai_video_pipeline
        
        topic = mission['topic']
        style = mission['recommended_style']
        
        # 生成视频ID
        video_id = f"VT{datetime.now().strftime('%Y%m%d')}_{index:03d}"
        output_file = self.output_dir / f"{video_id}_{topic[:20]}.mp4"
        
        # 生成剧本
        print(f"   🎬 生成剧本...")
        scenes_data = generate_script_by_style(
            topic=topic,
            style=style,
            api_key=self.deepseek_key,
            auto_image_prompt=True
        )
        
        if not scenes_data:
            return {
                'video_id': video_id,
                'topic': topic,
                'status': 'failed',
                'error': '剧本生成失败'
            }
        
        print(f"   ✅ 剧本完成: {len(scenes_data)} 个分镜")
        
        # 渲染视频
        print(f"   🎥 渲染视频...")
        success = render_ai_video_pipeline(
            scenes_data=scenes_data,
            zhipu_key=self.zhipu_key,
            output_path=str(output_file),
            pexels_key=self.pexels_key,
            voice_id="zh-CN-YunxiNeural",
            style_name=style
        )
        
        if success and output_file.exists():
            # 保存表现记录（初始数据，后续更新）
            metrics = PerformanceMetrics(
                video_id=video_id,
                topic=topic,
                style=style,
                publish_time=datetime.now().isoformat()
            )
            self.feedback_db.save_performance(metrics)
            
            return {
                'video_id': video_id,
                'topic': topic,
                'status': 'success',
                'video_file': str(output_file),
                'style': style,
                'scenes_count': len(scenes_data)
            }
        else:
            return {
                'video_id': video_id,
                'topic': topic,
                'status': 'failed',
                'error': '视频渲染失败'
            }
    
    def schedule_daily_run(self, run_time: str = "04:00", num_videos: int = 1):
        """
        设置每日定时运行
        
        Args:
            run_time: 运行时间，格式 "HH:MM"
            num_videos: 每次生成视频数量
        """
        schedule.every().day.at(run_time).do(self.auto_drive_mission, num_videos)
        print(f"⏰ 已设置每日 {run_time} 自动运行，每次生成 {num_videos} 个视频")
    
    def run_scheduler(self):
        """启动调度器（阻塞式）"""
        print("🚀 VideoTaxi 调度塔台已启动")
        print("📡 等待定时任务...")
        
        self.is_running = True
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        print("🛑 调度塔台已停止")
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表盘数据（供UI使用）"""
        strategy_report = self.data_navigator.get_strategy_report()
        
        return {
            'daily_stats': self.daily_stats,
            'strategy_report': strategy_report,
            'is_running': self.is_running,
            'next_run': schedule.next_run().strftime('%Y-%m-%d %H:%M:%S') if schedule.next_run() else None
        }


# 🧪 命令行测试接口
if __name__ == "__main__":
    import os
    
    # 从环境变量读取密钥
    tian_key = os.getenv("TIANAPI_KEY", "")
    deep_key = os.getenv("DEEPSEEK_KEY", "")
    zhipu_key = os.getenv("ZHIPU_KEY", "")
    pexels_key = os.getenv("PEXELS_KEY", "")
    
    if not all([tian_key, deep_key, zhipu_key]):
        print("❌ 请设置环境变量: TIANAPI_KEY, DEEPSEEK_KEY, ZHIPU_KEY")
        exit(1)
    
    # 创建调度塔台
    tower = SchedulerTower(
        tianapi_key=tian_key,
        deepseek_key=deep_key,
        zhipu_key=zhipu_key,
        pexels_key=pexels_key
    )
    
    # 模式选择
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # 立即执行一次
        print("🚗 立即执行模式")
        tower.auto_drive_mission(num_videos=1)
    else:
        # 定时调度模式
        print("⏰ 定时调度模式（每天04:00运行）")
        tower.schedule_daily_run(run_time="04:00", num_videos=1)
        
        try:
            tower.run_scheduler()
        except KeyboardInterrupt:
            tower.stop_scheduler()