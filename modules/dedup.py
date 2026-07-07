"""
去重模块
基于内容哈希进行智能去重
"""
import hashlib
import pandas as pd
from typing import List, Dict, Tuple
from pathlib import Path
import json


class Deduplicator:
    """数据去重器"""
    
    def __init__(self, history_file: str = "config/history.json"):
        self.history_file = Path(history_file)
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """加载历史记录"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"seen_hashes": []}
    
    def _save_history(self):
        """保存历史记录"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def _compute_hash(self, item: Dict) -> str:
        """计算数据项的哈希值"""
        # 使用标题+来源URL作为唯一标识
        key = f"{item.get('标题', '')}|{item.get('来源URL', '')}|{item.get('详情链接', '')}"
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def deduplicate(self, items: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        去重
        返回: (新数据, 重复数据)
        """
        new_items = []
        duplicate_items = []
        
        for item in items:
            item_hash = self._compute_hash(item)
            
            if item_hash in self.history["seen_hashes"]:
                duplicate_items.append(item)
            else:
                new_items.append(item)
                self.history["seen_hashes"].append(item_hash)
        
        # 保存更新后的历史
        self._save_history()
        
        return new_items, duplicate_items
    
    def reset_history(self):
        """重置历史记录"""
        self.history = {"seen_hashes": []}
        self._save_history()
    
    def get_stats(self) -> Dict:
        """获取去重统计"""
        return {
            "已记录数据量": len(self.history.get("seen_hashes", []))
        }
    
    def to_dataframe(self, items: List[Dict]) -> pd.DataFrame:
        """转换为DataFrame"""
        if not items:
            return pd.DataFrame()
        
        df = pd.DataFrame(items)
        
        # 整理列顺序
        preferred_cols = ['标题', '价格', '来源站点', '分类', '描述', '详情链接', '采集时间']
        available_cols = [c for c in preferred_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in preferred_cols]
        
        return df[available_cols + other_cols]
