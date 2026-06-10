"""
adapters/weather_web.py - 天气网页爬取适配器

功能说明：
- 通过网页爬取方式获取气象数据
- 实现 WeatherProvider 接口
- 处理 HTML 解析和数据提取
- 获取全国35个省级行政区省会城市数据
"""

from .base import WeatherProvider
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime


class WeatherWebAdapter(WeatherProvider):
    """天气网页爬取适配器 - 获取全国省会城市天气数据"""

    def __init__(self):
        self.base_url = "https://www.weather.com.cn"
        self.radar_url = "https://www.weather.com.cn/radar/"
        
        # 省级行政区数据：包含URL、纬度、经度、省份代码、所属区域
        # 数据来源：截图中的CSV内容
        self.province_data = {
            '北京': {'url': 'https://www.weather.com.cn/weather/101010100.shtml', 'lat': 39.9042, 'lon': 116.4074, 'province_code': '110000', 'region': '华北', 'province_name': '北京市'},
            '天津': {'url': 'https://www.weather.com.cn/weather/101030100.shtml', 'lat': 39.0842, 'lon': 117.2000, 'province_code': '120000', 'region': '华北', 'province_name': '天津市'},
            '石家庄': {'url': 'https://www.weather.com.cn/weather/101090101.shtml', 'lat': 38.0428, 'lon': 114.5149, 'province_code': '130000', 'region': '华北', 'province_name': '河北省'},
            '太原': {'url': 'https://www.weather.com.cn/weather/101100101.shtml', 'lat': 37.8706, 'lon': 112.5489, 'province_code': '140000', 'region': '华北', 'province_name': '山西省'},
            '呼和浩特': {'url': 'https://www.weather.com.cn/weather/101080101.shtml', 'lat': 40.8426, 'lon': 111.7492, 'province_code': '150000', 'region': '华北', 'province_name': '内蒙古自治区'},
            '沈阳': {'url': 'https://www.weather.com.cn/weather/101070101.shtml', 'lat': 41.8057, 'lon': 123.4315, 'province_code': '210000', 'region': '东北', 'province_name': '辽宁省'},
            '长春': {'url': 'https://www.weather.com.cn/weather/101060101.shtml', 'lat': 43.8171, 'lon': 125.3235, 'province_code': '220000', 'region': '东北', 'province_name': '吉林省'},
            '哈尔滨': {'url': 'https://www.weather.com.cn/weather/101050101.shtml', 'lat': 45.8038, 'lon': 126.5349, 'province_code': '230000', 'region': '东北', 'province_name': '黑龙江省'},
            '上海': {'url': 'https://www.weather.com.cn/weather/101020100.shtml', 'lat': 31.2304, 'lon': 121.4737, 'province_code': '310000', 'region': '华东', 'province_name': '上海市'},
            '南京': {'url': 'https://www.weather.com.cn/weather/101190101.shtml', 'lat': 32.0603, 'lon': 118.7969, 'province_code': '320000', 'region': '华东', 'province_name': '江苏省'},
            '杭州': {'url': 'https://www.weather.com.cn/weather/101210101.shtml', 'lat': 30.2741, 'lon': 120.1551, 'province_code': '330000', 'region': '华东', 'province_name': '浙江省'},
            '合肥': {'url': 'https://www.weather.com.cn/weather/101220101.shtml', 'lat': 31.8206, 'lon': 117.2272, 'province_code': '340000', 'region': '华东', 'province_name': '安徽省'},
            '福州': {'url': 'https://www.weather.com.cn/weather/101230101.shtml', 'lat': 26.0745, 'lon': 119.2965, 'province_code': '350000', 'region': '华东', 'province_name': '福建省'},
            '南昌': {'url': 'https://www.weather.com.cn/weather/101240101.shtml', 'lat': 28.6820, 'lon': 115.8579, 'province_code': '360000', 'region': '华东', 'province_name': '江西省'},
            '济南': {'url': 'https://www.weather.com.cn/weather/101120101.shtml', 'lat': 36.6512, 'lon': 117.1201, 'province_code': '370000', 'region': '华东', 'province_name': '山东省'},
            '郑州': {'url': 'https://www.weather.com.cn/weather/101180101.shtml', 'lat': 34.7466, 'lon': 113.6254, 'province_code': '410000', 'region': '中南', 'province_name': '河南省'},
            '武汉': {'url': 'https://www.weather.com.cn/weather/101200101.shtml', 'lat': 30.5928, 'lon': 114.3055, 'province_code': '420000', 'region': '中南', 'province_name': '湖北省'},
            '长沙': {'url': 'https://www.weather.com.cn/weather/101250101.shtml', 'lat': 28.2282, 'lon': 112.9388, 'province_code': '430000', 'region': '中南', 'province_name': '湖南省'},
            '广州': {'url': 'https://www.weather.com.cn/weather/101280101.shtml', 'lat': 23.1291, 'lon': 113.2644, 'province_code': '440000', 'region': '中南', 'province_name': '广东省'},
            '南宁': {'url': 'https://www.weather.com.cn/weather/101300101.shtml', 'lat': 22.8170, 'lon': 108.3669, 'province_code': '450000', 'region': '中南', 'province_name': '广西壮族自治区'},
            '海口': {'url': 'https://www.weather.com.cn/weather/101310101.shtml', 'lat': 20.0440, 'lon': 110.1999, 'province_code': '460000', 'region': '中南', 'province_name': '海南省'},
            '重庆': {'url': 'https://www.weather.com.cn/weather/101040100.shtml', 'lat': 29.5630, 'lon': 106.5516, 'province_code': '500000', 'region': '西南', 'province_name': '重庆市'},
            '成都': {'url': 'https://www.weather.com.cn/weather/101270101.shtml', 'lat': 30.5728, 'lon': 104.0668, 'province_code': '510000', 'region': '西南', 'province_name': '四川省'},
            '贵阳': {'url': 'https://www.weather.com.cn/weather/101260101.shtml', 'lat': 26.6470, 'lon': 106.6302, 'province_code': '520000', 'region': '西南', 'province_name': '贵州省'},
            '昆明': {'url': 'https://www.weather.com.cn/weather/101290101.shtml', 'lat': 25.0389, 'lon': 102.7183, 'province_code': '530000', 'region': '西南', 'province_name': '云南省'},
            '拉萨': {'url': 'https://www.weather.com.cn/weather/101140101.shtml', 'lat': 29.6520, 'lon': 91.1721, 'province_code': '540000', 'region': '西南', 'province_name': '西藏自治区'},
            '西安': {'url': 'https://www.weather.com.cn/weather/101110101.shtml', 'lat': 34.3416, 'lon': 108.9398, 'province_code': '610000', 'region': '西北', 'province_name': '陕西省'},
            '兰州': {'url': 'https://www.weather.com.cn/weather/101160101.shtml', 'lat': 36.0611, 'lon': 103.8343, 'province_code': '620000', 'region': '西北', 'province_name': '甘肃省'},
            '西宁': {'url': 'https://www.weather.com.cn/weather/101150101.shtml', 'lat': 36.6171, 'lon': 101.7782, 'province_code': '630000', 'region': '西北', 'province_name': '青海省'},
            '银川': {'url': 'https://www.weather.com.cn/weather/101170101.shtml', 'lat': 38.4872, 'lon': 106.2309, 'province_code': '640000', 'region': '西北', 'province_name': '宁夏回族自治区'},
            '乌鲁木齐': {'url': 'https://www.weather.com.cn/weather/101130101.shtml', 'lat': 43.8256, 'lon': 87.6168, 'province_code': '650000', 'region': '西北', 'province_name': '新疆维吾尔自治区'},
            # 港澳台地区（使用独立数据源）
            '台北': {'url': 'https://www.weather.com.cn/weather/101340101.shtml', 'lat': 25.0330, 'lon': 121.5654, 'province_code': '710000', 'region': '港澳台', 'province_name': '台湾省'},
            '香港': {'url': 'http://www.weather.com.cn/weathern/101320101.shtml', 'lat': 22.3193, 'lon': 114.1694, 'province_code': '810000', 'region': '港澳台', 'province_name': '香港特别行政区'},
            '澳门': {'url': 'https://www.weather.com.cn/weather/101330101.shtml', 'lat': 22.1987, 'lon': 113.5439, 'province_code': '820000', 'region': '港澳台', 'province_name': '澳门特别行政区'},
        }
        
        # 保留旧接口兼容
        self.city_data = self.province_data
        self.city_urls = {city: info['url'] for city, info in self.province_data.items() if info['url']}

    def fetch_data(self, **kwargs) -> pd.DataFrame:
        """
        通过网页爬取获取全国省会城市天气数据

        Args:
            **kwargs: 可选参数，如 date, province_name, region 等

        Returns:
            pd.DataFrame: 统一格式的天气数据
        """
        all_data = []
        date = kwargs.get('date', datetime.now().strftime('%Y-%m-%d'))
        province_name = kwargs.get('province_name')
        region = kwargs.get('region')
        limit = kwargs.get('limit', len(self.city_urls))
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.weather.com.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        cities_to_fetch = list(self.city_urls.items())[:limit]
        
        for idx, (city_name, url) in enumerate(cities_to_fetch):
            try:
                info = self.province_data[city_name]
                print(f"[{idx+1}/{len(cities_to_fetch)}] 正在获取 {info['province_name']} - {city_name} 的天气数据...")
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                response.encoding = 'utf-8'
                html_content = response.text
                soup = BeautifulSoup(html_content, 'lxml')
                
                city_data = self._parse_city_weather(soup, html_content, city_name, info, date)
                if city_data:
                    all_data.append(city_data)
                    print(f"    [OK] 成功")
                else:
                    print(f"    [FAIL] 未获取到有效数据")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    [FAIL] 获取失败: {str(e)[:30]}")
                continue
        
        if all_data:
            df = pd.DataFrame(all_data)
            if province_name:
                df = df[df['province_name'] == province_name]
            if region:
                df = df[df['region'] == region]
            return df
        return pd.DataFrame()

    def _parse_city_weather(self, soup, html_content, city_name, info, date):
        """解析城市天气页面"""
        data = {
            'province_name': info.get('province_name', city_name),
            'province_code': info.get('province_code'),
            'region': info.get('region'),
            'city_name': city_name,
            'date': date,
            'temperature_max': None,
            'temperature_min': None,
            'precipitation_sum': 0.0,
            'latitude': info.get('lat'),
            'longitude': info.get('lon'),
            'source': 'web',
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        temp_info = self._extract_temperature_new(soup, html_content)
        if temp_info:
            data['temperature_max'], data['temperature_min'] = temp_info
        
        precip = self._extract_precipitation_new(html_content)
        if precip is not None:
            data['precipitation_sum'] = precip
        
        if data['temperature_max'] is None and data['temperature_min'] is None:
            return None
        
        return data

    def _extract_temperature_new(self, soup, html_content):
        """气温提取方法"""
        temp_pattern = re.compile(r'(\d+)\s*℃\s*[-~至]\s*(\d+)\s*℃')
        match = temp_pattern.search(html_content)
        if match:
            try:
                return int(match.group(1)), int(match.group(2))
            except:
                pass
        
        temp_pattern2 = re.compile(r'最高\s*[气]?温\s*[:：]\s*(\d+)\s*℃')
        temp_pattern3 = re.compile(r'最低\s*[气]?温\s*[:：]\s*(\d+)\s*℃')
        max_temp = None
        min_temp = None
        
        match_max = temp_pattern2.search(html_content)
        if match_max:
            max_temp = int(match_max.group(1))
        
        match_min = temp_pattern3.search(html_content)
        if match_min:
            min_temp = int(match_min.group(1))
        
        if max_temp is not None or min_temp is not None:
            return max_temp, min_temp
        
        for tag in soup.find_all(['span', 'div', 'p']):
            text = tag.get_text()
            if '℃' in text and len(text) < 30:
                temp_matches = re.findall(r'-?\d+', text)
                if len(temp_matches) >= 2:
                    try:
                        return int(temp_matches[0]), int(temp_matches[1])
                    except:
                        pass
        
        return None

    def _extract_precipitation_new(self, html_content):
        """降水量提取方法"""
        precip_pattern = re.compile(r'降水\s*[:：]\s*(\d+\.?\d*)\s*mm')
        match = precip_pattern.search(html_content)
        if match:
            return float(match.group(1))
        
        precip_pattern2 = re.compile(r'降雨量?\s*[:：]\s*(\d+\.?\d*)\s*mm')
        match2 = precip_pattern2.search(html_content)
        if match2:
            return float(match.group(1))
        
        if '无降水' in html_content or '无雨' in html_content:
            return 0.0
        
        mm_pattern = re.compile(r'(\d+\.?\d*)\s*mm')
        mm_matches = mm_pattern.findall(html_content)
        if mm_matches:
            for val in mm_matches:
                fval = float(val)
                if fval > 0:
                    return fval
        
        return 0.0

    def fetch_15day_forecast(self, **kwargs) -> pd.DataFrame:
        """
        获取15天天气预报（7天预报 + 8-15天预报）
        
        Returns:
            pd.DataFrame: 包含15天逐日天气预报数据
        """
        all_records = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.weather.com.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        cities_list = [(c, u, self.province_data[c]) for c, u in self.city_urls.items()]
        
        for idx, (city_name, url, info) in enumerate(cities_list):
            print(f"[{idx+1}/{len(cities_list)}] 正在获取 {info['province_name']} {city_name} 15天预报...")
            
            try:
                # === 1. 获取7天预报（第1-7天）===
                resp7 = requests.get(url, headers=headers, timeout=30)
                resp7.raise_for_status()
                resp7.encoding = 'utf-8'
                soup7 = BeautifulSoup(resp7.text, 'lxml')
                days_1_7 = self._parse_7day_all(soup7, resp7.text, city_name, info)
                
                # === 2. 获取8-15天预报 ===
                # 港澳台地区特殊处理
                if city_name == '香港':
                    # 香港使用 weathern 页面，直接解析该页面获取15天数据
                    days_8_15 = self._parse_hk_15day(soup7, resp7.text, city_name, info)
                elif city_name in ['台北', '澳门']:
                    # 台北和澳门使用标准 weather15d 页面
                    url15 = url.replace('/weather/', '/weather15d/')
                    resp15 = requests.get(url15, headers=headers, timeout=30)
                    resp15.raise_for_status()
                    resp15.encoding = 'utf-8'
                    soup15 = BeautifulSoup(resp15.text, 'lxml')
                    days_8_15 = self._parse_15day_all(soup15, resp15.text, city_name, info)
                else:
                    # 其他省份使用标准 weather15d 页面
                    url15 = url.replace('/weather/', '/weather15d/')
                    resp15 = requests.get(url15, headers=headers, timeout=30)
                    resp15.raise_for_status()
                    resp15.encoding = 'utf-8'
                    soup15 = BeautifulSoup(resp15.text, 'lxml')
                    days_8_15 = self._parse_15day_all(soup15, resp15.text, city_name, info)
                
                combined = days_1_7 + days_8_15
                all_records.extend(combined)
                print(f"    [OK] {len(combined)} 天数据")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    [FAIL] {str(e)[:40]}")
                continue
        
        if all_records:
            df = pd.DataFrame(all_records)
            province_name = kwargs.get('province_name')
            region = kwargs.get('region')
            if province_name:
                df = df[df['province_name'] == province_name]
            if region:
                df = df[df['region'] == region]
            return df
        return pd.DataFrame()
    
    def _parse_7day_all(self, soup, html, city_name, info):
        """解析7天预报页面中的所有天数"""
        records = []
        
        # 查找7天天气列表: <ul class="t clearfix"> 里面的 <li>
        items = soup.select('ul.t.clearfix li, ul[class*="t"] li, .t7 li')
        if not items:
            items = soup.find_all('li', class_=lambda c: c and 'sky' in c)
        
        for li in items:
            try:
                h1 = li.find('h1')
                if not h1:
                    continue
                h1_text = h1.get_text(strip=True)
                date_match = re.search(r'(\d+)日', h1_text)
                if not date_match:
                    continue
                day_num = int(date_match.group(1))
                
                # 天气现象
                wea_el = li.find(class_='wea')
                weather = wea_el.get_text(strip=True) if wea_el else '未知'
                
                # 温度: 今天只有 <i>16℃</i> (只有最低温)
                # 其他天: <span>25℃</span>/<i>17℃</i>
                temp_el = li.find(class_='tem')
                temp_max, temp_min = None, None
                if temp_el:
                    spans = temp_el.find_all('span')
                    ies = temp_el.find_all('i')
                    if spans:
                        temp_max = int(re.search(r'(\d+)', spans[0].get_text()).group(1))
                    if ies:
                        temp_min = int(re.search(r'(\d+)', ies[0].get_text()).group(1))
                    # 今天的情况: 只有 <i>
                    if not spans and ies:
                        temp_min = int(re.search(r'(\d+)', ies[0].get_text()).group(1))
                        temp_max = temp_min + 10  # 估算
                
                if temp_max and temp_min:
                    day_date = self._build_date_str(day_num)
                    precip = self._estimate_precip(weather)
                    records.append(self._make_record(city_name, info, day_date, temp_max, temp_min, precip))
            except Exception as e:
                continue
        
        return records
    
    def _parse_15day_all(self, soup, html, city_name, info):
        """解析8-15天预报页面"""
        records = []
        
        items = soup.find_all('li')
        if not items:
            items = soup.find_all('li')
        
        for li in items:
            try:
                time_el = li.find(class_='time')
                if not time_el:
                    continue
                time_text = time_el.get_text(strip=True)
                date_match = re.search(r'（(\d+)日）', time_text)
                if not date_match:
                    continue
                day_num = int(date_match.group(1))
                
                wea_el = li.find(class_='wea')
                weather = wea_el.get_text(strip=True) if wea_el else '未知'
                
                tem_el = li.find(class_='tem')
                temp_max, temp_min = None, None
                if tem_el:
                    ems = tem_el.find_all('em')
                    text = tem_el.get_text()
                    temps = re.findall(r'(\d+)', text)
                    if ems:
                        temp_max = int(re.search(r'(\d+)', ems[0].get_text()).group(1))
                    if len(temps) >= 2:
                        if not temp_max:
                            temp_max = int(temps[0])
                        temp_min = int(temps[-1])
                    elif len(temps) == 1:
                        temp_max = int(temps[0])
                        temp_min = int(temps[0]) - 5
                
                if temp_max and temp_min:
                    day_date = self._build_date_str(day_num)
                    precip = self._estimate_precip(weather)
                    records.append(self._make_record(city_name, info, day_date, temp_max, temp_min, precip))
            except Exception as e:
                continue
        
        return records
    
    def _build_date_str(self, day_num):
        """根据日期数字构建日期字符串"""
        today = datetime.now()
        target = today.replace(day=day_num)
        if day_num < today.day:
            # 跨月处理
            if today.month == 12:
                target = target.replace(year=today.year + 1, month=1)
            else:
                target = target.replace(month=today.month + 1)
        return target.strftime('%Y-%m-%d')
    
    def _parse_hk_15day(self, soup, html, city_name, info):
        """解析香港15天预报页面（weathern页面）"""
        records = []
        
        # 香港的 weathern 页面包含完整的15天预报数据
        # 尝试从页面中提取第8-15天的数据
        
        # 查找天气列表
        items = soup.select('ul.t.clearfix li, ul[class*="t"] li, .t15 li')
        if not items:
            items = soup.find_all('li', class_=lambda c: c and 'sky' in c)
        
        for li in items:
            try:
                h1 = li.find('h1')
                if not h1:
                    continue
                h1_text = h1.get_text(strip=True)
                date_match = re.search(r'(\d+)日', h1_text)
                if not date_match:
                    continue
                day_num = int(date_match.group(1))
                
                # 只处理第8-15天
                if day_num < 8:
                    continue
                
                # 天气现象
                wea_el = li.find(class_='wea')
                weather = wea_el.get_text(strip=True) if wea_el else '未知'
                
                # 温度
                temp_el = li.find(class_='tem')
                temp_max, temp_min = None, None
                if temp_el:
                    spans = temp_el.find_all('span')
                    ies = temp_el.find_all('i')
                    if spans:
                        temp_max = int(re.search(r'(\d+)', spans[0].get_text()).group(1))
                    if ies:
                        temp_min = int(re.search(r'(\d+)', ies[0].get_text()).group(1))
                
                if temp_max and temp_min:
                    day_date = self._build_date_str(day_num)
                    precip = self._estimate_precip(weather)
                    records.append(self._make_record(city_name, info, day_date, temp_max, temp_min, precip))
                    
            except Exception as e:
                continue
        
        return records
    
    def _estimate_precip(self, weather):
        """根据天气现象估算降水量"""
        weather = str(weather)
        if '暴雨' in weather:
            return 50.0
        elif '大雨' in weather:
            return 25.0
        elif '中雨' in weather:
            return 12.5
        elif '小雨' in weather:
            return 3.0
        elif '阵雨' in weather:
            return 5.0
        elif '雷阵雨' in weather:
            return 8.0
        elif '雨' in weather:
            return 2.0
        elif '雪' in weather:
            return 5.0
        else:
            return 0.0
    
    def _make_record(self, city_name, info, day_date, temp_max, temp_min, precip):
        """创建记录"""
        return {
            'province_name': info.get('province_name', city_name),
            'province_code': info.get('province_code'),
            'region': info.get('region'),
            'city_name': city_name,
            'date': day_date,
            'temp_max': temp_max,
            'temp_min': temp_min,
            'precip': precip,
            'latitude': info.get('lat'),
            'longitude': info.get('lon'),
            'source': 'web',
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
