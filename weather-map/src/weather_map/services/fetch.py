"""
services/fetch.py - 数据抓取服务

功能说明：
- 根据指定数据源获取原始天气数据
- 支持 API 和网页爬取两种方式
- 实现缓存机制
"""

import pandas as pd


def fetch_weather_data(source: str, **kwargs) -> pd.DataFrame:
    """
    获取天气数据

    Args:
        source: 数据源 ('api' 或 'web')
        **kwargs: 其他参数

    Returns:
        pd.DataFrame: 原始天气数据
    """
    pass

