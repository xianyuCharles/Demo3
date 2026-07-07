"""
报表生成模块
生成CSV报表和HTML可视化看板
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json


class ReportGenerator:
    """报表生成器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_csv(self, items: List[Dict], filename: str = "采集数据.csv") -> Path:
        """生成CSV报表"""
        if not items:
            return None
        
        df = pd.DataFrame(items)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return output_path
    
    def generate_price_report(self, items: List[Dict]) -> Dict:
        """生成价格对比报表"""
        # 筛选有价格的数据
        priced_items = [item for item in items if item.get('价格')]
        
        if not priced_items:
            return {"file": None, "stats": {"有价格数据": 0}}
        
        df = pd.DataFrame(priced_items)
        
        # 按来源统计
        source_stats = df.groupby('来源站点')['价格'].agg(['count', 'mean', 'min', 'max']).round(2)
        source_stats.columns = ['数量', '平均价格', '最低价', '最高价']
        
        # 按分类统计
        category_stats = df.groupby('分类')['价格'].agg(['count', 'mean']).round(2)
        category_stats.columns = ['数量', '平均价格']
        
        # 保存报表
        stats_path = self.output_dir / "价格统计.csv"
        with pd.ExcelWriter(stats_path) as writer:
            source_stats.to_excel(writer, sheet_name='按来源')
            category_stats.to_excel(writer, sheet_name='按分类')
            df.to_excel(writer, sheet_name='全部数据', index=False)
        
        # 生成完整数据CSV
        price_csv = self.output_dir / "价格清单.csv"
        df.to_csv(price_csv, index=False, encoding='utf-8-sig')
        
        return {
            "file": stats_path,
            "csv": price_csv,
            "stats": {
                "有价格数据": len(priced_items),
                "平均价格": round(df['价格'].mean(), 2),
                "最低价": round(df['价格'].min(), 2),
                "最高价": round(df['价格'].max(), 2)
            }
        }
    
    def generate_html_dashboard(self, items: List[Dict], stats: Dict) -> Path:
        """生成HTML可视化看板"""
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>网页采集看板</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stat-card .number {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .stat-card .label {{ color: #666; margin-top: 5px; }}
        .content {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background: #f8f9fa; }}
        .price {{ color: #e74c3c; font-weight: bold; }}
        .source {{ color: #3498db; }}
        .category {{ background: #ecf0f1; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 网页采集数据看板</h1>
        <p>采集时间: {stats.get('采集时间', '未知')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="number">{stats.get('总采集数', 0)}</div>
            <div class="label">总采集数</div>
        </div>
        <div class="stat-card">
            <div class="number">{len(stats.get('来源分布', {}))}</div>
            <div class="label">数据来源</div>
        </div>
        <div class="stat-card">
            <div class="number">{len(stats.get('分类分布', {}))}</div>
            <div class="label">数据分类</div>
        </div>
        <div class="stat-card">
            <div class="number">{stats.get('新增数据', 0)}</div>
            <div class="label">本次新增</div>
        </div>
    </div>
    
    <div class="content">
        <h2>最新采集数据</h2>
        <table>
            <thead>
                <tr>
                    <th>标题</th>
                    <th>价格</th>
                    <th>来源</th>
                    <th>分类</th>
                    <th>采集时间</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 添加数据行（最多显示20条）
        for item in items[:20]:
            title = item.get('标题', '-')[:50]
            price = f"¥{item['价格']}" if item.get('价格') else '-'
            source = item.get('来源站点', '-')
            category = item.get('分类', '-')
            time_str = item.get('采集时间', '-')
            
            price_class = 'price' if item.get('价格') else ''
            
            html_content += f"""
                <tr>
                    <td>{title}</td>
                    <td class="{price_class}">{price}</td>
                    <td class="source">{source}</td>
                    <td><span class="category">{category}</span></td>
                    <td>{time_str}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
    
    <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
        <p>星亦网络科技工作室 - 网页采集系统</p>
    </div>
</body>
</html>"""
        
        output_path = self.output_dir / "采集看板.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
