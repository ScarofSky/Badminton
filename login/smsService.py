import requests
import json


def send_sms_code():
    url = "https://ds-api.dong24.com/bais-client-v1/app/sendSms"

    payload = {
        "shopId": "3641246707790003",
        "mobile": "13121247856"
    }

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Origin": "https://venue.dongsport.com",
        "Referer": "https://venue.dongsport.com/",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection": "keep-alive"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code
    except requests.RequestException as e:
        print("请求失败:", e)
        return -1  # 可自定义错误状态码

if __name__ == "__main__":
    pass