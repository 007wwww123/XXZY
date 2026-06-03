"""
adapters/open_meteo_api.py - Open-Meteo API 数据适配器

功能说明：
- 通过 Open-Meteo 公开 API 获取气象数据
- 实现 WeatherProvider 接口
- 处理 API 请求和响应解析
"""

from .base import WeatherProvider
import pandas as pd
import requests
from typing import Any


class OpenMeteoAdapter(WeatherProvider):
    """Open-Meteo API 适配器"""

    API_URL = "https://api.open-meteo.com/v1/forecast"

    def fetch_data(self, latitude: float, longitude: float, province_name: str = "", province_code: str = "", region: str = "", capital_city: str = "", forecast_days: int = 3, timeout: int = 10, **kwargs: Any) -> pd.DataFrame:
        """从 Open-Meteo API 获取单地点天气数据并返回统一的 DataFrame。

        返回的 DataFrame 至少包含：time, apparent_temperature, weathercode, precipitation

        Args:
            latitude: 纬度
            longitude: 经度
            province_name: 省名（可选，用于打标）
            province_code: 省代码（可选）
            region: 区域（可选）
            capital_city: 省会（可选）
            forecast_days: 预报天数
            timeout: 请求超时时间（秒）
            **kwargs: 透传给 API 的其它参数

        Returns:
            pd.DataFrame: 单条位置天气数据
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,weathercode,precipitation",
            "hourly": "temperature_2m,precipitation_probability",
            "forecast_days": forecast_days,
            "timezone": "auto",
        }
        params.update(kwargs)

        resp = requests.get(self.API_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        time = current.get("time")
        apparent_temperature = current.get("apparent_temperature")
        weathercode = current.get("weathercode")
        precipitation = current.get("precipitation")

        row = {
            "time": time,
            "apparent_temperature": apparent_temperature,
            "weathercode": weathercode,
            "precipitation": precipitation,
        }

        # 保留传入的元数据（若需要在批量中补回）
        if province_name:
            row["province_name"] = province_name
        if province_code:
            row["province_code"] = province_code
        if region:
            row["region"] = region
        if capital_city:
            row["capital_city"] = capital_city
        row["latitude"] = latitude
        row["longitude"] = longitude

        return pd.DataFrame([row])

