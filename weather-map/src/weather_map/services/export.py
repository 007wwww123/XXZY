"""
services/export.py - 数据导出服务

功能说明：
- 将处理后的数据导出为 Parquet 格式
- 支持原始数据和处理后数据的不同输出
- 管理数据版本
"""

import pandas as pd


def export_raw_parquet(df: pd.DataFrame, partition_key: str = None) -> str:
    """
    导出原始结构化数据为 Parquet

    Args:
        df: 原始数据
        partition_key: 分区键（例如日期）

    Returns:
        str: 输出文件路径
    """
    pass


def export_processed_parquet(df: pd.DataFrame, partition_key: str = None) -> str:
    """
    导出处理后的省级数据为 Parquet（用于绘图）

    Args:
        df: 处理后的数据
        partition_key: 分区键（例如日期）

    Returns:
        str: 输出文件路径
    """
    pass

