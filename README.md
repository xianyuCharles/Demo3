# Demo3: 网页公开信息采集系统

自动采集网页公开信息，去重整理后生成结构化报表和可视化看板。

## 功能

- ✅ 网页公开信息采集（价格、招聘、销售线索等）
- ✅ 自动去重（基于内容哈希）
- ✅ 生成价格/线索对比报表
- ✅ 可视化数据看板（HTML）
- ✅ 企微/钉钉通知文案生成
- ✅ 支持自定义CSS选择器配置

## 使用方法

### 1. 配置采集目标

编辑 `config/sites.json`，添加要采集的网站：

```json
[
  {
    "name": "站点名称",
    "url": "https://example.com",
    "category": "分类",
    "selectors": {
      "item": ".item-selector",
      "title": ".title-selector",
      "price": ".price-selector"
    }
  }
]
```

### 2. 运行程序

双击运行 `网页采集工具.exe`

### 3. 查看结果

结果自动保存到 `output` 目录：

- `采集数据.csv` — 完整数据清单
- `价格清单.csv` — 有价格的数据
- `价格统计.xlsx` — 价格对比分析
- `采集看板.html` — 可视化看板
- `企微通知文案.txt` — 企微通知
- `钉钉通知文案.txt` — 钉钉通知

## 配置说明

### sites.json 字段说明

| 字段 | 说明 | 必填 |
|------|------|------|
| name | 站点名称 | ✅ |
| url | 采集URL | ✅ |
| category | 数据分类 | ✅ |
| selectors.item | 列表项选择器 | ✅ |
| selectors.title | 标题选择器 | |
| selectors.price | 价格选择器 | |
| selectors.description | 描述选择器 | |
| selectors.fields | 自定义字段 | |

### 选择器语法

支持标准CSS选择器：
- `.class` — 类选择器
- `#id` — ID选择器
- `tag` — 标签选择器
- `.class1.class2` — 多类组合
- `tag .class` — 后代选择器

## 技术栈

- Python 3.11+
- requests（HTTP请求）
- BeautifulSoup4（HTML解析）
- pandas（数据处理）
- PyInstaller（打包为exe）

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python scripts/process.py

# 打包
cd build
build.bat
```

## 项目结构

```
demo3-web-scraper/
├── modules/          # 核心模块
│   ├── scraper.py           # 网页采集
│   ├── dedup.py             # 去重模块
│   ├── report_generator.py  # 报表生成
│   └── notifier.py          # 通知生成
├── scripts/
│   └── process.py   # 主入口
├── config/
│   └── sites.json   # 采集配置
├── build/
│   └── build.bat    # 打包脚本
├── input/           # 输入目录
├── output/          # 输出结果目录
└── requirements.txt # 依赖清单
```

## 适用场景

- 竞品价格监控
- 招聘信息采集
- 销售线索收集
- 公开数据抓取

## 注意事项

- 仅采集公开可访问的信息
- 遵守目标网站的robots.txt规则
- 建议设置合理的采集间隔
- 部分网站可能需要登录或验证码
