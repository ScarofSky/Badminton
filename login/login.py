import os

import requests
import json
from smsService import send_sms_code

# ==== 发送验证码 ====
status = send_sms_code()
if status != 200:
    print(f"❌ 短信发送失败，状态码: {status}，终止执行。")
    exit(1)
else:
    print("📩 短信验证码已发送，请查看手机。")

# ==== 用户输入验证码 ====
sms_code = input("请输入验证码 (smsCode): ").strip()

# ==== 登录请求 URL ====
url = "https://ds-api.dong24.com/bais-client-v1/app/h5/login"

# ==== 登录请求体 Payload ====
payload = {
    "appId": "14285138416960",
    "shopId": "3641246707790003",
    "loginType": 0,
    "mobile": "13121247856",
    "smsCode": sms_code
}

# ==== 请求头 ====
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Origin": "https://venue.dongsport.com",
    "Referer": "https://venue.dongsport.com/",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "*/*"
}

# ==== 发送登录请求 ====
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
    print("状态码:", response.status_code)

    if response.status_code == 200:
        result = response.json()
        token = result.get("token")
        member_id = result.get("memberId")

        if token:
            print("✅ 登录成功")
            print("Token:", token)
            print("Member ID:", member_id)

            # === 写入本地文件 ===
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            auth_path = os.path.join(project_root, "auth.dat")

            with open(auth_path, "w", encoding="utf-8") as f:
                f.write(token)

            print(f"💾 token 已写入文件: {auth_path}")

        else:
            print("⚠️ 登录失败，未返回 token。返回内容:", result)
    else:
        print("❌ 登录失败，服务器返回:", response.text)

except requests.exceptions.RequestException as e:
    print("请求异常:", e)
