import json
from datetime import datetime, timedelta
from utils import safe_generate

SCHEDULE_FILE = "schedules.json"

def normalize_schedule_data(data):
    """統一資料格式，將中文欄位轉換為英文欄位"""
    mapping = {
        "任務": "task",
        "地點": "location",
        "時間": "time",
        "人物": "person",
        "場所": "place"
    }
    
    normalized = {}
    for key, value in data.items():
        if key in mapping:
            normalized[mapping[key]] = value
        else:
            normalized[key] = value
    return normalized

def parse_relative_time(text):
    """解析相對時間表達"""
    now = datetime.now()
    
    # 定義相對時間的映射
    time_mapping = {
        "今天": 0,
        "明天": 1,
        "後天": 2,
        "大後天": 3,
        "昨天": -1,
        "前天": -2,
        "上禮拜": -7,
        "下禮拜": 7
    }
    
    # 定義時間段的映射
    period_mapping = {
        "早上": "08:00",
        "中午": "12:00",
        "下午": "14:00",
        "晚上": "18:00",
        "凌晨": "00:00"
    }
    
    # 檢查是否包含具體時間（例如：5月10日、5/10、5-10）
    import re
    date_patterns = [
        r'(\d{1,2})月(\d{1,2})日',  # 5月10日
        r'(\d{1,2})/(\d{1,2})',     # 5/10
        r'(\d{1,2})-(\d{1,2})'      # 5-10
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            month, day = map(int, match.groups())
            year = now.year
            # 如果月份小於當前月份，可能是明年
            if month < now.month:
                year += 1
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            # 檢查是否包含時間段
            for period, time in period_mapping.items():
                if period in text:
                    return f"{date_str} {time}"
            
            # 檢查是否包含具體時間（例如：下午3點、15:00）
            time_patterns = [
                r'(\d{1,2})點',           # 3點
                r'(\d{1,2}):(\d{2})',     # 15:00
                r'(\d{1,2})點(\d{1,2})分'  # 3點30分
            ]
            
            for time_pattern in time_patterns:
                time_match = re.search(time_pattern, text)
                if time_match:
                    if ':' in time_pattern:
                        hour, minute = map(int, time_match.groups())
                    else:
                        hour = int(time_match.group(1))
                        minute = 0
                    
                    # 處理上午/下午
                    if '下午' in text and hour < 12:
                        hour += 12
                    elif '晚上' in text and hour < 12:
                        hour += 12
                    
                    return f"{date_str} {hour:02d}:{minute:02d}"
            
            # 如果沒有指定時間，使用當前時間
            return f"{date_str} {now.strftime('%H:%M')}"
    
    # 檢查是否包含相對時間詞
    for key, days in time_mapping.items():
        if key in text:
            target_date = now + timedelta(days=days)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # 檢查是否包含時間段
            for period, time in period_mapping.items():
                if period in text:
                    return f"{date_str} {time}"
            
            # 如果沒有指定時間段，使用當前時間
            return f"{date_str} {now.strftime('%H:%M')}"
    
    return None

# 安排時程（擷取並記錄）
def handle_schedule_input(text):
    # 先解析相對時間
    relative_time = parse_relative_time(text)
    
    prompt = f"""
請從下列句子中擷取資訊並以 JSON 格式回覆，欄位名稱請使用英文（task, location, place, time, person）：

- task：任務（例如 去吃飯）
- location：具體地點（例如 台北車站）
- place：地點分類（例如 餐廳）
- time：請使用 24 小時制 YYYY-MM-DD HH:mm 格式
- person：誰的行程（沒提到就填「我」）

如果句子中包含相對時間（如：明天、後天、大後天等），請使用以下時間：
{relative_time if relative_time else "請根據句子中的時間描述來設定"}

請只回傳 JSON，不要加說明或換行。
句子：「{text}」
"""
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
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedules = json.load(f)
    except:
        schedules = []

    # 統一資料格式
    data = normalize_schedule_data(data)
    
    # 如果解析出相對時間，優先使用它
    if relative_time:
        data["time"] = relative_time
        
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schedules.append(data)
    
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)

    print(f"已安排：{data.get('person', '我')} 在 {data.get('time', '未指定時間')} 要「{data.get('task', '未知任務')}」@{data.get('location', '未知地點')}（{data.get('place', '')}）")

# 查詢時程（今日 or 關鍵字）
def query_schedule(keyword=None, today_only=False):
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except:
        print("查無時程資料。")
        return

    # 統一所有記錄的格式
    records = [normalize_schedule_data(r) for r in records]
    
    results = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for r in records:
        if today_only:
            try:
                schedule_date = datetime.strptime(r["time"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
                if schedule_date != today:
                    continue
            except (ValueError, KeyError):
                continue
                
        if keyword:
            if not any(keyword in str(r.get(field, "")) for field in ["task", "location", "place"]):
                continue
                
        results.append(r)

    if results:
        print(f"查到 {len(results)} 筆時程安排：")
        for r in results:
            print(f" - [{r['timestamp']}] {r.get('person', '我')} 在 {r.get('time', '未指定時間')} 要「{r.get('task', '未知任務')}」@{r.get('location', '未知地點')}（{r.get('place', '')}）")
    else:
        print("沒有找到符合條件的時程。")


# 使用者主動刪除時程（透過語意判斷擷取關鍵字）
def delete_schedule_by_keyword(text):
    prompt = f"請判斷這句話是否是要刪除時程，並擷取關鍵任務（如 拿藥、去市場），只回傳任務名稱，不加其他說明：\n「{text}」"
    keyword = safe_generate(prompt)
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except:
        print("找不到時程資料。")
        return

    # 統一所有記錄的格式
    records = [normalize_schedule_data(r) for r in records]
    
    for i, r in enumerate(records):
        if keyword in r.get("task", ""):
            del records[i]
            with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"🗑️ 已刪除「{keyword}」的時程提醒。")
            return

    print(f"沒有找到關於「{keyword}」的時程可刪除。")