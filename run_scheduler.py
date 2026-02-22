# -*- coding: utf-8 -*-
"""
VideoTaxi 调度塔台启动脚本
用法:
    python run_scheduler.py --now     # 立即执行一次
    python run_scheduler.py           # 启动定时调度（每天04:00）
    python run_scheduler.py --time 06:00 --num 2  # 自定义时间和数量
"""

import os
import sys
import argparse

# 尝试加载 .env 文件（如果 python-dotenv 已安装）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 未安装 python-dotenv，跳过

from scheduler_tower import SchedulerTower


def main():
    parser = argparse.ArgumentParser(description='VideoTaxi 调度塔台')
    parser.add_argument('--now', action='store_true', 
                       help='立即执行一次，不启动定时调度')
    parser.add_argument('--time', type=str, default='04:00',
                       help='定时运行时间 (HH:MM格式，默认04:00)')
    parser.add_argument('--num', type=int, default=1,
                       help='每次生成视频数量 (默认1)')
    parser.add_argument('--output', type=str, default='./output',
                       help='视频输出目录 (默认./output)')
    
    args = parser.parse_args()
    
    # 读取API密钥
    tian_key = os.getenv("TIANAPI_KEY")
    deep_key = os.getenv("DEEPSEEK_KEY")
    zhipu_key = os.getenv("ZHIPU_KEY")
    pexels_key = os.getenv("PEXELS_KEY", "")
    
    # 验证密钥
    if not all([tian_key, deep_key, zhipu_key]):
        print("❌ 错误：缺少必要的API密钥")
        print("请设置以下环境变量：")
        print("  - TIANAPI_KEY")
        print("  - DEEPSEEK_KEY")
        print("  - ZHIPU_KEY")
        print("\n可以通过以下方式设置：")
        print("  1. 创建 .env 文件")
        print("  2. 使用 export 命令")
        print("  3. 在系统环境变量中设置")
        sys.exit(1)
    
    # 创建调度塔台
    print("🚀 正在启动 VideoTaxi 调度塔台...")
    tower = SchedulerTower(
        tianapi_key=tian_key,
        deepseek_key=deep_key,
        zhipu_key=zhipu_key,
        pexels_key=pexels_key,
        output_dir=args.output
    )
    
    if args.now:
        # 立即执行模式
        print(f"\n🚗 立即执行模式 - 生成 {args.num} 个视频\n")
        results = tower.auto_drive_mission(num_videos=args.num)
        
        # 输出结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\n{'='*60}")
        print(f"✅ 成功: {success_count}/{len(results)}")
        
        for r in results:
            if r['status'] == 'success':
                print(f"   📹 {r['video_file']}")
        
        print(f"{'='*60}\n")
        
    else:
        # 定时调度模式
        print(f"\n⏰ 定时调度模式")
        print(f"   每日运行时间: {args.time}")
        print(f"   每次生成数量: {args.num}")
        print(f"   输出目录: {args.output}")
        print(f"\n{'='*60}")
        print("按 Ctrl+C 停止调度塔台")
        print(f"{'='*60}\n")
        
        tower.schedule_daily_run(run_time=args.time, num_videos=args.num)
        
        try:
            tower.run_scheduler()
        except KeyboardInterrupt:
            print("\n🛑 正在停止调度塔台...")
            tower.stop_scheduler()
            print("✅ 已安全退出")


if __name__ == "__main__":
    main()