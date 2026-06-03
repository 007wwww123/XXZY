"""
services/map_join.py - 数据和地图关联服务

功能说明：
- 对齐省名和地理坐标
- 匹配天气数据与 GeoJSON 边界
- 处理名称混淆和别名
"""

import json
from pathlib import Path

import pandas as pd


def _normalize_name(value):
    if pd.isna(value):
        return value
    return str(value).strip()


def _find_name_column(df: pd.DataFrame) -> str:
    for column in ("province_name", "province", "name"):
        if column in df.columns:
            return column
    raise KeyError("DataFrame must contain one of: province_name, province, name")


def _load_inverse_name_map(name_map_path: str) -> dict:
    raw_map = json.loads(Path(name_map_path).read_text(encoding="utf-8"))
    inverse_map = {}
    for geo_name, internal_name in raw_map.items():
        if isinstance(geo_name, str) and isinstance(internal_name, str):
            inverse_map.setdefault(internal_name.strip(), geo_name.strip())
    return inverse_map


def align_province_names(df: pd.DataFrame, name_map_path: str) -> pd.DataFrame:
    """
    对齐省名和地理信息

    Args:
        df: 省级聚合数据
        name_map_path: 省名映射文件路径

    Returns:
        pd.DataFrame: 对齐后的数据
    """
    result = df.copy()
    source_col = _find_name_column(result)
    inverse_map = _load_inverse_name_map(name_map_path)

    normalized = result[source_col].map(_normalize_name)
    aligned = normalized.map(lambda x: inverse_map.get(x, x))

    result[f"{source_col}_raw"] = result[source_col]
    result[source_col] = aligned

    if source_col != "province_name":
        result["province_name"] = aligned

    return result


def join_with_geojson(df: pd.DataFrame, geojson_path: str) -> pd.DataFrame:
    """
    将数据与 GeoJSON 地理信息进行关联
    Args:
        df: 对齐后的数据
        geojson_path: GeoJSON 文件路径
    Returns:
        pd.DataFrame: 关联后的数据
    """
    pass

