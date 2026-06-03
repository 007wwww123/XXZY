"""
services/map_join.py - 数据和地图关联服务

功能说明：
- 对齐省名和地理坐标
- 匹配天气数据与 GeoJSON 边界
- 处理名称混淆和别名
"""

import json
from pathlib import Path
import sys

import pandas as pd

try:
    from ..config import NAME_MAP_JSON, PROVINCE_GEOJSON
    from ..utils.geo_cache import load_cached_geojson, load_cached_name_map
except ImportError:  # Support tests that import this module directly by file path.
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from weather_map.config import NAME_MAP_JSON, PROVINCE_GEOJSON
    from weather_map.utils.geo_cache import load_cached_geojson, load_cached_name_map


def _normalize_name(value):
    if pd.isna(value):
        return value
    return str(value).strip()


def _find_name_column(df: pd.DataFrame) -> str:
    for column in ("province_name", "province", "name"):
        if column in df.columns:
            return column
    raise KeyError("DataFrame must contain one of: province_name, province, name")


def _read_json_from_cache_or_path(path: str | Path) -> dict:
    source_path = Path(path)
    resolved_path = source_path.resolve()
    if source_path.name == "name_map.json" and resolved_path == NAME_MAP_JSON.resolve():
        return load_cached_name_map()
    if source_path.name == "china_province.geojson" and resolved_path == PROVINCE_GEOJSON.resolve():
        return load_cached_geojson()
    return json.loads(source_path.read_text(encoding="utf-8"))


def _load_inverse_name_map(name_map_path: str) -> dict:
    raw_map = _read_json_from_cache_or_path(name_map_path)
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
    result = df.copy()
    source_col = _find_name_column(result)
    geojson = _read_json_from_cache_or_path(geojson_path)

    rows = []
    for feature in geojson.get("features", []):
        properties = feature.get("properties", {}) or {}
        geometry = feature.get("geometry")

        for key in ("name", "fullname"):
            geo_name = properties.get(key)
            if not geo_name:
                continue

            rows.append(
                {
                    "_geo_join_name": _normalize_name(geo_name),
                    "geo_name": properties.get("name"),
                    "geo_fullname": properties.get("fullname"),
                    "geo_code": properties.get("code"),
                    "geo_center": properties.get("center"),
                    "geometry": geometry,
                }
            )

    geo_df = pd.DataFrame(rows).drop_duplicates("_geo_join_name")
    result["_geo_join_name"] = result[source_col].map(_normalize_name)
    joined = result.merge(geo_df, on="_geo_join_name", how="left")
    return joined.drop(columns=["_geo_join_name"])

