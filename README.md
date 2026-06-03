# weather-map

一个适合新手的“省级天气数据管道 + 交互式分层设色图（HTML）导出”项目：以**省会城市作为该省代表点**抓取天气数据（温度/降水等），统一清洗为 **Parquet**，并生成可离线打开的**省级分层设色地图**。

项目支持两种数据接入方式：
- **API 接入（推荐）**：通过公开天气 API 获取数据（如 Open-Meteo）。
- **网页爬取（学习用途）**：抓取并解析天气网页，将结果归一到同一套数据结构（便于对比与扩展）。

## 项目结构

- `data/geo/`：地图边界与省名对齐相关文件  
  - `china_province.geojson`：中国省级边界 GeoJSON  
  - `name_map.json`：省名映射表（GeoJSON 省名 ↔ 项目内部省名）
- `data/lookup/`：静态查表数据（全项目“唯一真源”）  
  - `provinces.csv`：省级单位 + 省会 + 经纬度
- `data/cache/`：抓取缓存（API JSON / 网页 HTML），减少重复请求
- `data/parquet/raw/`：归一化后的原始天气记录（统一 schema，API/网页共用）
- `data/parquet/processed/`：聚合后的省级数据（用于地图展示）
- `outputs/html/`：生成的交互式地图 HTML（离线打开即可）
- `src/weather_map/`：项目代码（CLI + adapters + services + viz）
- `tests/`：单元测试（建议至少保留聚合逻辑测试）

## 数据流程（核心步骤）

1. **抓取（Fetch）**：按 `provinces.csv` 中的省会经纬度抓取天气数据（API 或网页）。
2. **归一化（Normalize）**：将不同来源的数据整理成统一结构，写入 `data/parquet/raw/`。
3. **清洗与聚合（Transform & Aggregate）**：计算省级展示值  
   - 示例：当日最高温 / 当日降水总量 / 某时刻温度等
4. **省名对齐（Map Join）**：用 `name_map.json` 将省名统一到 GeoJSON 的命名体系，避免地图无法匹配。
5. **可视化导出（Render）**：生成交互式分层设色地图，输出到 `outputs/html/`。

## 运行环境与依赖

- 建议 Python 3.10+
- 依赖见 `requirements.txt`（通常包含：`requests`、`pandas`、`pyarrow`、`pyecharts` 等）

## 快速开始

```bash
pip install -r requirements.txt
python -m weather_map.cli --source api --metric temperature --date 2026-06-03
```

该命令通常会：
- 拉取天气数据（API 模式），
- 在 `data/parquet/` 下生成 raw/processed 的 Parquet 文件，
- 并在 `outputs/html/` 生成交互式地图 HTML。

## 常用命令参数（建议）

- `--source`：数据来源，`api` 或 `web`
- `--metric`：指标类型，`temperature`（温度）或 `precipitation`（降水）
- `--date`：日期，格式 `YYYY-MM-DD`（例如 `2026-06-03`）

示例（网页爬取 + 降水）：

```bash
python -m weather_map.cli --source web --metric precipitation --date 2026-06-03
```

## 说明与限制

- 省级数据使用**省会代表点**近似全省情况，属于简化建模；若需要更准确，可改为“多个城市取均值/加权”。
- 网页爬取模式用于学习演示，网页结构可能变动，需要维护解析规则；抓取时请控制频率并遵守网站条款。
- 若地图出现某些省为空白，优先检查：`name_map.json` 是否覆盖了所有省名差异。

## 后续可扩展方向（可选）

- 增加更多指标：风速、湿度、体感温度、空气质量等
- 增加缓存策略：TTL、增量更新、失败重试
- 增加更多地图层级：市级/区县级（在省级稳定后再做）
- 输出更多图表：时间序列折线、极值统计、对比排行等