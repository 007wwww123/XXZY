"""
config.py - 配置管理

功能说明：
- 路径配置 (数据、输出等目录)
- 默认参数设置
- 数据源 URL 配置
- 常量定义
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
GEO_DIR = DATA_DIR / "geo"
LOOKUP_DIR = DATA_DIR / "lookup"
CACHE_DIR = DATA_DIR / "cache"
GEO_CACHE_DIR = CACHE_DIR / "geo"
PARQUET_DIR = DATA_DIR / "parquet"
RAW_PARQUET_DIR = PARQUET_DIR / "raw"
PROCESSED_PARQUET_DIR = PARQUET_DIR / "processed"

# 输出目录
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
HTML_OUTPUT_DIR = OUTPUTS_DIR / "html"

# 数据文件
PROVINCE_GEOJSON = GEO_DIR / "china_province.geojson"
NAME_MAP_JSON = GEO_DIR / "name_map.json"
PROVINCES_CSV = LOOKUP_DIR / "provinces.csv"

# 默认参数
DEFAULT_SOURCE = "api"  # api 或 web
DEFAULT_METRIC = "temperature"
DEFAULT_DATE = None  # 默认今天

