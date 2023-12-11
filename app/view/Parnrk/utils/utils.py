import os
import json
import requests
from requests.exceptions import RequestException
import time
from datetime import datetime, timedelta
import pytz

def get_api(field: str) -> dict:
    """
    获取 API。

    Args:
        field (str): API 所属分类，即 data/api 下的文件名（不含后缀名）

    Returns:
        dict, 该 API 的内容。
    """
    path = os.path.abspath(
        os.path.join(
            os.path.join(os.path.dirname(__file__), "..", "api", f"{field.lower()}.json")
        )
    )
    if os.path.exists(path):
        with open(path, encoding="utf8") as f:
            return json.loads(f.read())
    else:
        return {}

def get_versions(max_retries=5, retry_delay=0):
    """
    获取英雄联盟当前版本，用于请求头像资源。
    如果请求失败，将重试最大次数 max_retries，每次间隔 retry_delay 秒。
    """
    for attempt in range(max_retries):
        try:
            response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
            response.raise_for_status()  # 如果状态码不是200，将引发异常
            versions = response.json()
            return versions[0]  # 返回最新版本
        except RequestException:
            print(f"请求失败，正在尝试第 {attempt + 1} 次重试...")
            time.sleep(retry_delay)
    print("所有重试均失败。")
    return None

#把时间码编程
def convert_time_to_string(gameCreationDate):
    utc_time = datetime.strptime(gameCreationDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    china_timezone = pytz.timezone("Asia/Shanghai")
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(china_timezone)
    current_time = datetime.now(china_timezone)
    time_difference = current_time - local_time

    if time_difference.total_seconds() < 60:
        result = "刚刚"
    elif time_difference.total_seconds() < 3600:
        minutes = int(time_difference.total_seconds() // 60)
        result = f"{minutes}分钟前"
    elif time_difference.total_seconds() < 86400:
        hours = int(time_difference.total_seconds() // 3600)
        result = f"{hours}小时前"
    else:
        days = int(time_difference.total_seconds() // 86400)
        result = f"{days}天前"

    return result
































