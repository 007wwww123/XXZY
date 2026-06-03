"""
services/transform.py - 数据转换和清洗服务

功能说明：
- 清洗和标准化原始数据
- 处理缺失值
- 数据类型转换
- 异常值处理
"""

import pandas as pd


def transform_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    转换和清洗天气数据

    Args:
        df: 原始天气数据

    Returns:
        pd.DataFrame: 清洗后的数据
    """
    pass


def aggregate_to_province(df: pd.DataFrame) -> pd.DataFrame:
    """
    按省级进行数据聚合

    Args:
        df: 清洗后的数据

    Returns:
        pd.DataFrame: 省级聚合结果
    """
    pass

