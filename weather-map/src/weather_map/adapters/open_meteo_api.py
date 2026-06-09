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
import time
import json
from typing import Any
from ..utils.logging import get_logger

logger = get_logger(__name__)


class OpenMeteoAdapter(WeatherProvider):
    """Open-Meteo API 适配器"""

    API_URL = "https://api.open-meteo.com/v1/forecast"
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1.0

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

        Raises:
            Exception: 当所有重试都失败后抛出异常
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

        data = self._send_request_with_retry(params, timeout)

        current = data.get("current", {})
        time_val = current.get("time")
        apparent_temperature = current.get("apparent_temperature")
        weathercode = current.get("weathercode")
        precipitation = current.get("precipitation")

        row = {
            "time": time_val,
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

    def _send_request_with_retry(self, params: dict, timeout: int) -> dict:
        """发送请求并带有重试机制

        Args:
            params: 请求参数
            timeout: 超时时间（秒）

        Returns:
            dict: 响应数据

        Raises:
            Exception: 当所有重试都失败后抛出异常
        """
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return self._send_single_request(params, timeout, attempt)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
                last_exception = e
                if self._is_retryable_exception(e):
                    if attempt < self.MAX_RETRIES - 1:
                        backoff_time = self.INITIAL_BACKOFF * (2 ** attempt)
                        logger.warning(
                            f"请求失败（尝试 {attempt + 1}/{self.MAX_RETRIES}），"
                            f"等待 {backoff_time:.2f} 秒后重试。"
                            f"错误类型: {type(e).__name__}, 详情: {str(e)}"
                        )
                        time.sleep(backoff_time)
                        continue
                    else:
                        logger.error(
                            f"请求失败，已达到最大重试次数 {self.MAX_RETRIES}。"
                            f"错误类型: {type(e).__name__}, 详情: {str(e)}"
                        )
                else:
                    logger.error(
                        f"请求失败，不可重试的异常。"
                        f"错误类型: {type(e).__name__}, 详情: {str(e)}"
                    )
                    break
            except json.JSONDecodeError as e:
                last_exception = e
                logger.error(
                    f"请求失败，响应数据解析错误。"
                    f"错误类型: {type(e).__name__}, 详情: {str(e)}"
                )
                break
            except Exception as e:
                last_exception = e
                logger.error(
                    f"请求失败，发生未知异常。"
                    f"错误类型: {type(e).__name__}, 详情: {str(e)}"
                )
                break

        user_message = self._get_user_friendly_message(last_exception)
        raise Exception(user_message) from last_exception

    def _send_single_request(self, params: dict, timeout: int, attempt: int) -> dict:
        """发送单个请求

        Args:
            params: 请求参数
            timeout: 超时时间（秒）
            attempt: 当前尝试次数

        Returns:
            dict: 响应数据

        Raises:
            requests.exceptions.RequestException: 请求异常
            json.JSONDecodeError: JSON 解析异常
        """
        logger.info(f"发送请求（尝试 {attempt + 1}/{self.MAX_RETRIES}）: {self.API_URL}")

        resp = requests.get(self.API_URL, params=params, timeout=timeout)

        if not (200 <= resp.status_code < 300):
            response_text = getattr(resp, 'text', '')
            logger.error(
                f"HTTP 请求失败，状态码: {resp.status_code}。"
                f"响应内容: {response_text[:500] if response_text else '无内容'}"
            )
            resp.raise_for_status()

        logger.debug(f"HTTP 请求成功，状态码: {resp.status_code}")

        try:
            data = resp.json()
            logger.debug("响应 JSON 解析成功")
            return data
        except json.JSONDecodeError as e:
            response_text = getattr(resp, 'text', '')
            logger.error(
                f"响应数据解析失败。"
                f"错误类型: {type(e).__name__}，"
                f"响应内容: {response_text[:500] if response_text else '无内容'}"
            )
            raise

    @staticmethod
    def _is_retryable_exception(exception: Exception) -> bool:
        """判断异常是否可重试

        Args:
            exception: 异常对象

        Returns:
            bool: 是否可重试
        """
        if isinstance(exception, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            return True
        if isinstance(exception, requests.exceptions.HTTPError):
            if hasattr(exception, "response") and exception.response is not None:
                return 500 <= exception.response.status_code < 600
        return False

    @staticmethod
    def _get_user_friendly_message(exception: Exception) -> str:
        """获取用户友好的提示信息

        Args:
            exception: 异常对象

        Returns:
            str: 用户友好的提示信息
        """
        if isinstance(exception, requests.exceptions.ConnectionError):
            return "网络连接失败，请检查您的网络连接后重试。"
        elif isinstance(exception, requests.exceptions.Timeout):
            return "请求超时，服务器响应较慢，请稍后重试。"
        elif isinstance(exception, requests.exceptions.HTTPError):
            if hasattr(exception, "response") and exception.response is not None:
                status_code = exception.response.status_code
                if 400 <= status_code < 500:
                    return f"请求参数错误（错误码：{status_code}），请检查输入信息。"
                elif 500 <= status_code < 600:
                    return f"服务器暂时不可用（错误码：{status_code}），请稍后重试。"
            return "HTTP 请求失败，请稍后重试。"
        elif isinstance(exception, json.JSONDecodeError):
            return "数据解析失败，服务器返回了无效的数据格式，请稍后重试。"
        else:
            return "获取天气数据失败，请稍后重试。"

