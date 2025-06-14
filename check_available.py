import os

import requests
import pandas as pd
import json


def load_court_id_map(filepath="court_ids.json"):
    """
    读取场地名称与 itemId 的映射关系，并返回字典。

    参数：
        filepath (str): JSON 文件路径，默认为当前目录下的 court_ids.json

    返回：
        dict: 场地名称 => itemId 的映射字典
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 找不到映射文件: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    return mapping


if __name__ == "__main__":
    # ===== 请求设置 =====
    url = "https://ds-api.dong24.com/bais-client-v1/app/venue/sites/14285185605313/stocks"
    params = {
        "siteId": "14285185605313",
        "date": "2025-06-20",
        "itemType": "0",
        "shopId": "3641246707790003",
        "orderType": "0"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # ===== 获取数据 =====
    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    # ===== 提取并保存 itemId 与 itemName 对应关系 =====
    id_name_map = {item["itemName"]: item["itemId"] for item in data["itemList"]}

    json_path = "court_ids.json"
    if not os.path.exists(json_path):
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(id_name_map, f, ensure_ascii=False, indent=2)
        print("📄 场地 ID 映射已保存为 court_ids.json")
    else:
        print("✅ court_ids.json 已存在，跳过保存。")

    # ===== 过滤掉包含“篮”的场地 =====
    filtered_items = [item for item in data["itemList"] if "篮" not in item["itemName"]]

    # ===== 保留“大馆1~5”和“小馆6~9” =====
    target_courts = [f"大馆{i}" for i in range(1, 6)] + [f"小馆{i}" for i in range(6, 10)]
    filtered_items = [item for item in filtered_items if item["itemName"] in target_courts]

    # ===== 收集所有出现过的时间段 =====
    all_times = sorted({
        f"{slot['startTime']} - {slot['endTime']}"
        for item in filtered_items
        for slot in item["stockList"]
    })

    # ===== 构建表格结构 =====
    table = {"时间段": all_times}
    for court in target_courts:
        table[court] = []

    for time_slot in all_times:
        for court in target_courts:
            court_data = next((item for item in filtered_items if item["itemName"] == court), None)
            if not court_data:
                table[court].append("")
                continue

            slot_data = next(
                (s for s in court_data["stockList"]
                 if f"{s['startTime']} - {s['endTime']}" == time_slot),
                None
            )

            if not slot_data:
                table[court].append("")
            else:
                # 替换为等宽字符
                status = "✅" if slot_data["isLock"] == 0 else "❌"
                table[court].append(status)

    # ===== 输出表格 =====
    df = pd.DataFrame(table)

    # ===== 美观输出格式 =====
    try:
        from tabulate import tabulate

        print(df.to_markdown(index=False, tablefmt="grid"))
    except ImportError:
        print("⚠️ 缺少 tabulate 库，使用 pip install tabulate 安装后可显示更美观表格")
        print(df.to_string(index=False))
