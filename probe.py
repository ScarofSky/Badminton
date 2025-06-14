import requests
import time


def probe_availability(date: str, venue_from: int, venue_to: int, target_time_range: str) -> bool:
    # ===== 请求设置 =====
    url = "https://ds-api.dong24.com/bais-client-v1/app/venue/sites/14285185605313/stocks"
    params = {
        "siteId": "14285185605313",
        "date": date,
        "itemType": "0",
        "shopId": "3641246707790003",
        "orderType": "0"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # ===== 配置探测参数 =====
    probe_targets = [f"大馆{i}" for i in range(venue_from, venue_to + 1)]

    # ===== 记录开始时间 =====
    t_start = time.time()

    try:
        # ===== 获取数据 =====
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

    # ===== 记录结束时间并计算耗时 =====
    elapsed_ms = int((time.time() - t_start) * 1000)

    # ===== 探测逻辑 =====
    available_slots = []
    for item in data.get("itemList", []):
        if item.get("itemName") in probe_targets:
            for slot in item.get("stockList", []):
                current_range = f"{slot['startTime']} - {slot['endTime']}"
                if current_range == target_time_range and slot.get("isLock") == 0:
                    available_slots.append({
                        "场地": item["itemName"],
                        "时间段": current_range
                    })

    # ===== 打印结果 =====
    print(f"⏱️ 探测耗时: {elapsed_ms} 毫秒")

    if available_slots:
        print(f"🎯 发现可预约的场地（{target_time_range}）：")
        for entry in available_slots:
            print(f"✅ {entry['场地']} - {entry['时间段']}")
        return True
    else:
        print(f"❌ 暂无可预约的【大馆{venue_from}-{venue_to}】场地（{target_time_range}）")
        return False


if __name__ == "__main__":
    result = probe_availability("2025-06-20", 2, 5, "19:00 - 20:00")
    print(result)
