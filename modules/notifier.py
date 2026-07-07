"""
通知模块
生成企业微信和钉钉通知文案
"""
from typing import List, Dict
from pathlib import Path
import time


class Notifier:
    """通知生成器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_wechat_notification(self, stats: Dict, new_items: List[Dict]) -> str:
        """生成企业微信通知文案"""
        today = time.strftime("%Y-%m-%d")
        
        content = f"""【网页采集日报】{today}

📊 采集统计
• 总采集: {stats.get('总采集数', 0)} 条
• 本次新增: {stats.get('新增数据', 0)} 条
• 数据来源: {len(stats.get('来源分布', {}))} 个站点
• 数据分类: {len(stats.get('分类分布', {}))} 个类别

📈 来源分布
"""
        
        for source, count in stats.get('来源分布', {}).items():
            content += f"• {source}: {count} 条\n"
        
        if new_items:
            content += "\n🆕 最新数据\n"
            for item in new_items[:5]:  # 最多显示5条
                title = item.get('标题', '无标题')[:40]
                price = f" (¥{item['价格']})" if item.get('价格') else ""
                content += f"• {title}{price}\n"
        
        content += "\n详情请查看附件报表。"
        
        # 保存文案
        output_path = self.output_dir / "企微通知文案.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    def generate_dingtalk_notification(self, stats: Dict, new_items: List[Dict]) -> str:
        """生成钉钉通知文案"""
        today = time.strftime("%Y-%m-%d")
        
        content = f"""# 网页采集日报 {today}

## 📊 采集统计
- **总采集**: {stats.get('总采集数', 0)} 条
- **本次新增**: {stats.get('新增数据', 0)} 条
- **数据来源**: {len(stats.get('来源分布', {}))} 个站点

## 📈 来源分布
"""
        
        for source, count in stats.get('来源分布', {}).items():
            content += f"- {source}: {count} 条\n"
        
        if new_items:
            content += "\n## 🆕 最新数据\n"
            for item in new_items[:5]:
                title = item.get('标题', '无标题')[:40]
                price = f" (**¥{item['价格']}**)" if item.get('价格') else ""
                content += f"- {title}{price}\n"
        
        content += "\n> 详情请查看附件报表。"
        
        # 保存文案
        output_path = self.output_dir / "钉钉通知文案.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    def generate_all(self, stats: Dict, new_items: List[Dict]) -> Dict:
        """生成所有通知"""
        wechat = self.generate_wechat_notification(stats, new_items)
        dingtalk = self.generate_dingtalk_notification(stats, new_items)
        
        return {
            "wechat": wechat,
            "dingtalk": dingtalk
        }
