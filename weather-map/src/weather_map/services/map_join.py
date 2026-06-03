"""
services/map_join.py - 数据和地图关联服务

功能说明：
- 对齐省名和地理坐标
- 匹配天气数据与 GeoJSON 边界
- 处理名称混淆和别名
"""

import pandas as pd


def align_province_names(df: pd.DataFrame, name_map_path: str) -> pd.DataFrame:
    """
    对齐省名和地理信息

    Args:
        df: 省级聚合数据
        name_map_path: 省名映射文件路径

    Returns:
        pd.DataFrame: 对齐后的数据
    """
    pass


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

