# 全国降水/气温实时地图

基于 ECharts 与 Open-Meteo API 开发的轻量级气象可视化应用，支持全国省级行政区实时降水与气温数据的展示。

## 功能特性

### 功能一：实时气象数据地图
- **实时气象数据**：集成 Open-Meteo API，获取全国省会城市当前气温、降水观测值
- **双模式切换**：一键切换降水/气温视图，自动更新地图填充色与色阶图例
- **交互工具**：支持缩放、平移，Tooltip 展示详细气象数据
- **数据缓存**：LocalStorage 缓存机制，减少重复 API 请求
- **自动刷新**：可配置自动刷新间隔（5分钟/10分钟/30分钟/1小时）
- **响应式设计**：适配桌面端与移动端

### 功能二：15天动态天气预报
- **网页爬取数据**：集成中国天气网爬虫，获取15天逐日天气预报数据
- **动态时间轴**：支持播放/暂停、快进/快退、速度调节等交互控制
- **双模式展示**：降水量与气温两种可视化模式
- **统计信息**：实时显示平均降水、平均气温、降雨城市数量
- **数据来源**：中国天气网15天预报（7天+8-15天）

## 目录结构

```
weather-map/
├── web/                          # 前端资源目录
│   ├── index.html                # 功能一：实时气象地图入口
│   ├── forecast.html             # 功能二：15天动态预报入口
│   ├── weather_15day_forecast.json  # 15天预报数据（爬虫生成）
│   ├── assets/
│   │   ├── china-provinces.js    # 中国省级行政区 GeoJSON（34个省级要素）
│   │   └── province-capitals.js   # 省会城市坐标与名称映射表
│   ├── js/
│   │   ├── app.js                # 应用主逻辑
│   │   ├── config.js             # 色阶图例与 API 配置
│   │   ├── mapView.js            # ECharts 地图渲染模块
│   │   ├── openMeteoClient.js    # Open-Meteo API 请求封装
│   │   ├── storage.js            # LocalStorage 缓存管理
│   │   └── weatherService.js     # 气象数据服务层
│   └── vendor/
│       └── echarts.min.js        # ECharts 库
├── data/
│   ├── cache/                    # 运行时缓存目录
│   │   └── geo/
│   ├── geo/                      # 地理数据
│   │   ├── china_province.geojson
│   │   └── name_map.json
│   └── lookup/                   # 查询数据
│       └── provinces.csv
├── src/                          # Python 后端源码
│   └── weather_map/
│       ├── adapters/             # API 适配器
│       │   ├── base.py           # 适配器基类
│       │   ├── open_meteo_api.py # Open-Meteo API 适配器
│       │   └── weather_web.py    # 中国天气网爬虫适配器
│       ├── services/             # 数据处理服务
│       │   ├── fetch.py          # 数据抓取服务（支持API/Web两种源）
│       │   ├── transform.py      # 数据转换
│       │   ├── map_join.py       # 地图数据关联
│       │   └── export.py         # 数据导出
│       ├── utils/                # 工具函数
│       ├── viz/                  # 可视化模块
│       └── cli.py                # 命令行接口
├── tests/                        # 测试用例
├── .github/workflows/            # GitHub Actions 自动部署
├── requirements.txt              # Python 依赖
└── README.md                     # 项目文档

```

## 快速开始

### 功能一：实时气象地图（纯前端，无需安装依赖）

直接用浏览器打开 `web/index.html` 文件即可运行：

```bash
# Windows
start weather-map/web/index.html

# macOS
open weather-map/web/index.html

# Linux
xdg-open weather-map/web/index.html
```

> 注意：由于浏览器安全策略，直接打开本地文件时 AJAX 请求可能受限。建议使用本地服务器：
> ```bash
> cd weather-map/web
> python -m http.server 8080
> # 然后访问 http://localhost:8080
> ```

### 功能二：15天动态预报

```bash
cd weather-map/web
python -m http.server 8080
# 访问 http://localhost:8080/forecast.html
```

### Python 后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端服务
cd src
python -m weather_map.cli serve

# 访问 http://localhost:5000
```

## 数据获取方式

### 方式一：API 数据获取（Open-Meteo）

```python
from weather_map.services.fetch import fetch_weather_data

# 获取实时天气数据
df = fetch_weather_data(source='api', latitude=39.9, longitude=116.4)
```

### 方式二：网页爬取（中国天气网）

```python
from weather_map.services.fetch import fetch_weather_data

# 获取当日天气数据（网页爬取）
df = fetch_weather_data(source='web')

# 获取15天预报数据（网页爬取）
df = fetch_weather_data(source='web15d')
```

## 数据说明

### 气象数据

#### 实时数据（Open-Meteo API）
- **数据源**：Open-Meteo API (https://api.open-meteo.com/v1/forecast)
- **请求变量**：`temperature_2m`（2米气温）、`precipitation`（总降水量）、`rain`（降雨量）
- **时区**：Asia/Shanghai
- **数据精度**：以省会城市观测站数据代表所在省级行政区

#### 预报数据（中国天气网爬取）
- **数据源**：中国天气网 (https://www.weather.com.cn)
- **数据范围**：全国31个省会城市（港澳台除外）
- **预报时长**：15天（7天预报 + 8-15天预报）
- **数据字段**：最高温、最低温、降水量估算
- **更新频率**：建议每日更新

### 色阶图例

#### 降水分级（mm/h）

| 等级 | 范围 | 颜色 |
|------|------|------|
| 暴雨 | ≥16 | #5b1a8e |
| 大雨 | 8-15.9 | #1f5fbf |
| 中雨 | 2.5-7.9 | #2f9bff |
| 小雨 | 0.1-2.4 | #a8d8ff |
| 无降水 | 0-0.09 | #edf3f7 |

#### 气温分级（°C）

| 等级 | 范围 | 颜色 |
|------|------|------|
| 高温 | ≥35 | #8c1d18 |
| 炎热 | 30-34.9 | #d9482b |
| 温暖 | 20-29.9 | #f2a43a |
| 舒适 | 10-19.9 | #f6df72 |
| 偏冷 | 0-9.9 | #7bc8a4 |
| 寒冷 | -10--0.1 | #44a7d8 |
| 严寒 | -20--10.1 | #276fbf |
| 极寒 | <-20 | #1f3b88 |

### 地理底图

- **GeoJSON 来源**：中国省级行政区划标准地图
- **要素数量**：34个省级行政区（不含南海诸岛等争议区域）
- **匹配字段**：`fullname`（如"北京市"、"广东省"）

## API 缓存机制

- **缓存 TTL**：10 分钟
- **存储位置**：浏览器 LocalStorage
- **缓存 Key**：
  - `mojiLite.dataset.rain` / `mojiLite.dataset.temp` - 数据集缓存
  - `mojiLite.raw.rain` / `mojiLite.raw.temp` - 原始 API 响应缓存

## 性能指标

| 指标 | 目标 |
|------|------|
| 页面加载时间 | <3秒 |
| 地图渲染响应 | <500ms |
| API 超时 | 12秒 |

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 部署说明

### 前端静态部署

将 `web/` 目录部署到任意静态服务器即可：

```bash
# Nginx
location / {
    root /path/to/weather-map/web;
    index index.html;
}

# Apache
DocumentRoot "/path/to/weather-map/web"
```

### GitHub Pages 自动部署

项目已配置 GitHub Actions 工作流 (`.github/workflows/deploy.yml`)，推送代码后自动部署到 GitHub Pages。

### 注意事项

1. **跨域问题**：Open-Meteo API 支持 CORS，可直接从前端调用
2. **HTTPS**：生产环境建议使用 HTTPS 以获得更好的浏览器体验
3. **Service Worker**：如需离线支持，可自行添加 PWA 能力
4. **爬虫频率**：使用网页爬取功能时，请合理控制请求频率，避免对目标网站造成压力

## 开源许可

MIT License

## 更新日志

### v1.1.0 (2026-06-08)
- 新增15天动态天气预报功能
- 集成中国天气网网页爬虫适配器
- 新增动态时间轴交互控制
- 支持降水量与气温双模式动态展示
- 新增 forecast.html 预报可视化页面

### v1.0.0 (2026-06-06)
- 初始版本发布
- 支持降水/气温双模式切换
- 集成 Open-Meteo 实时气象 API
- 34个省级行政区 GeoJSON 底图
- 响应式设计与 Tooltip 交互
