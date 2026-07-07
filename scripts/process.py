"""
Demo3: 网页公开信息采集系统
主入口脚本

功能：
1. 采集网页公开信息（价格、招聘、线索等）
2. 自动去重整理
3. 生成对比报表和可视化看板
4. 生成企微/钉钉通知文案
"""
import sys
from pathlib import Path

# 兼容PyInstaller打包后的路径
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(BASE_DIR))

import os
os.chdir(BASE_DIR)

from modules.scraper import WebScraper
from modules.dedup import Deduplicator
from modules.report_generator import ReportGenerator
from modules.notifier import Notifier


def main():
    print("=" * 60)
    print("网页公开信息采集系统 v1.0")
    print("=" * 60)
    print()
    
    # 检查配置文件
    config_dir = Path("config")
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
        print("❌ config目录不存在，已自动创建")
        print("请在config目录创建sites.json配置文件")
        input("按回车键退出...")
        return
    
    sites_file = config_dir / "sites.json"
    if not sites_file.exists():
        print("❌ 未找到配置文件 config/sites.json")
        print("请先配置要采集的网站信息")
        input("按回车键退出...")
        return
    
    print(f"📋 加载配置: {sites_file.name}")
    
    try:
        # 初始化采集器
        scraper = WebScraper(str(sites_file))
        sites = scraper.load_config()
        print(f"  ✓ 已配置 {len(sites)} 个采集目标")
        print()
        
        # 开始采集
        print("正在采集网页数据...")
        all_items = scraper.scrape_all()
        
        if not all_items:
            print("\n⚠️ 未采集到任何数据")
            print("请检查:")
            print("  1. 网站是否可访问")
            print("  2. CSS选择器是否正确")
            print("  3. 是否需要登录或验证码")
            input("\n按回车键退出...")
            return
        
        # 获取采集摘要
        scrape_stats = scraper.get_scrape_summary(all_items)
        print(f"\n📊 采集完成: {scrape_stats['总采集数']} 条数据")
        print()
        
        # 去重
        print("正在去重...")
        dedup = Deduplicator()
        new_items, duplicate_items = dedup.deduplicate(all_items)
        
        print(f"  ✓ 新数据: {len(new_items)} 条")
        print(f"  ✓ 重复数据: {len(duplicate_items)} 条")
        
        dedup_stats = dedup.get_stats()
        print(f"  ✓ 历史累计: {dedup_stats['已记录数据量']} 条")
        print()
        
        # 生成报表
        print("正在生成报表...")
        report_gen = ReportGenerator()
        
        # CSV报表
        csv_path = report_gen.generate_csv(new_items)
        if csv_path:
            print(f"  ✓ 采集数据: {csv_path.name} ({len(new_items)} 条)")
        
        # 价格报表
        price_report = report_gen.generate_price_report(new_items)
        if price_report['file']:
            print(f"  ✓ 价格统计: {price_report['file'].name}")
            stats = price_report['stats']
            print(f"    平均价格: ¥{stats.get('平均价格', 0)}")
            print(f"    价格区间: ¥{stats.get('最低价', 0)} - ¥{stats.get('最高价', 0)}")
        
        # HTML看板
        update_stats = {
            "总采集数": scrape_stats['总采集数'],
            "新增数据": len(new_items),
            "来源分布": scrape_stats.get('来源分布', {}),
            "分类分布": scrape_stats.get('分类分布', {}),
            "采集时间": scrape_stats.get('采集时间', '')
        }
        
        html_path = report_gen.generate_html_dashboard(new_items, update_stats)
        print(f"  ✓ 可视化看板: {html_path.name}")
        print()
        
        # 生成通知文案
        print("正在生成通知文案...")
        notifier = Notifier()
        notifications = notifier.generate_all(update_stats, new_items)
        print(f"  ✓ 企微通知文案")
        print(f"  ✓ 钉钉通知文案")
        print()
        
        # 输出结果汇总
        output_dir = Path("output")
        print("=" * 60)
        print("✅ 采集完成！")
        print("=" * 60)
        print()
        print(f"结果已保存到: {output_dir.absolute()}")
        print()
        print("生成文件:")
        print(f"  📄 采集数据.csv — 完整数据清单")
        if price_report['csv']:
            print(f"  💰 价格清单.csv — 有价格的数据")
        if price_report['file']:
            print(f"  📊 价格统计.xlsx — 价格对比分析")
        print(f"  🌐 采集看板.html — 可视化看板（用浏览器打开）")
        print(f"  💬 企微通知文案.txt — 复制粘贴到企业微信")
        print(f"  💬 钉钉通知文案.txt — 复制粘贴到钉钉")
        
    except Exception as e:
        print(f"\n❌ 处理出错: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    # 打包模式下不等待
    if not getattr(sys, 'frozen', False):
        input("按回车键退出...")


if __name__ == "__main__":
    main()
