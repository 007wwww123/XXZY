"""
adapters/base.py - 天气数据提供者基类

功能说明：
- 定义 WeatherProvider 抽象基类
- 规范数据源适配器的接口
- 统一返回数据格式
"""

from abc import ABC, abstractmethod
import pandas as pd


class WeatherProvider(ABC):
    """天气数据提供者基类"""

    @abstractmethod
    def fetch_data(self, **kwargs) -> pd.DataFrame:
        """
        获取天气数据

        Returns:
            pd.DataFrame: 统一格式的天气数据
        """
        pass

