"""
网页采集模块
支持多种网页结构，采集价格、招聘信息、销售线索等
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional
import re
import time
import json


class WebScraper:
    """网页采集器"""
    
    def __init__(self, config_path: str = "config/sites.json"):
        self.config_path = Path(config_path)
        self.sites = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
    def load_config(self):
        """加载采集目标配置"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.sites = json.load(f)
        
        return self.sites
    
    def scrape_site(self, site_config: Dict) -> List[Dict]:
        """采集单个站点"""
        url = site_config['url']
        name = site_config['name']
        category = site_config.get('category', '通用')
        selectors = site_config.get('selectors', {})
        
        print(f"  采集: {name} ({url})")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = []
            
            # 根据配置的选择器提取数据
            item_selector = selectors.get('item', '.item')
            item_elements = soup.select(item_selector)
            
            if not item_elements:
                # 如果选择器没匹配到，尝试通用提取
                items = self._extract_generic(soup, url, name, category)
            else:
                for elem in item_elements:
                    item = {
                        "来源站点": name,
                        "来源URL": url,
                        "分类": category,
                        "采集时间": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "原始URL": url
                    }
                    
                    # 提取标题
                    title_sel = selectors.get('title', 'h2, h3, .title')
                    title_elem = elem.select_one(title_sel)
                    if title_elem:
                        item['标题'] = title_elem.get_text(strip=True)
                    
                    # 提取价格
                    price_sel = selectors.get('price', '.price, .amount, [class*=price]')
                    price_elem = elem.select_one(price_sel)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        item['价格'] = self._extract_price(price_text)
                    
                    # 提取描述
                    desc_sel = selectors.get('description', '.desc, .description, p')
                    desc_elem = elem.select_one(desc_sel)
                    if desc_elem:
                        item['描述'] = desc_elem.get_text(strip=True)[:200]
                    
                    # 提取链接
                    link_elem = elem.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        if href.startswith('/'):
                            from urllib.parse import urljoin
                            href = urljoin(url, href)
                        item['详情链接'] = href
                    
                    # 提取其他自定义字段
                    for field, sel in selectors.get('fields', {}).items():
                        field_elem = elem.select_one(sel)
                        if field_elem:
                            item[field] = field_elem.get_text(strip=True)
                    
                    items.append(item)
            
            print(f"    ✓ 采集到 {len(items)} 条数据")
            return items
            
        except Exception as e:
            print(f"    ❌ 采集失败: {e}")
            return []
    
    def _extract_generic(self, soup: BeautifulSoup, url: str, name: str, category: str) -> List[Dict]:
        """通用提取（当没有配置选择器时）"""
        items = []
        
        # 尝试提取所有链接和标题
        for link in soup.find_all('a', href=True)[:50]:  # 限制数量
            text = link.get_text(strip=True)
            if len(text) > 5:  # 过滤太短的文本
                items.append({
                    "来源站点": name,
                    "来源URL": url,
                    "分类": category,
                    "采集时间": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "标题": text,
                    "详情链接": link['href'] if link['href'].startswith('http') else url + link['href'],
                    "原始URL": url
                })
        
        return items
    
    def _extract_price(self, text: str) -> Optional[float]:
        """从文本中提取价格"""
        # 匹配常见价格格式
        patterns = [
            r'[¥￥]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*元',
            r'USD\s*(\d+\.?\d*)',
            r'\$(\d+\.?\d*)',
            r'(\d+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        
        return None
    
    def scrape_all(self) -> List[Dict]:
        """采集所有配置的站点"""
        all_items = []
        
        for site in self.sites:
            items = self.scrape_site(site)
            all_items.extend(items)
            time.sleep(1)  # 礼貌延迟，避免请求过快
        
        return all_items
    
    def get_scrape_summary(self, items: List[Dict]) -> Dict:
        """获取采集摘要"""
        if not items:
            return {"总采集数": 0}
        
        sources = {}
        categories = {}
        
        for item in items:
            source = item.get('来源站点', '未知')
            category = item.get('分类', '未分类')
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "总采集数": len(items),
            "来源分布": sources,
            "分类分布": categories,
            "采集时间": time.strftime("%Y-%m-%d %H:%M:%S")
        }
