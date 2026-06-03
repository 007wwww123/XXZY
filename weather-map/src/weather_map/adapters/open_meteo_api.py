"""
adapters/open_meteo_api.py - Open-Meteo API 数据适配器

功能说明：
- 通过 Open-Meteo 公开 API 获取气象数据
- 实现 WeatherProvider 接口
- 处理 API 请求和响应解析
"""

from .base import WeatherProvider
import pandas as pd


class OpenMeteoAdapter(WeatherProvider):
    """Open-Meteo API 适配器"""

    def fetch_data(self, **kwargs) -> pd.DataFrame:
        """
        从 Open-Meteo API 获取天气数据

        Returns:
            pd.DataFrame: 统一格式的天气数据
        """
        pass

