# 墨迹天气-全国降水/气温实时地图

基于 ECharts 与 Open-Meteo API 开发的轻量级气象可视化应用，支持全国省级行政区实时降水与气温数据的展示。

## 功能特性

- **实时气象数据**：集成 Open-Meteo API，获取全国省会城市当前气温、降水观测值
- **双模式切换**：一键切换降水/气温视图，自动更新地图填充色与色阶图例
- **交互工具**：支持缩放、平移，Tooltip 展示详细气象数据
- **数据缓存**：LocalStorage 缓存机制，减少重复 API 请求
- **自动刷新**：可配置自动刷新间隔（5分钟/10分钟/30分钟/1小时）
- **响应式设计**：适配桌面端与移动端

## 目录结构

```
weather-map/
├── web/                          # 前端资源目录
│   ├── index.html                # 应用入口页面
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
│   ├── geo/
│   │   ├── china_province.geojson    # 原始省级 GeoJSON
│   │   └── name_map.json             # 省份名称标准化映射
│   └── lookup/
│       └── provinces.csv              # 省份代码与名称对照表
└── src/                          # Python 后端源码（可选）
    └── weather_map/
        ├── adapters/            # API 适配器
        ├── services/            # 数据处理服务
        ├── utils/               # 工具函数
        └── viz/                 # 可视化模块

```

## 快速开始

### 方式一：纯前端运行（推荐，无需安装依赖）

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

### 方式二：使用 Python 后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端服务
cd src
python -m weather_map.cli serve

# 访问 http://localhost:5000
```

## 数据说明

### 气象数据

- **数据源**：Open-Meteo API (https://api.open-meteo.com/v1/forecast)
- **请求变量**：`temperature_2m`（2米气温）、`precipitation`（总降水量）、`rain`（降雨量）
- **时区**：Asia/Shanghai
- **数据精度**：以省会城市观测站数据代表所在省级行政区

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

### 注意事项

1. **跨域问题**：Open-Meteo API 支持 CORS，可直接从前端调用
2. **HTTPS**：生产环境建议使用 HTTPS 以获得更好的浏览器体验
3. **Service Worker**：如需离线支持，可自行添加 PWA 能力

## 开源许可

MIT License

## 更新日志

### v1.0.0 (2026-06-06)
- 初始版本发布
- 支持降水/气温双模式切换
- 集成 Open-Meteo 实时气象 API
- 34个省级行政区 GeoJSON 底图
- 响应式设计与 Tooltip 交互
