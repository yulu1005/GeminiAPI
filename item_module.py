import json
from datetime import datetime
from utils import safe_generate

ITEMS_FILE = "items.json"

# 記錄物品

def handle_item_input(text):
    prompt = f"""請從下面這句話中擷取出下列資訊，用 JSON 格式回覆：
- item：物品名稱
- location：放置位置
- owner：誰的（如果沒提到就填「我」）
句子：「{text}」"""

    reply = safe_generate(prompt)

    if not reply:
        print("Gemini 沒有回應，請稍後再試。")
        return

    if reply.startswith("```"):
        reply = reply.strip("`").replace("json", "").strip()

    try:
        data = json.loads(reply)
    except:
        print(f"回傳格式錯誤，無法解析：{reply}")
        return

    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except:
        records = []

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records.append(data)
    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"已記錄：{data['owner']}的「{data['item']}」放在 {data['location']}")


# 查詢物品並刪除

def query_item_by_keyword(text):
    keyword = text.replace("在哪", "").replace("在哪裡", "").strip()
    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except:
        print("目前還沒有記錄任何物品喔～")
        return

    for i, r in enumerate(records):
        if keyword in r["item"]:
            print(f"找到了：「{r['item']}」被記在 {r['location']}（紀錄時間：{r['timestamp']}）")
            del records[i]
            with open(ITEMS_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print("查詢完畢，這筆紀錄已刪除。")
            return

    print("找不到這個物品的記錄喔～")


# 使用者主動刪除物品紀錄

def delete_item_by_keyword(text):
    prompt = f"請判斷這句話是否是要求刪除物品，並擷取出物品名稱，只回傳物品名稱，不要加其他解釋：\n「{text}」"
    keyword = safe_generate(prompt)

    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except:
        print("目前沒有物品記錄。")
        return

    for i, r in enumerate(records):
        if keyword in r["item"]:
            del records[i]
            with open(ITEMS_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"已刪除關於「{keyword}」的記錄。")
            return

    print(f"沒有找到關於「{keyword}」的記錄。")
