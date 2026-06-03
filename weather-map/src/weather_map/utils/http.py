"""
utils/http.py - HTTP 请求工具

功能说明：
- 重试机制
- 超时控制
- 默认 headers
"""

import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def create_session(retries: int = 3, backoff_factor: float = 0.5) -> requests.Session:
    """
    创建带重试机制的会话

    Args:
        retries: 重试次数
        backoff_factor: 重试间隔因子

    Returns:
        requests.Session: 配置好的会话
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> requests.Response:
    """
    发送 GET 请求

    Args:
        url: 请求 URL
        params: 查询参数
        headers: 请求头
        timeout: 超时时间（秒）
        retries: 重试次数

    Returns:
        requests.Response: 响应对象

    Raises:
        requests.RequestException: 请求失败时抛出
    """
    session = create_session(retries=retries)
    headers = {**DEFAULT_HEADERS, **(headers or {})}

    logger.debug(f"GET {url} with params={params}")

    response = session.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()

    logger.debug(f"Response status: {response.status_code}")
    return response


def http_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> requests.Response:
    """
    发送 POST 请求

    Args:
        url: 请求 URL
        data: 表单数据
        json: JSON 数据
        headers: 请求头
        timeout: 超时时间（秒）
        retries: 重试次数

    Returns:
        requests.Response: 响应对象

    Raises:
        requests.RequestException: 请求失败时抛出
    """
    session = create_session(retries=retries)
    headers = {**DEFAULT_HEADERS, **(headers or {})}

    logger.debug(f"POST {url}")

    response = session.post(url, data=data, json=json, headers=headers, timeout=timeout)
    response.raise_for_status()

    logger.debug(f"Response status: {response.status_code}")
    return response
