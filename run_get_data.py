import requests

url = "https://riot:16D0MFk6PeUsTi2K4sKe5w@127.0.0.1:12313/lol-match-history/v1/products/lol/92fab665-7821-5196-a97b-d539e5e8f260/matches?begIndex=0&endIndex=50"

# 发送 GET 请求
response = requests.get(url,verify=False)

# 检查响应状态码是否为 200 (OK)
if response.status_code == 200:
    # 获取 JSON 数据
    data = response.json()
    print(data)
else:
    print("请求失败，状态码：", response.status_code)