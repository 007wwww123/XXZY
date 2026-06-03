"""
adapters/weather_web.py - 天气网页爬取适配器

功能说明：
- 通过网页爬取方式获取气象数据
- 实现 WeatherProvider 接口
- 处理 HTML 解析和数据提取
"""

from .base import WeatherProvider
import pandas as pd


class WeatherWebAdapter(WeatherProvider):
    """天气网页爬取适配器"""

    def fetch_data(self, **kwargs) -> pd.DataFrame:
        """
        通过网页爬取获取天气数据

        Returns:
            pd.DataFrame: 统一格式的天气数据
        """
        pass

