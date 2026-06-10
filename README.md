# XXZY · 全国气象可视化项目

[![GitHub Stars](https://img.shields.io/github/stars/007wwww123/XXZY?style=social)](https://github.com/007wwww123/XXZY)
[![License](https://img.shields.io/github/license/007wwww123/XXZY)](https://github.com/007wwww123/XXZY/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

> **仓库地址**：[https://github.com/007wwww123/XXZY.git](https://github.com/007wwww123/XXZY.git)

## 项目简介

基于 **ECharts** 与 **Open-Meteo API** 的轻量级全国省级气象可视化应用，同时提供 Python 数据处理管道，用于抓取、清洗、聚合省级天气数据并导出交互式地图。

> **建模策略**：项目以省会城市观测值代表所在省级行政区，属于简化建模方案，适合学习气象数据可视化与数据处理流程。

---

## 目录

- [快速开始](#快速开始)
- [功能特点](#功能特点)
- [环境要求](#环境要求)
- [安装步骤](#安装步骤)
- [使用方法](#使用方法)
- [目录结构](#目录结构)
- [核心模块](#核心模块)
- [数据说明](#数据说明)
- [部署说明](#部署说明)
- [常见问题](#常见问题)
- [开发规划](#开发规划)
- [贡献指南](#贡献指南)
- [更新日志](#更新日志)

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/007wwww123/XXZY.git
cd XXZY

# 启动本地服务器（推荐）
cd weather-map/web
python -m http.server 8080

# 浏览器访问
# ├── 实时气象地图：http://localhost:8080/index.html
# └── 15天天气预报：http://localhost:8080/forecast.html
```

---

## 功能特点

### 功能一：实时气象数据地图（Web 前端）

| 特性 | 说明 |
|------|------|
| **实时数据** | 对接 [Open-Meteo API](https://open-meteo.com/)，获取全国省会当前气温与降水 |
| **双模式切换** | 一键切换降水 / 气温视图，自动更新地图填色与色阶图例 |
| **交互体验** | 支持缩放、平移，Tooltip 展示详细气象信息 |
| **本地缓存** | LocalStorage 缓存（TTL 10 分钟），减少重复请求 |
| **自动刷新** | 可配置 5 / 10 / 30 / 60 分钟自动更新 |
| **响应式布局** | 适配桌面端与移动端 |

### 功能二：15 天动态天气预报（Web 前端）

| 特性 | 说明 |
|------|------|
| **预报数据** | 基于中国天气网爬虫生成的 `weather_15day_forecast.json` |
| **动态时间轴** | 支持播放 / 暂停、快进 / 快退、速度调节 |
| **双模式展示** | 降水量与气温两种可视化模式 |
| **统计面板** | 实时显示平均降水、平均气温、降雨城市数量 |

#### 15 天预报地图优化特性（v1.1.1）

- **南海诸岛处理**：地图不包含南海诸岛区域标注（无相关天气数据）
- **地图交互优化**：固定地图位置，禁止拖拽，保持页面布局稳定
- **缩放控制**：设置缩放比例上下限（1.2x - 4x），防止无限缩放
- **省份名称显示**：鼠标悬停时以黑色加粗字体展示省份名称
- **边界样式**：地图边界加粗处理，与实时气象地图风格一致

### 功能三：Python 数据处理管道（后端）

| 特性 | 说明 |
|------|------|
| **多数据源** | Open-Meteo API（api）、中国天气网当日爬取（web）、15 天预报（web15d） |
| **批量抓取** | 按 `provinces.csv` 并发抓取全国省级数据，含重试与限速 |
| **省名对齐** | `map_join` 模块将数据省名与 GeoJSON 命名体系统一 |
| **规划能力** | Parquet 存储、pyecharts 分层设色 HTML 导出（transform / export / choropleth / cli 待完善） |

---

## 环境要求

### 组件要求

| 组件 | 要求 |
|------|------|
| **浏览器** | Chrome 90+、Firefox 88+、Safari 14+、Edge 90+ |
| **Python** | 3.10+（仅后端 / 爬虫功能需要） |
| **网络** | 需访问 Open-Meteo API；爬虫功能需访问中国天气网 |

### Python 依赖

```
pandas>=2.0.0
requests>=2.31.0
pyecharts>=2.0.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pyarrow>=14.0.0
```

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/007wwww123/XXZY.git
cd XXZY
```

### 2. 安装 Python 依赖（可选）

> 仅后端功能需要，如只需使用 Web 前端可跳过此步骤。

```bash
cd weather-map
pip install -r requirements.txt
```

### 3. 准备前端静态资源

`web/index.html` 依赖以下本地文件，请确保存在：

```
weather-map/web/
├── vendor/echarts.min.js          # 可从 https://echarts.apache.org 下载
├── assets/china-provinces.js      # 省级 GeoJSON（由 china_province.geojson 转换）
└── assets/province-capitals.js    # 省会坐标映射表
```

> **注意**：`forecast.html` 已通过 CDN 加载 ECharts，无需本地 vendor 文件。

### 4. 准备地理基准数据（Python 管道需要）

```
weather-map/data/geo/china_province.geojson   # 中国省级边界 GeoJSON
```

---

## 使用方法

### 方式一：实时气象地图（推荐入门）

直接用浏览器打开 `web/index.html` 文件即可运行：

```bash
# Windows
start weather-map/web/index.html

# macOS
open weather-map/web/index.html

# Linux
xdg-open weather-map/web/index.html
```

> 由于浏览器安全策略，**直接打开本地文件时 AJAX 请求可能受限**。建议使用本地服务器：

```bash
cd weather-map/web
python -m http.server 8080
# 然后访问 http://localhost:8080
```

### 方式二：15 天动态预报

```bash
cd weather-map/web
python -m http.server 8080
# 浏览器访问：http://localhost:8080/forecast.html
```

### 方式三：Python 数据抓取

在 `weather-map` 目录下，将 `src` 加入 Python 路径后调用：

```python
from weather_map.services.fetch import fetch_weather_data, fetch_all_provinces

# 单点 API 抓取
df = fetch_weather_data(source="api", latitude=39.9, longitude=116.4)

# 全国批量抓取（Open-Meteo，含并发重试）
df = fetch_all_provinces()

# 中国天气网当日爬取
df = fetch_weather_data(source="web")

# 15 天预报爬取
df = fetch_weather_data(source="web15d")
```

### 方式四：运行测试

```bash
cd weather-map
python -m unittest discover -s tests -v
```

---

## 目录结构

```
XXZY/
├── README.md                         # 项目文档
└── weather-map/                       # 核心子项目
    ├── requirements.txt               # Python 依赖清单
    ├── data/                          # 数据层
    │   ├── geo/                       # 地理基准（GeoJSON、省名映射）
    │   ├── lookup/                    # 静态查表（provinces.csv）
    │   └── cache/                     # 运行时缓存
    ├── src/weather_map/               # Python 后端
    │   ├── adapters/                  # 数据源适配器
    │   ├── services/                  # 抓取、转换、关联、导出
    │   ├── utils/                    # 缓存、HTTP、日志等工具
    │   └── viz/                       # pyecharts 可视化
    ├── tests/                         # 单元测试
    ├── web/                           # 前端页面与脚本
    └── .github/workflows/             # CI/CD 部署配置
```

---

## 核心模块

### 前端模块（`weather-map/web/js/`）

| 模块 | 文件 | 职责 |
|------|------|------|
| 配置中心 | `config.js` | Open-Meteo API 参数、色阶图例、缓存策略 |
| API 客户端 | `openMeteoClient.js` | 批量请求省会坐标、解析 JSON 响应 |
| 数据服务 | `weatherService.js` | 缓存读写、数据归一化、地图数据集构建 |
| 地图渲染 | `mapView.js` | ECharts 注册地图、分层设色、Tooltip |
| 缓存管理 | `storage.js` | LocalStorage 读写与 TTL 校验 |
| 应用入口 | `app.js` | 模式切换、自动刷新、状态栏更新 |

### 后端模块（`weather-map/src/weather_map/`）

| 模块 | 文件 | 状态 | 职责 |
|------|------|------|------|
| 配置 | `config.py` | ✅ | 目录路径、默认参数 |
| API 适配器 | `adapters/open_meteo_api.py` | ✅ | Open-Meteo 请求与 DataFrame 归一化 |
| 爬虫适配器 | `adapters/weather_web.py` | ✅ | 中国天气网 HTML 解析、15 天预报 |
| 数据抓取 | `services/fetch.py` | ✅ | 统一入口、全国批量并发抓取 |
| 省名对齐 | `services/map_join.py` | ✅ | 省名映射、GeoJSON 属性关联 |
| 地理缓存 | `utils/geo_cache.py` | ✅ | GeoJSON / CSV / JSON 缓存加载 |
| 数据转换 | `services/transform.py` | 🚧 | 清洗、聚合（待实现） |
| 数据导出 | `services/export.py` | 🚧 | Parquet 导出（待实现） |
| 地图可视化 | `viz/choropleth.py` | 🚧 | pyecharts HTML 导出（待实现） |
| 命令行 | `cli.py` | 🚧 | CLI 流水线编排（待实现） |

> **图例**：✅ 已完成 | 🚧 待实现

### 数据流程（规划中的完整管道）

```
provinces.csv 
    ↓ 抓取(Fetch)
归一化 
    ↓
Parquet(raw)
    ↓ 清洗聚合(Transform)
Parquet(processed)
    ↓ 省名对齐(Map Join)
可视化(Render)
    ↓
outputs/html/
```

---

## 数据说明

### 实时数据（Open-Meteo）

| 项目 | 说明 |
|------|------|
| **接口** | `https://api.open-meteo.com/v1/forecast` |
| **变量** | `temperature_2m`（2 米气温）、`precipitation`（降水量） |
| **时区** | Asia/Shanghai |
| **代表策略** | 省会观测值代表省级行政区 |

### 预报数据（中国天气网）

| 项目 | 说明 |
|------|------|
| **来源** | `https://www.weather.com.cn` |
| **范围** | 31 个省会城市 + 港澳台地区 |
| **时长** | 15 天（7 天 + 8–15 天） |
| **字段** | 最高温、最低温、降水量估算 |

### 色阶图例

**降水（mm/h）**：

```
无降水 #edf3f7 → 小雨 #a8d8ff → 中雨 #2f9bff → 大雨 #1f5fbf → 暴雨 #5b1a8e
```

**气温（°C）**：

```
极寒 #1f3b88 → 严寒 #276fbf → 寒冷 #44a7d8 → 偏冷 #7bc8a4 
    ↓
舒适 #f6df72 → 温暖 #f2a43a → 炎热 #d9482b → 高温 #8c1d18
```

---

## 部署说明

### 本地静态服务

```bash
cd weather-map/web
python -m http.server 8080
```

### GitHub Pages

项目已配置 `.github/workflows/deploy.yml`，推送至 `main` 分支后自动部署 `web/` 目录。

> **注意**：工作流中 `path: 'web/'` 相对于 `weather-map` 子目录；若从仓库根目录触发，需将路径改为 `weather-map/web/`。

### 生产环境建议

- Open-Meteo 支持 CORS，前端可直接调用
- 生产环境建议使用 HTTPS
- 爬虫功能请控制请求频率，遵守目标网站服务条款

---

## 常见问题

### Q1：打开 index.html 后地图空白或报错？

**原因**：缺少 `web/assets/` 或 `web/vendor/` 下的静态资源。

**解决**：按「安装步骤 · 第 3 步」补齐 `echarts.min.js`、`china-provinces.js`、`province-capitals.js`，并通过本地 HTTP 服务访问。

---

### Q2：API 请求失败或超时？

**原因**：网络不通或 Open-Meteo 响应慢（默认超时 12 秒）。

**解决**：检查网络连接；查看浏览器控制台错误；10 分钟内会优先使用 LocalStorage 缓存。

---

### Q3：地图上某些省份没有数据？

**原因**：省名与 GeoJSON 字段不一致。

**解决**：检查 `data/geo/name_map.json` 是否覆盖该省简称与全称的映射。

---

### Q4：python -m weather_map.cli 无响应？

**原因**：`cli.py` 目前为空实现，CLI 流水线尚未完成。

**解决**：直接使用 `fetch_weather_data()` / `fetch_all_provinces()` Python API，或等待 CLI 模块完善。

---

### Q5：15 天预报数据如何更新？

```python
from weather_map.services.fetch import fetch_weather_data
# 爬取后手动写入 web/weather_15day_forecast.json
```

> **建议**：每日更新一次，避免对目标网站造成压力。

---

### Q6：Python 导入模块失败？

```bash
cd weather-map
set PYTHONPATH=src          # Windows CMD
$env:PYTHONPATH="src"       # Windows PowerShell
export PYTHONPATH=src       # Linux / macOS
```

---

## 开发规划

### 已完成

- ✅ 实时降水 / 气温 Web 地图
- ✅ 15 天动态预报可视化
- ✅ Open-Meteo / 中国天气网数据适配器
- ✅ 全国批量抓取与省名对齐

### 待实现

- ⬜ CLI 一键流水线
- ⬜ Parquet 存储与 pyecharts HTML 导出
- ⬜ 多城市加权聚合（替代省会单点代表）
- ⬜ 更多指标：风速、湿度、空气质量等

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交 Issue

在使用过程中遇到问题或有功能建议，请通过以下方式反馈：

1. 在 GitHub 仓库提交 Issue
2. 描述清楚问题或建议，包括复现步骤（如适用）

### 提交代码

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/YourFeature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/YourFeature`
5. **创建 Pull Request**

---

## 开源许可

**MIT License**

---

## 联系方式

- **Issues**：请在 GitHub 仓库提交 Issue 反馈 Bug 或功能建议
- **维护者**：请在仓库 About 页面查看作者信息

---

## 更新日志

### v1.1.1（2026-06-09）

**15 天预报地图优化**：

- 移除南海诸岛区域标注（无天气数据）
- 固定地图位置，禁止拖拽
- 设置缩放比例上下限（1.2x - 4x）
- 鼠标悬停显示黑色加粗省份名称
- 地图边界加粗处理
- 项目结构优化：删除冗余的 `weather-map/README.md`，统一文档管理

### v1.1.0（2026-06-08）

- 新增 15 天动态天气预报页面 `forecast.html`
- 集成中国天气网爬虫适配器
- 新增动态时间轴交互控制
- 支持降水量与气温双模式动态展示

### v1.0.0（2026-06-06）

- 初始版本：实时降水 / 气温双模式地图
- 集成 Open-Meteo API 与 ECharts 省级底图
