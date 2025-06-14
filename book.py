import requests
import json
import time
from datetime import datetime
import os
from check_available import load_court_id_map
from probe import probe_availability

if __name__ == "__main__":
    # ==== 从本地读取 Authorization Token ====
    auth_file = "auth.dat"
    if not os.path.exists(auth_file):
        print("❌ 找不到 auth.dat 文件，请先执行登录脚本获取 token。")
        exit(1)

    with open(auth_file, "r", encoding="utf-8") as f:
        token = f.read().strip()

    cim = load_court_id_map()

    # ==== 启动时间设置 ====
    start_time_str = "2025-06-14 23:58:00"
    book_date = "2025-06-21"

    stime = "19:00"
    etime = "20:00"

    start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")

    # ==== 请求目标 URL ====
    url = "https://ds-api.dong24.com/bais-client-v1/v2/app/orders/sites"

    # ==== 请求体 Payload ====
    payload = {
        "venueSiteItemNodes": [
            {"itemId": cim['大馆2'], "startTime": "22:00", "endTime": "23:00", "groupType": 0},
            {"itemId": cim['大馆3'], "startTime": "22:00", "endTime": "23:00", "groupType": 0},
            {"itemId": cim['大馆4'], "startTime": "22:00", "endTime": "23:00", "groupType": 0},
            {"itemId": cim['大馆5'], "startTime": "22:00", "endTime": "23:00", "groupType": 0},
        ],
        "date": book_date,
        "venueId": "",
        "siteId": 14285185605313,
        "memberId": "3813998211344161",
        "linkMan": "智浩",
        "linkPhone": "13121247856",
        "appId": "14285138416960",
        "shopId": "3641246707790003",
        "lineType": 1,
        "orderSource": 3,
        "couponLogId": ""
    }

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
        "Authorization": token
    }

    # ==== 等待到指定时间 ====
    print(f"⏳ 等待至 {start_time_str} 开始探测...")
    while datetime.now() < start_time:
        time.sleep(0.01)

    # warm up
    session = requests.Session()
    probe_availability(book_date, 2, 5, "22:00 - 23:00", session)

    print("🔍 开始探测可预约状态...")
    while True:
        found = probe_availability(book_date, 2, 5, "22:00 - 23:00", session)
        if found:
            print("🚀 开始发送 POST 请求，连续发送 20 次")
            for i in range(1, 21):
                try:
                    send_time = time.time()
                    response = session.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                    elapsed = int((time.time() - send_time) * 1000)
                    status = response.status_code

                    print(f"[POST {i}] 状态码: {status}, 耗时: {elapsed} ms")

                    if status == 200:
                        print("✅ 成功预约，停止脚本。")
                        break
                    elif status == 500:
                        try:
                            error_message = response.json().get("message") or response.text
                        except Exception:
                            error_message = response.text
                        print(f"❗️ 错误 500，内容: {error_message}")
                except Exception as e:
                    print(f"[POST {i}] 请求异常: {e}")
                time.sleep(0.01)
            break  # 探测成功并完成 POST 发送后退出
        else:
            time.sleep(0.001)
